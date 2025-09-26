import requests
import os
import gzip
from scripts.progress import progress
import shutil

source_folder = 'source/mls'
images_folder = 'images/mls'
csv_path = f'{source_folder}/MLS-full-cell-export-final.csv'

def download(redownload=False):
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
    
    if not redownload and os.path.exists(f'{source_folder}/MLS-full-cell-export-final.csv'):
        return

    with progress("Downloading MLS cell tower export", 1) as pbar:
        r = requests.get('https://archive.org/download/MLS_Full_Cell_Export_Final/MLS-full-cell-export-final.csv.gz')
        with open(f'{source_folder}/MLS-full-cell-export-final.csv.gz', 'wb') as f:
            f.write(r.content)

        # Unzip the file
        with gzip.open(f'{source_folder}/MLS-full-cell-export-final.csv.gz', 'rb') as f_in:
            with open(f'{source_folder}/MLS-full-cell-export-final.csv', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(f'{source_folder}/MLS-full-cell-export-final.csv.gz')

        pbar.update(1)