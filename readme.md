# SOC It To Me!
Welcome to SOC It To Me, the premier application for identifying Soil Organic Carbon values and statistics 
from remote sensing data!


## Application Overview
The application is built using the following technologies:
- **REST API**: FastAPI
- **GeoTIFF Raster Processing**: Rasterio
- **Containerization**: Docker/Docker Compose

While there are a lot of components for such a small application, I believed it to be important to showcase my expertise among
these technologies and my ability to stand up a full stack containerized application in a short amount of time.


## Initialization
To get started, all that is needed to run this application is docker and docker-compose.

To initialize the application, be sure no other applications are running on ports 8000,
then navigate to the root directory of the project and simply run `docker-compose up`.
Once the project finishes building, the application will be available for API requests at `http://localhost:8000`.

Upon initialization, the application will load all GeoTIFF files from the `/geodata` directory into the app's state in memory.
The GeoTIFF files are loaded into objects of the `RasterData' class, which processes the data using rasterio and numpy, 
performs some basic stats calculations, and provides a method to check if an x, y coordinate is within the bounds of the raster.

Since multiple GeoTIFF files may be loaded, stats are calculated for each file (and stored in the RasterData class),
then an aggregate calculation is performed on all files up front. To avoid unnecessarily performing calculations multiple times, 
all stats are calculated on app initialization and stored in the app's state.

On app shutdown, all raster data is closed and the app's state is cleared.


## Usage
To use the API, two endpoints are available:
 - `http://localhost:8000/soc-stock`
 - `http://localhost:8000/stats`

### `http://localhost:8000/soc-stock`
This endpoint accepts a GET request with the following parameters:
- `lat`: Latitude of the location (required value between -90 and 90) (required)
- `lon`: Longitude of the location (required value between -180 and 180)

For example `http://localhost:8000/soc-stock?lat=41.959271&lon=-97.92046` should yield the response:
```json
{
	"soc_stock": 60.66596221923828,
	"filename": "nebraska_30m_soc.tif"
}
```

The response will be a JSON object containing the SOC stock value for the given location, and the filename of the GeoTIFF
file containing the SOC stock value (since multiple files may be loaded into the app's state).

Error handling has been implemented for the following cases:
- If the latitude and/or longitude is not provided, a 422 Unprocessable Entity error will be returned with a message indicating the missing parameter.
- If the latitude and/or longitude is out of range, a 422 Unprocessable Entity error will be returned with a message indicating the invalid value.
- If the latitude and longitude are not within the bounds of any loaded GeoTIFF file, a 400 Not Found error will be returned with a message indicating the location is not found in any loaded files.
- If the band does not contain data at the given location, a 400 or 404 error will be returned with a message.

### `http://localhost:8000/stats`
This endpoint accepts a GET request with no parameters, and returns a JSON object of the aggregates stats from the app's state -
the response should look like:

```json
{
    "min_soc": 38.999664306640625,
    "max_soc": 88.94852447509766,
    "mean_soc": 63.1354866027832
}
```
