import netCDF4
import os
from scripts import progress, to_tif

# Load the data
source_directory = 'source/eot20'
output_directory = 'images/eot20'
x_scale = 0.125
y_scale = 0.125

# TODO: Download the data from https://www.seanoe.org/data/00683/79489/data/85762.zip and unzip it to source/eot20
def download():
    pass

def process_ocean_tides():
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(source_directory, exist_ok=True)

    constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

    with progress.progress(f'Processing ocean tides', len(constituents) * 2) as pbar:
        for constituent in constituents:
            file_path = f'{source_directory}/ocean_tides/{constituent}_ocean_eot20.nc'
            with netCDF4.Dataset(file_path, 'r') as file:
                imaginary = file.variables['imag'][:]
                real = file.variables['real'][:]
                # imaginary = np.deg2rad(file.variables['phase'][:])
                # real = file.variables['amplitude'][:] / 1000
                
                x_shift = real.shape[1] // 2
                
                to_tif(imaginary, f'{output_directory}/{constituent}-imaginary.tif', True, x_shift, 100000)
                pbar.update(1)
                to_tif(real, f'{output_directory}/{constituent}-real.tif', True, x_shift, 100000)
                pbar.update(1)
