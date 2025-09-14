import requests
import os
import gzip
import shutil
import csv
from scripts.progress import progress
from .operators.basic import Save
import numpy as np
from scripts.operators import process
from .operators.masking import RemoveOceans

api_key_file = 'opencellid-api-key.txt'
source_folder = 'source/opencellid'
images_folder = 'images/opencellid'


def download(redownload=False):
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)

    if not redownload and os.path.exists(f'{source_folder}/cell_towers.csv'):
        return

    if not os.path.exists(api_key_file):
        api_key = input("OpenCellID API key: ")
        with open(api_key_file, 'w') as f:
            f.write(api_key)
    else:
        with open(api_key_file, 'r') as f:
            api_key = f.read().strip()
    with progress("Downloading and unzipping OpenCellID data", 1) as pbar:
        url = f'https://opencellid.org/ocid/downloads?token={
            api_key}&type=full&file=cell_towers.csv.gz'
        r = requests.get(url)
        with open(f'{source_folder}/cell_towers.csv.gz', 'wb') as f:
            f.write(r.content)

        pbar.update(1)

        # Unzip the file
        with gzip.open(f'{source_folder}/cell_towers.csv.gz', 'rb') as f_in:
            with open(f'{source_folder}/cell_towers.csv', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(f'{source_folder}/cell_towers.csv.gz')

        pbar.update(1)


def process_towers(resolution = 0.05):
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    cell_towers = {}

    pixels_per_degree = 1 / resolution

    image = np.zeros((int(180 * pixels_per_degree), int(360 * pixels_per_degree)), dtype=np.uint8)

    # Get the line count
    with open(f'{source_folder}/cell_towers.csv', 'r') as file:
        line_count = sum(1 for _ in file)

    with progress("Processing OpenCellID data", line_count) as pbar:
        with open(f'{source_folder}/cell_towers.csv', 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                lat = float(row['lat'])
                lon = float(row['lon'])
                # samples = int(row['samples'])
                # if samples < 3:
                #     pbar.update(1)
                #     continue
                radios = {
                    'GSM': 127,
                    'UMTS': 127,
                    'LTE': 127,
                    'NR': 127
                }
                raw_radio = row['radio']
                if raw_radio == 'CDMA':
                    raw_radio = 'UMTS'
                radio = radios.get(raw_radio)
                rounded_lat = round(lat * pixels_per_degree) / pixels_per_degree
                rounded_lon = round(lon * pixels_per_degree) / pixels_per_degree

                if radio is None:
                    print(f'Unknown radio type: {row["radio"]}')
                    pbar.update(1)
                    continue

                if (rounded_lat, rounded_lon) not in cell_towers:
                    cell_towers[(rounded_lat, rounded_lon)] = radio
                else:
                    cell_towers[(rounded_lat, rounded_lon)] |= radio
                
                new_radio = cell_towers[(rounded_lat, rounded_lon)]
                image[int((90 - rounded_lat) * pixels_per_degree), int((rounded_lon + 180) * pixels_per_degree)] = new_radio
                pbar.update(1)

    process([image], RemoveOceans(dilation=0, scale=1), Save([f'{images_folder}/cell_towers.tif']))
