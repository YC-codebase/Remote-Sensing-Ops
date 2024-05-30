
from osgeo import gdal
import rasterio
from matplotlib import pyplot as plt
import numpy as np
import pygeoprocessing
from typing import List

# File paths for Landsat 8 datasets
L8_2013_FILES = [
    '../data/landsat/LC08_L1TP_042034_20130605_20170310_01_T1_B4_120x120.TIF',
    '../data/landsat/LC08_L1TP_042034_20130605_20170310_01_T1_B5_120x120.TIF',
    '../data/landsat/LC08_L1TP_042034_20130605_20170310_01_T1_BQA_120x120.TIF'
]

L8_2016_FILES = [
    '../data/landsat/LC08_L1TP_042034_20160629_20170222_01_T1_B4_120x120.TIF',
    '../data/landsat/LC08_L1TP_042034_20160629_20170222_01_T1_B5_120x120.TIF',
    '../data/landsat/LC08_L1TP_042034_20160629_20170222_01_T1_BQA_120x120.TIF'
]

NODATA = -9999
ALIGNED_FILES = [
    'al_red_2013.tif', 'al_nir_2013.tif', 'al_qa_2013.tif',
    'al_red_2016.tif', 'al_nir_2016.tif', 'al_qa_2016.tif'
]

def plot(array: np.ndarray) -> None:
    """Plot a numpy array with an NDVI colormap."""
    plt.imshow(array, cmap='RdYlGn')
    plt.colorbar()
    plt.show()

def calc_ndvi(red: np.ndarray, nir: np.ndarray, qa: np.ndarray) -> np.ndarray:
    """Calculate NDVI from red and near-infrared landsat bands."""
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)
    
    ndvi = (nir - red) / (nir + red)
    ndvi[qa == 1] = NODATA
    return ndvi

def align_and_resize(L8_2013_files: List[str], L8_2016_files: List[str], aligned_files: List[str]) -> None:
    """Align and resize raster stack."""
    pygeoprocessing.align_and_resize_raster_stack(
        L8_2013_files + L8_2016_files,
        aligned_files,
        ['nearest'] * len(aligned_files),
        (120, -120),
        'intersection'
    )

def diff_ndvi(red_2013: np.ndarray, nir_2013: np.ndarray, qa_2013: np.ndarray,
              red_2016: np.ndarray, nir_2016: np.ndarray, qa_2016: np.ndarray) -> np.ndarray:
    """Calculate the difference in NDVI between two years."""
    valid_pixels = (qa_2013 != 1) & (qa_2016 != 1)
    
    def _calc_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """Calculate NDVI from red and near-infrared landsat bands."""
        red = red[valid_pixels].astype(np.float32)
        nir = nir[valid_pixels].astype(np.float32)
    
        ndvi = (nir - red) / (nir + red)
        return ndvi
    
    ndvi_2013 = _calc_ndvi(red_2013, nir_2013)
    ndvi_2016 = _calc_ndvi(red_2016, nir_2016)
    
    output_ndvi = np.empty_like(red_2013, dtype=np.float32)
    output_ndvi[:] = NODATA
    output_ndvi[valid_pixels] = (ndvi_2013 - ndvi_2016)
    
    return output_ndvi

def calculate_ndvi_difference(L8_2013_files: List[str], L8_2016_files: List[str], aligned_files: List[str], output_file: str) -> None:
    """Calculate the difference in NDVI between two years and plot the result."""
    align_and_resize(L8_2013_files, L8_2016_files, aligned_files)
    
    pygeoprocessing.raster_calculator(
        [(filename, 1) for filename in aligned_files],
        diff_ndvi,
        output_file,
        gdal.GDT_Float32,
        NODATA
    )

    # Read and plot the result
    array = gdal.Open(output_file).ReadAsArray()
    plot(np.ma.array(array, mask=array == NODATA))

if __name__ == "__main__":
    calculate_ndvi_difference(L8_2013_FILES, L8_2016_FILES, ALIGNED_FILES, 'diff_ndvi.tif')
