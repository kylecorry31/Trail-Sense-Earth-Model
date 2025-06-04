import netCDF4
import os
from scripts import progress, to_tif, natural_earth
import numpy as np
import shutil
import rasterio
import requests
from PIL import Image

# Load the data
source_directory = 'source/eot20'
output_directory = 'images/eot20'

# This needs to be less than 255
final_width = 250

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
    
def __create_condensed_image(image, valid_indices, final_width=250):
    updated = image[valid_indices]
    total_values = len(updated)
    updated = np.append(updated, np.zeros(final_width - (total_values % final_width)))
    updated = updated.reshape((-1, final_width))
    return updated

def __create_index_image(image, ignored_value, final_width):
    non_zero_bool_array = image != ignored_value
    indices_x = np.zeros(image.shape)
    indices_y = np.zeros(image.shape)
    non_zero_indices = np.argwhere(non_zero_bool_array)
    for i in range(len(non_zero_indices)):
        source_x = non_zero_indices[i][1]
        source_y = non_zero_indices[i][0]
        destination_x = i % final_width + 1
        destination_y = i // final_width + 1
        indices_x[source_y, source_x] = destination_x
        indices_y[source_y, source_x] = destination_y
    return indices_x, indices_y, lambda i: __create_condensed_image(i, non_zero_bool_array, final_width), non_zero_bool_array

def __reshape(image, shape):
    if shape is not None:
        img = Image.fromarray(image).resize(shape, Image.NEAREST)
        return np.array(img).reshape((shape[1], shape[0]))
    return image

def __normalize(image, minimum, maximum, ignored_value = None):
    if minimum is None:
        minimum = np.min(image[image != ignored_value]) if ignored_value is not None else np.min(image)
    if maximum is None:
        maximum = np.max(image[image != ignored_value]) if ignored_value is not None else np.max(image)

    if ignored_value is None:
        return (image - minimum) / (maximum - minimum), minimum, maximum
    normalized = (image[image != 100000] - minimum) / (maximum - minimum)
    normalized[normalized < 0] = 0
    result = image.copy()
    result[result != 100000] = normalized
    return result, minimum, maximum

def __extract_large_values(image, threshold, replacement = 0, ignored_value = None):
    large_values = []
    result = image.copy()
    large_amplitude_indices = np.argwhere((image > threshold) & (image != ignored_value))
    for idx in large_amplitude_indices:
        large_values.append((int(idx[0]), int(idx[1]), image[idx[0], idx[1]]))
        if replacement is not None:
            result[idx[0], idx[1]] = replacement
    return result, large_values

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
                amplitude = to_tif(amplitude, f'{output_directory}/{constituent}-amplitude.tif', True, amplitude.shape[1] // 2, 100000)
                amplitude = natural_earth.remove_oceans(amplitude, dilation=5, replacement=100000, scale=4)
                amplitude = __reshape(amplitude, final_shape)

                # Remove large amplitudes to avoid compression loss before normalizing
                amplitude, large_values = __extract_large_values(amplitude, 500, ignored_value = 100000)
                for value in large_values:
                    large_amplitudes.append((constituent, value[0], value[1], int(value[2])))
                
                # Normalize amplitudes
                amplitude, _, max_amplitude = __normalize(amplitude, 0.0, None, 100000)
                amplitudes[constituent] = float(max_amplitude)           

                # PHASE
                phase = file.variables['phase'][:]
                phase, _, _ = __normalize(phase, -180.0, 180.0)
                phase = to_tif(phase, f'{output_directory}/{constituent}-phase.tif', True, phase.shape[1] // 2, 100000)
                phase = natural_earth.remove_oceans(phase, dilation=5, replacement=100000, scale=4)
                phase = __reshape(phase, final_shape)

                # Create the indices images
                if not indices_images_created:
                    indices_x, indices_y, condenser, _ = __create_index_image(amplitude, 100000, final_width)
                    to_tif(indices_x, f'{output_directory}/indices-x.tif')
                    to_tif(indices_y, f'{output_directory}/indices-y.tif')

                # Create condensed images
                to_tif(condenser(amplitude), f'{output_directory}/{constituent}-amplitude.tif')                
                to_tif(condenser(phase), f'{output_directory}/{constituent}-phase.tif')
                pbar.update(1)

    return amplitudes, large_amplitudes
    

