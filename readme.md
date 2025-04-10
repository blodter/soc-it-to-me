# SOC It To Me!
Welcome to SOC It To Me, the premier application for identifying Soil Organic Carbon values and statistics 
from remote sensing data!


## Application Overview
The application is built using the following technologies:
- **REST API**: FastAPI
- **GeoTIFF Raster Processing**: Rasterio
- **Containerization**: Docker/Docker Compose


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

### GET `http://localhost:8000/soc-stock`
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
- If the latitude and/or longitude is not provided, a 422 Unprocessable Entity error will be returned with a message indicating 
  the missing parameter.
- If the latitude and/or longitude is out of range, a 422 Unprocessable Entity error will be returned with a message indicating
  the invalid value.
- If the latitude and longitude are not within the bounds of any loaded GeoTIFF file, a 400 Not Found error will be returned
  with a message indicating the location is not found in any loaded files.
- If the band does not contain data at the given location, a 400 or 404 error will be returned with a message.

### GET `http://localhost:8000/stats`
This endpoint accepts a GET request with no parameters, and returns a JSON object of the aggregates stats from the app's state -
the response should look like:

```json
{
    "min_soc": 38.999664306640625,
    "max_soc": 88.94852447509766,
    "mean_soc": 63.1354866027832
}
```

## Suggested Improvements
### Data Ingestion and Preprocessing
- Use Flyte to orchestrate the data loading and processing.
- During data preprocessing, reproject the data to a common coordinate system (EPSG:4326).
- Mosaic raster datasets together if multiple datasets are available for adjacent areas.
- Convert the processed data into a format compatible with Zarr.
- Register the processed data in a STAC catalog.

### Data processing and querying
- Use a service like Dask to parallelize the data processing and querying.
- Store each datasets bounds along with a spatial index for faster querying.
- Use Dask to perform the stats calculations.
- Allow querying of the data by bounding box, and return the stats for that bounding box (such as min, max, sum, mean, etc.).
- Use PostGIS to store the data in a database, and use SQL queries to perform bounding box queries and stats calculations.
- Add a caching layer (Redis) to store frequently accessed data and stats.

### Frontend
- Use a frontend framework like React or Angular to build a user interface for the application.
- Include a mapping library such as Mapbox to visualize the data on a map.
- Provide tools to select points, polygons, or bounding boxes on the map, and query the data for those areas.
- Provide heatmaps if historical data is available and charts/histograms for the data alongside the map.
- Make an admin management platform to allow a user to perform CRUD operations on the data.

### Reliability and CI/CD
- Use Kubernetes to orchestrate containerized application rather than Docker Compose.
- Implement unit tests for the application using a library like pytest.
- Use e2e testing tools like Cypress or Selenium to test the frontend and backend together.
- Use a CI/CD tool like GitHub Actions to automate the build and deployment process.
- Add more robust logging and error handling.
- Host the application on a cloud provider like AWS or GCP.
