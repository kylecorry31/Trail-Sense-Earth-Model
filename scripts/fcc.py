import requests
import os
import zipfile
from scripts.progress import progress
import csv

source_folder = 'source/fcc'

# https://data.fcc.gov/download/pub/uls/complete/r_tower.zip

def download(redownload=False):
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
    
    if not redownload and os.path.exists(f'{source_folder}/CO.dat'):
        return

    with progress("Downloading FCC antenna data", 1) as pbar:
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

def get_tower_locations():
    """The (latitude, longitude) in degrees of each tower with a position."""
    # Get the line count
    with open(f'{source_folder}/CO.dat', 'r') as file:
        line_count = sum(1 for _ in file)

    locations = []
    with progress("Reading FCC antenna data", line_count) as pbar:
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

                locations.append((lat, lon))
                pbar.update(1)
    return locations