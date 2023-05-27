import requests
import os
from .progress import progress
import zipfile

def __download(url, redownload=False):
    filename = url.split('/')[-1]
    if not os.path.exists(f'source/natural-earth'):
        os.makedirs(f'source/natural-earth')
    if not os.path.exists(f'source/natural-earth/{filename}') or redownload:
        r = requests.get(url)
        if r.status_code == 200:
            with open(f'source/natural-earth/{filename}', 'wb') as f:
                f.write(r.content)
        else:
            raise Exception(f'Error {r.status_code} downloading {url}')

def download(redownload=False):
    files = [
        'https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip',
        'https://naciscdn.org/naturalearth/10m/physical/ne_10m_minor_islands.zip',
    ]
    with progress("Downloading Natural Earth data", len(files)) as pbar:
        for file in files:
            __download(file, redownload)
            pbar.update(1)
    
    # unzip the files
    with progress("Unzipping Natural Earth data", len(files)) as pbar:
        for file in files:
            filename = file.split('/')[-1]
            with zipfile.ZipFile(f'source/natural-earth/{filename}', 'r') as zip_ref:
                zip_ref.extractall(f'source/natural-earth')
            pbar.update(1)