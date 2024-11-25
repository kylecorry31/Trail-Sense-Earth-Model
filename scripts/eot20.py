import netCDF4
import os

import rasterio.mask
import rasterio.transform
from scripts import progress, to_tif
import numpy as np
import os
import shutil
import geopandas as gpd
import rasterio
from scipy.ndimage import binary_dilation
from rasterio.features import rasterize
import requests

# from osgeo import gdal

# Load the data
source_directory = 'source/eot20'
output_directory = 'images/eot20'
x_scale = 0.125
y_scale = 0.125

shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"

def download():
    os.makedirs(source_directory, exist_ok=True)
    with progress.progress("Downloading ocean tides", 1) as pbar:
        if not os.path.exists(f'{source_directory}/ocean_tides/2N2_ocean_eot20.nc'):
            url = 'https://www.seanoe.org/data/00683/79489/data/85762.zip'
            r = requests.get(url, allow_redirects=True)
            with open(f'{source_directory}/85762.zip', 'wb') as f:
                f.write(r.content)
            shutil.unpack_archive(f'{source_directory}/85762.zip', f'{source_directory}')
            os.remove(f'{source_directory}/85762.zip')
            os.remove(f'{source_directory}/load_tides.zip')
            shutil.unpack_archive(f'{source_directory}/ocean_tides.zip', f'{source_directory}')
            os.remove(f'{source_directory}/ocean_tides.zip')
            shutil.rmtree(f'{source_directory}/__MACOSX')
        pbar.update(1)
    

def process_ocean_tides():
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(source_directory, exist_ok=True)

    constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

    with progress.progress("Loading land masks", 2) as pbar:
        gdf = gpd.read_file(shapefile_path)
        pbar.update(1)
        gdf_islands = gpd.read_file(island_shapefile_path)
        pbar.update(1)

    # Render the shapefiles to an image of 2881x1441
    with progress.progress("Rendering land masks", 3) as pbar:
        scale = 4
        mask = rasterize(gdf.geometry, out_shape=(1441 * scale, 2881 * scale), transform=rasterio.transform.from_origin(-180, 90, x_scale / scale, y_scale / scale), dtype=np.float32)
        mask[mask > 0] = 255
        pbar.update(1)

        img_islands = rasterize(gdf_islands.geometry, out_shape=(1441 * scale, 2881 * scale), transform=rasterio.transform.from_origin(-180, 90, x_scale / scale, y_scale / scale), dtype=np.float32)
        img_islands[img_islands > 0] = 255
        pbar.update(1)

        mask = np.maximum(mask, img_islands)

        # Dilate the image
        mask = mask > 0
        mask = binary_dilation(mask, iterations=5 * scale)
        mask = mask.astype(np.float32)
        
        # Downsample the image
        mask = mask[::scale, ::scale]

        # to_tif(img, f'{output_directory}/land-and-islands.tif')

        pbar.update(1)

    with progress.progress(f'Processing ocean tides', len(constituents) * 2) as pbar:
        amplitudes = {}
        for constituent in constituents:
            file_path = f'{source_directory}/ocean_tides/{constituent}_ocean_eot20.nc'
            with netCDF4.Dataset(file_path, 'r') as file:
                phase = file.variables['phase'][:]
                amplitude = file.variables['amplitude'][:]

                min_phase = -180.0
                max_phase = 180.0
                phase = (phase - min_phase) / (max_phase - min_phase)
   
                x_shift = amplitude.shape[1] // 2
                
                updated = to_tif(phase, f'{output_directory}/{constituent}-phase.tif', True, x_shift, 100000)
                # Mask the image
                updated = updated * mask
                updated[updated == 0] = 100000
                to_tif(updated, f'{output_directory}/{constituent}-phase.tif')


                pbar.update(1)
                updated = to_tif(amplitude, f'{output_directory}/{constituent}-amplitude.tif', True, x_shift, 100000)
                # Mask the image
                updated = updated * mask
                updated[updated == 0] = 100000
                min_amplitude = 0.0
                max_amplitude = np.max(updated[updated != 100000])
                normalized = (updated[updated != 100000] - min_amplitude) / (max_amplitude - min_amplitude)
                
                # Accentuate the higher values
                curve = np.power(normalized, 0.25)
                updated[updated != 100000] = curve
                amplitudes[constituent] = float(max_amplitude)
                to_tif(updated, f'{output_directory}/{constituent}-amplitude.tif')
                pbar.update(1)
    return amplitudes
    

