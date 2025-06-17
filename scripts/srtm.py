import xarray as xr
import numpy as np
from . import to_tif, progress
import os

resolution_arc_seconds = 15 # arc seconds per pixel

def download(redownload=False):
    # TODO: Download https://pae-paha.pacioos.hawaii.edu/thredds/ncss/srtm30plus_v11_land?var=elev&north=89.9958&west=-179.9958&east=179.9958&south=-89.9958&disableLLSubset=on&disableProjSubset=on&horizStride=1  (https://data.noaa.gov/onestop/collections/details/96d77f2d-1ec2-4967-baa0-89626dc803bf)
    pass

def get_file_paths():
    regions = []
    for lat in range(-75, 91, 15):
        for lon in range(-180, 180, 15):
            regions.append([lat, lon])
    
    files = []
    for region in regions:
        files.append(f'images/srtm/{"N" if region[0] >= 0 else "S"}{str(abs(region[0])).zfill(2)}{"E" if region[1] >= 0 else "W"}{str(abs(region[1])).zfill(3)}.tif')
    
    return files

def process():
    # Open the netcdf file
    dataset = xr.open_dataset("source/srtm/srtm30plus_v11_land.nc")

    if not os.path.exists('images/srtm'):
        os.makedirs('images/srtm')

    with progress.progress('Generating DEM', (180 // 15) * (360 // 15)) as pbar:
        for latitude in range(-90, 90, 15):
            for longitude in range(-180, 180, 15):
                start_latitude = latitude + 15
                end_latitude = latitude
                # Extract the region using xarray slicing for efficiency
                lat_slice = slice(end_latitude, start_latitude)
                lon_slice = slice(longitude, longitude + 15)
                
                # Use xarray's built-in interpolation/resampling
                region_data = dataset.elev.sel(lat=lat_slice, lon=lon_slice)
                
                # Resample to the desired resolution if needed
                step = (resolution_arc_seconds / 60) / 60
                new_lat = np.arange(end_latitude, start_latitude, step)
                new_lon = np.arange(longitude, longitude + 15, step)
                
                image = region_data.interp(lat=new_lat, lon=new_lon).values
                to_tif(image, f'images/srtm/{"N" if start_latitude >= 0 else "S"}{str(abs(start_latitude)).zfill(2)}{"E" if longitude >= 0 else "W"}{str(abs(longitude)).zfill(3)}.tif', is_inverted=True)
                pbar.update(1)