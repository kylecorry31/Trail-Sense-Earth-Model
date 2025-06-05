import netCDF4
import os
from scripts import progress
import shutil
import requests
from .operators import process
from .operators.basic import FlipY, ReplaceInvalid, Reshape, ShiftX, Normalize, ReplaceLargeValues, Save, SplitProcessing
from .operators.compression import Index
from .operators.masking import RemoveOceans

# Load the data
source_directory = 'source/eot20'
output_directory = 'images/eot20'

# This needs to be less than 255
final_width = 250
invalid_value = 100000

shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"

def download():
    os.makedirs(source_directory, exist_ok=True)
    with progress.progress("Downloading EOT20 data", 1) as pbar:
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

def process_ocean_tides(final_shape):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(source_directory, exist_ok=True)

    constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

    with progress.progress(f'Processing ocean tides', len(constituents)) as pbar:
        amplitudes = {}
        large_amplitudes = []
        indices_images_created = False
        condenser = None
        for constituent in constituents:
            file_path = f'{source_directory}/ocean_tides/{constituent}_ocean_eot20.nc'
            with netCDF4.Dataset(file_path, 'r') as file:
                # AMPLITUDE
                _, amplitude_results = process(
                    [file.variables['amplitude'][:]],
                    ReplaceInvalid(invalid_value),
                    ShiftX(0.5, True),
                    FlipY(),
                    RemoveOceans(dilation=5, replacement=invalid_value),
                    Reshape(final_shape),
                    ReplaceLargeValues(500, invalid_value=invalid_value),
                    SplitProcessing(Normalize(0.0, invalid_value=invalid_value)),
                    Index(condenser, final_width, invalid_value),
                    Save([f'{output_directory}/{constituent}-amplitude.tif'])
                )

                replace_large_values_idx = 5
                normalize_index = 6
                index_index = 7

                # Extract results
                for value in amplitude_results[replace_large_values_idx]['large_values'][0]:
                    large_amplitudes.append((constituent, value[0], value[1], int(value[2])))

                amplitudes[constituent] = float(amplitude_results[normalize_index]['data'][0][0]['maximum'])           
                
                if condenser is None:
                    condenser = amplitude_results[index_index]['condenser']
                
                if not indices_images_created:
                    process([amplitude_results[index_index]['indices_x']], Save([f'{output_directory}/indices-x.tif']))
                    process([amplitude_results[index_index]['indices_y']], Save([f'{output_directory}/indices-y.tif']))
                    indices_images_created = True

                # PHASE
                process(
                    [file.variables['phase'][:]],
                    Normalize(-180.0, 180.0, invalid_value),
                    ReplaceInvalid(invalid_value),
                    ShiftX(0.5, True),
                    FlipY(),
                    RemoveOceans(dilation=5, replacement=invalid_value),
                    Reshape(final_shape),
                    Index(condenser, final_width, invalid_value),
                    Save([f'{output_directory}/{constituent}-phase.tif'])
                )

                pbar.update(1)

    return amplitudes, large_amplitudes
    

