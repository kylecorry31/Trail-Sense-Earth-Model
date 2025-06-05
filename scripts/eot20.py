import netCDF4
import os
from scripts import progress, to_tif, natural_earth, compression, reshape
import shutil
import requests

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
                amplitude = file.variables['amplitude'][:]
                amplitude = to_tif(amplitude, is_inverted=True, x_shift=amplitude.shape[1] // 2, masked_value_replacement=invalid_value)
                amplitude = natural_earth.remove_oceans(amplitude, dilation=5, replacement=invalid_value, scale=4)
                amplitude = reshape(amplitude, final_shape)

                # Remove large amplitudes to avoid compression loss before normalizing
                amplitude, large_values = compression.extract_large_values(amplitude, 500, ignored_value = invalid_value)
                for value in large_values:
                    large_amplitudes.append((constituent, value[0], value[1], int(value[2])))
                
                # Normalize amplitudes
                amplitude, _, max_amplitude = compression.normalize(amplitude, 0.0, None, invalid_value)
                amplitudes[constituent] = float(max_amplitude)           

                # PHASE
                phase = file.variables['phase'][:]
                phase, _, _ = compression.normalize(phase, -180.0, 180.0)
                phase = to_tif(phase, is_inverted=True, x_shift=phase.shape[1] // 2, masked_value_replacement=invalid_value)
                phase = natural_earth.remove_oceans(phase, dilation=5, replacement=invalid_value, scale=4)
                phase = reshape(phase, final_shape)

                # Create the indices images
                if not indices_images_created:
                    indices_x, indices_y, condenser, _ = compression.index(amplitude, invalid_value, final_width)
                    to_tif(indices_x, f'{output_directory}/indices-x.tif')
                    to_tif(indices_y, f'{output_directory}/indices-y.tif')

                # Create condensed images
                to_tif(condenser(amplitude), f'{output_directory}/{constituent}-amplitude.tif')                
                to_tif(condenser(phase), f'{output_directory}/{constituent}-phase.tif')
                pbar.update(1)

    return amplitudes, large_amplitudes
    

