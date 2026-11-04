import netCDF4
import os
from scripts import progress
import shutil
import requests

# Load the data
source_directory = 'source/eot20'


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

def load(constituent):
    """The amplitude (cm) and phase (degrees) grids of a tidal constituent, with invalid cells masked."""
    with netCDF4.Dataset(f'{source_directory}/ocean_tides/{constituent}_ocean_eot20.nc', 'r') as file:
        return [file.variables['amplitude'][:], file.variables['phase'][:]]
