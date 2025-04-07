import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from rasterio.windows import Window

import settings
from data import RasterDataset
from functions import calculate_aggregated_stats, transform_lat_lon

# Configure logging.
logger = logging.getLogger('uvicorn.error')


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    Handles the lifespan of the FastAPI app, specifically loading and unloading the GeoTIFF data on startup and shutdown.
    
    :param app_: The FastAPI app instance.
    """
    logger.info('Loading GeoTIFF data...')
    loaded_raster_data = []
    
    # Load all GeoTIFF files from the settings.GEODATA_DIR.
    for filename in os.listdir(settings.GEODATA_DIR):
        if filename.endswith('.tif'):
            loaded_raster_data.append(RasterDataset(filename))
    # Check if any datasets were loaded.
    if len(loaded_raster_data) == 0:
        raise ValueError('No datasets have been loaded!')
    
    # Store the loaded raster data and aggregated stats in the app state.
    app_.state.raster_data = loaded_raster_data
    app_.state.stats = calculate_aggregated_stats(loaded_raster_data)
    
    # Yield control back to the FastAPI app.
    logger.info('Finished loading GeoTIFF data, yielding control to the FastAPI app...')
    yield
    
    # Close all datasets when the app shuts down.
    logger.info('Shutting down the FastAPI app, closing all datasets...')
    for raster_data in app_.state.raster_data:
        raster_data.dataset.close()
    app_.state.raster_data = None
    app_.state.stats = None
    logger.info('All datasets closed, FastAPI app shutdown complete.')


# Initialize the FastAPI app with the lifespan context manager above.
app = FastAPI(
    title='SOC It To Me',
    description='API to retrieve soil organic carbon (SOC) stock data from GeoTIFF files.',
    version='0.1.0',
    lifespan=lifespan,
)


@app.get('/soc-stock')
def get_soc_stock(
    lat: float = Query(..., ge=-90, le=90, description='Latitude in decimal degrees'),
    lon: float = Query(..., ge=-180, le=180, description='Longitude in decimal degrees'),
) -> dict:
    """
    Get the SOC stock for a given latitude and longitude.
    
    :param lat: Latitude in decimal degrees with bounds [-90, 90].
    :param lon: Longitude in decimal degrees with bounds [-180, 180].
    :return: A dictionary containing the SOC stock value and the filename of the dataset.
    """
    # Check if coordinates are within bounds of any raster dataset.
    bounding_data = None
    x, y = None, None
    for raster_data in app.state.raster_data:
        x, y = transform_lat_lon(lon, lat, raster_data)
        if raster_data.point_in_bounds(x, y):
            bounding_data = raster_data
            break
    
    # If no x or y coordinates are found, or if no bounding data is found, raise an HTTPException.
    if not x or not y:
        raise HTTPException(status_code=400, detail='Coordinates are invalid.')
    if not bounding_data:
        raise HTTPException(status_code=400, detail='Coordinates are out of bounds for all datasets.')
    
    # Transform the lat/lon coordinates to the dataset's CRS, get the row/col indices, and read the data at that location.
    row, col = bounding_data.dataset.index(x, y)
    window = Window(col, row, 1, 1)
    band = bounding_data.dataset.read(1, window=window)
    
    # Check if the band size is zero.
    if band.size == 0:
        raise HTTPException(status_code=400, detail='No data returned for the specified coordinates.')
        
    # Check if the band value is equal to the nodata value.
    if bounding_data.dataset.nodata is not None:
        if band[0, 0] == bounding_data.dataset.nodata:
            raise HTTPException(status_code=404, detail='No data available for the specified coordinates.')
        
    # Return the SOC value
    return {
        'soc_stock': float(band[0, 0]),
        'filename': bounding_data.filename,
    }


@app.get('/stats')
def get_stats():
    """
    Get the statistics from state for all loaded raster datasets.
    
    :return: A dictionary containing the minimum, maximum, and mean SOC values across all datasets.
    """
    return app.state.stats
