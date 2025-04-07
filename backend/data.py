import os

import numpy as np
import rasterio

import settings


class RasterDataset:
    """
    A class to represent a raster dataset.
    
    :param dataset: rasterio dataset object.
    :param filename: The name of the raster file that has been processed.
    :param stats: Dictionary to hold the statistics of the dataset's SOC band.
    """
    dataset: rasterio.DatasetReader
    filename: str
    stats: dict = {
        'min_soc': None,
        'max_soc': None,
        'mean_soc': None
    }
    
    def __init__(self, filename: str):
        """
        Initialize the RasterDataset with a filename.
        
        :param filename: The name of the raster file to be opened and processed.
        """
        # Set the filename.
        self.filename = filename
        
        # Open the dataset
        self.dataset = rasterio.open(os.path.join(settings.GEODATA_DIR, filename))
        
        # Read SOC band.
        soc_band = self.dataset.read(1)
        
        # Check if the dataset has a nodata value and filter out nodata values.
        if self.dataset.nodata is not None:
            mask = soc_band != self.dataset.nodata
            valid_data = soc_band[mask]
        else:
            valid_data = soc_band
        
        # Calculate statistics if valid data is available.
        if valid_data.size > 0:
            self.stats = {
                'min_soc': float(np.nanmin(valid_data)),
                'max_soc': float(np.nanmax(valid_data)),
                'mean_soc': float(np.nanmean(valid_data))
            }
    
    def point_in_bounds(self, x: float, y: float) -> bool:
        """
        Check if the given coordinates are within the bounds of the dataset.
        
        :param x: X position of the point relative to the dataset.
        :param y: Y position of the point relative to the dataset.
        :return: True if the coordinates are within bounds, False otherwise.
        """
        return (
            self.dataset.bounds.left <= x <= self.dataset.bounds.right and
            self.dataset.bounds.bottom <= y <= self.dataset.bounds.top
        )
