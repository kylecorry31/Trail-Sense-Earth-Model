import requests
import os
import zipfile
from scripts.progress import progress
import csv
from .operators.basic import Save
import numpy as np
from scripts.operators import process

source_folder = 'source/fcc'
images_folder = 'images/fcc'

# https://data.fcc.gov/download/pub/uls/complete/r_tower.zip

def download(redownload=False):
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
    
    if not redownload and os.path.exists(f'{source_folder}/CO.dat'):
        return

    with progress("Downloading antenna data", 1) as pbar:
        r = requests.get('https://data.fcc.gov/download/pub/uls/complete/r_tower.zip')
        with open(f'{source_folder}/r_towers.zip', 'wb') as f:
            f.write(r.content)

        # Unzip the file
        with zipfile.ZipFile(f'{source_folder}/r_towers.zip', 'r') as zip_ref:
            zip_ref.extractall(source_folder)

        # Remove everything except for CO.dat
        for filename in os.listdir(source_folder):
            if filename != 'CO.dat':
                os.remove(os.path.join(source_folder, filename))

        pbar.update(1)

def process_towers(resolution = 0.05):
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
    
    pixels_per_degree = 1 / resolution

    image = np.zeros((int(180 * pixels_per_degree), int(360 * pixels_per_degree)), dtype=np.uint8)

    # Get the line count
    with open(f'{source_folder}/CO.dat', 'r') as file:
        line_count = sum(1 for _ in file)

    with progress("Processing antenna data", line_count) as pbar:
        with open(f'{source_folder}/CO.dat', 'r') as file:
            reader = csv.reader(file, delimiter='|')

            for row in reader:
                lat_degrees = row[6]
                lat_minutes = row[7]
                lat_seconds = row[8]
                lat_direction = row[9]

                lon_degrees = row[11]
                lon_minutes = row[12]
                lon_seconds = row[13]
                lon_direction = row[14]

                if lat_degrees == '' or lon_degrees == '':
                    pbar.update(1)
                    continue

                lat = float(lat_degrees) + float(lat_minutes) / 60 + float(lat_seconds) / 3600
                if lat_direction == 'S':
                    lat = -lat
                
                lon = float(lon_degrees) + float(lon_minutes) / 60 + float(lon_seconds) / 3600
                if lon_direction == 'W':
                    lon = -lon

                rounded_lat = round(lat * pixels_per_degree) / pixels_per_degree
                rounded_lon = round(lon * pixels_per_degree) / pixels_per_degree
                image[int((90 - rounded_lat) * pixels_per_degree), int((rounded_lon + 180) * pixels_per_degree)] = 127
                pbar.update(1)

    process([image], Save([f'{images_folder}/cell_towers.tif']))