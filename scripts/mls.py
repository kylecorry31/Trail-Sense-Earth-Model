import requests
import os
import gzip
from scripts.progress import progress
import csv
from .operators.basic import Save
import numpy as np
from scripts.operators import process
import shutil

source_folder = 'source/mls'
images_folder = 'images/mls'

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

def __get_all_towers():
    """Get all towers, deduplicated with either the changeable=0 row or the row with the highest samples taken"""
    # Get the line count
    with open(f'{source_folder}/MLS-full-cell-export-final.csv', 'r') as file:
        line_count = sum(1 for _ in file)

    towers = {}
    with progress("Reading MLS data", line_count) as pbar:
        with open(f'{source_folder}/MLS-full-cell-export-final.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                samples = int(row['samples'])
                mnc = row['net']
                mcc = row['mcc']
                lac = row['area']
                id = mnc + '/' + mcc + '/' + lac
                if id in towers:
                    existing = towers[id]
                    if existing['changeable'] == '0':
                        pbar.update(1)
                        continue
                    # TODO: Potentially average out the location
                    if row['changeable'] == '0' or samples > int(existing['samples']):
                        towers[id] = row
                else:
                    towers[id] = row
                pbar.update(1)
    return towers.values()

def process_towers(resolution = 0.05):
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    pixels_per_degree = 1 / resolution

    image = np.zeros((int(180 * pixels_per_degree), int(360 * pixels_per_degree)), dtype=np.uint8)

    towers = __get_all_towers()

    with progress("Processing MLS data", len(towers)) as pbar:
        for row in towers:
            lat = float(row['lat'])
            lon = float(row['lon'])
            rounded_lat = round(lat * pixels_per_degree) / pixels_per_degree
            rounded_lon = round(lon * pixels_per_degree) / pixels_per_degree
            image[int((90 - rounded_lat) * pixels_per_degree), int((rounded_lon + 180) * pixels_per_degree)] = 127
            pbar.update(1)

    process([image], Save([f'{images_folder}/cell_towers.tif']))
