from rasterio.crs import CRS

# Directory where geospatial data is stored.
GEODATA_DIR = 'geodata'

# Coordinate reference system for Lat/Lon coordinates.
COORDINATE_REFERENCE_SYSTEM = CRS({'init': 'EPSG:4326'})
