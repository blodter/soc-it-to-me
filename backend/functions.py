from typing import List, Tuple

from rasterio.warp import transform

import settings
from data import RasterDataset


def calculate_aggregated_stats(loaded_raster_data: List[RasterDataset]) -> dict:
    """
    Returns aggregate statistics for all raster datasets.
    
    :param loaded_raster_data: List of loaded raster datasets.
    :return: Dictionary containing the minimum, maximum, and mean SOC values across all datasets.
    """
    return {
        # Calculate the minimum SOC value across all loaded raster datasets using Python's built-in min function.
        'min_soc': min(
            [raster_data.stats['min_soc'] for raster_data in loaded_raster_data if raster_data.stats['min_soc'] is not None]
        ),
        # Calculate the maximum SOC value across all loaded raster datasets using Python's built-in max function.
        'max_soc': max(
            [raster_data.stats['max_soc'] for raster_data in loaded_raster_data if raster_data.stats['max_soc'] is not None]
        ),
        # Calculate the mean SOC value across all loaded raster datasets by summing the mean SOC values and dividing by the number of datasets.
        'mean_soc': sum(
            [raster_data.stats['mean_soc'] for raster_data in loaded_raster_data if raster_data.stats['mean_soc'] is not None]
        ) / len(loaded_raster_data)
    }


def transform_lat_lon(lon: float, lat: float, bounding_data: RasterDataset) -> Tuple[float, float]:
    """
    Transform the latitude and longitude coordinates to the dataset's coordinate reference system (CRS).
    
    :param lon: Longitude in decimal degrees.
    :param lat: Latitude in decimal degrees.
    :param bounding_data: The RasterDataset object containing the dataset's CRS.
    :return: Tuple containing the transformed x and y coordinates.
    """
    x, y = transform(settings.COORDINATE_REFERENCE_SYSTEM, bounding_data.dataset.crs, [lon], [lat])
    return x[0], y[0]
