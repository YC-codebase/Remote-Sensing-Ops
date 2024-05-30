
from osgeo import gdal
import rasterio
from matplotlib import pyplot as plt
import numpy as np
from typing import Any

# File paths for Landsat 8 datasets
L8_RED = '../data/landsat/LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF'
L8_NIR = '../data/landsat/LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.TIF'
L8_QA = '../data/landsat/LC08_L1TP_042034_20130605_20170310_01_T1_BQA_120x120.TIF'

def plot(array: np.ndarray) -> None:
    """Plot a numpy array with an NDVI colormap."""
    plt.imshow(array, cmap='RdYlGn')
    plt.colorbar()
    plt.show()

def read_band(file_path: str) -> np.ndarray:
    """Read a single band from a file."""
    dataset = gdal.Open(file_path)
    return dataset.ReadAsArray()

def ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Calculate NDVI from red and near-infrared bands."""
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)
    return (nir - red) / (nir + red)

def save_ndvi_as_tif(ndvi_array: np.ndarray, reference_file: str, output_file: str) -> None:
    """Save NDVI array as a GeoTIFF file."""
    dataset = gdal.Open(reference_file)
    driver = gdal.GetDriverByName('GTiff')
    new_dataset = driver.Create(
        output_file,
        dataset.RasterXSize,
        dataset.RasterYSize,
        1,
        gdal.GDT_Float32
    )
    new_dataset.SetProjection(dataset.GetProjection())
    new_dataset.SetGeoTransform(dataset.GetGeoTransform())

    band = new_dataset.GetRasterBand(1)
    band.WriteArray(ndvi_array)
    band.SetNoDataValue(-9999)
    band = None
    new_dataset = None

def calculate_and_save_ndvi(red_file: str, nir_file: str, output_file: str) -> None:
    """Calculate NDVI from given red and NIR files, and save the result as a GeoTIFF."""
    red = read_band(red_file)
    nir = read_band(nir_file)
    
    calculated_ndvi = ndvi(red, nir)
    
    plot(calculated_ndvi)
    
    save_ndvi_as_tif(calculated_ndvi, red_file, output_file)

if __name__ == "__main__":
    calculate_and_save_ndvi(L8_RED, L8_NIR, 'ndvi.tif')
