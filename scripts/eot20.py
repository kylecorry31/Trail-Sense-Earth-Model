import netCDF4
import numpy as np
import math
from PIL import Image
import os
from scripts import progress

# Load the data
source_directory = 'source/eot20'
output_directory = 'images/eot20'
x_scale = 0.125
y_scale = 0.125

# TODO: Download the data from https://www.seanoe.org/data/00683/79489/data/85762.zip and unzip it to source/eot20
def download():
    pass

def process_ocean_tides(reprocess = False):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(source_directory, exist_ok=True)

    constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

    # Don't process if the files already exist
    if not reprocess:
        is_missing = False
        for constituent in constituents:
            if not os.path.exists(f'{output_directory}/{constituent}-real.tif') or not os.path.exists(f'{output_directory}/{constituent}-imaginary.tif'):
                is_missing = True
                break
        if not is_missing:
            return

    with progress.progress(f'Processing ocean tides', len(constituents)) as pbar:
        for constituent in constituents:
            file_path = f'{source_directory}/ocean_tides/{constituent}_ocean_eot20.nc'
            with netCDF4.Dataset(file_path, 'r') as file:
                imaginary = file.variables['imag'][:]
                real = file.variables['real'][:]
                
                def get_value(latitude, longitude):
                    latitude_index = int((latitude + 90) / y_scale)
                    longitude_index = int((longitude + 180) / x_scale)
                    return (real[latitude_index, longitude_index], imaginary[latitude_index, longitude_index])
                
                real_image = Image.new("F", (int(360 / x_scale), int(180 / y_scale)))
                imaginary_image = Image.new("F", (int(360 / x_scale), int(180 / y_scale)))
                for i in range(real_image.height):
                    for j in range(real_image.width):
                        value = get_value(i * y_scale - 90, j * x_scale - 180)
                        if np.ma.is_masked(value[0]) or math.isnan(value[0]):
                            real_image.putpixel((j, real_image.height - i - 1), 100000)
                        else:
                            real_image.putpixel((j, real_image.height - i - 1), value[0])

                        if np.ma.is_masked(value[1]) or math.isnan(value[1]):
                            imaginary_image.putpixel((j, imaginary_image.height - i - 1), 100000)
                        else:
                            imaginary_image.putpixel((j, imaginary_image.height - i - 1), value[1])
                real_image.save(f'{output_directory}/{constituent}-real.tif')
                imaginary_image.save(f'{output_directory}/{constituent}-imaginary.tif')
                pbar.update(1)
