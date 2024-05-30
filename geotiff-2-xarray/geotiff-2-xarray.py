import glob
import os
import pandas as pd
import xarray as xr
from typing import List
import matplotlib.pyplot as plt

def geotiff_to_netcdf(directory: str, output_netcdf: str, output_csv: str) -> None:
    """
    Converts a collection of GeoTIFF files in a directory to a NetCDF file, and exports a time series to CSV.

    Args:
    - directory (str): Directory containing the GeoTIFF files.
    - output_netcdf (str): Path to the output NetCDF file.
    - output_csv (str): Path to the output CSV file for the time series.
    """
    def read_file_time(flist: List[str]) -> pd.DatetimeIndex:
        """
        Create a pandas DatetimeIndex for raster files based on the filename.

        Args:
        - flist (List[str]): List of filenames.

        Returns:
        - pd.DatetimeIndex: DatetimeIndex object.
        """
        datetime_collect = []
        for eachfile in flist:
            obj = os.path.basename(eachfile).split('_')[1]
            datetime_collect.append(pd.datetime.strptime(obj, '%Y%m').strftime('%Y-%m-%d'))
        return pd.DatetimeIndex(datetime_collect)

    # Change to the specified directory
    os.chdir(directory)

    # Load all GeoTIFF files
    filenames = glob.glob('*.tif')

    # Create time dimension for xarray dataset
    time = xr.Variable('time', read_file_time(filenames))

    # Define x, y dimension in xarray dataset
    chunks = {'x': 5490, 'y': 5490, 'band': 1}

    # Concat data arrays along time dimension
    da = xr.concat([xr.open_rasterio(f, chunks=chunks) for f in filenames], dim=time)

    # Export xarray dataset to NetCDF format
    da.to_netcdf(output_netcdf)

    # Select a certain spatial subset to pandas dataframe
    t_series = da.isel(x=200, y=200).to_pandas()

    # Export pandas dataframe to CSV format
    t_series.to_csv(output_csv)

    # Plot the time series
    t_series.plot()
    plt.show()

# Example usage
directory = '../data'
output_netcdf = 'AET_ok.nc'
output_csv = 'AET_ok.csv'
geotiff_to_netcdf(directory, output_netcdf, output_csv)
