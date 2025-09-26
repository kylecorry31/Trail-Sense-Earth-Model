import csv
from scripts.progress import progress
import os
from scripts.operators import process
import numpy as np
from scripts.operators.basic import Save
import datetime

def get_all_towers(csv_path, name, towers={}):
    """Get all towers, deduplicated with either the changeable=0 row or the row with the highest samples taken. Only towers updated in the past 5 years are taken (to avoid outdated towers)"""
    now = datetime.datetime.now()

    # Get the line count
    with open(csv_path, 'r') as file:
        line_count = sum(1 for _ in file)

    with progress(f"Reading {name} data", line_count) as pbar:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                updated = row.get('updated', None)
                # Parse the unix timestamp (ex. 1657960739)
                if updated is not None and updated != '':
                    updated_date = datetime.datetime.fromtimestamp(int(updated))
                    if (now - updated_date).days > 5 * 365:
                        pbar.update(1)
                        continue
                samples = int(row['samples'])
                # Exclude towers without enough samples, these are likely not accurate
                if samples < 3 and row['changeable'] != '0':
                    pbar.update(1)
                    continue
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
    return towers

def create_tower_image(towers, resolution, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pixels_per_degree = 1 / resolution

    image = np.zeros((int(180 * pixels_per_degree), int(360 * pixels_per_degree)), dtype=np.uint8)

    towers = towers.values()

    with progress("Processing cell tower data", len(towers)) as pbar:
        for row in towers:
            lat = float(row['lat'])
            lon = float(row['lon'])
            rounded_lat = round(lat * pixels_per_degree) / pixels_per_degree
            rounded_lon = round(lon * pixels_per_degree) / pixels_per_degree
            image[int((90 - rounded_lat) * pixels_per_degree), int((rounded_lon + 180) * pixels_per_degree)] = 127
            pbar.update(1)

    process([image], Save([f'{output_folder}/cell_towers.tif']))