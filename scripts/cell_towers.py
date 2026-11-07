import csv
from collections import namedtuple
from scripts.progress import progress
import numpy as np
import datetime
from .geo_points import GeoPointFormat

# Only what is needed is kept per tower, since the full rows of the MLS export do not fit in memory
Tower = namedtuple("Tower", ["latitude", "longitude", "changeable", "samples"])

FILENAME = "cell_towers.tsgeo"
# The type tells the app how to use the file, so a change in what the points mean needs a new type
FILE_FORMAT = GeoPointFormat(cell_degrees=5, decimals=2, properties={"type": "cell_towers"})
# Towers within the same 0.01 degree (about 1 km) square are merged into one point
MERGE_DECIMALS = 2

def create_tower_points(latitudes, longitudes):
    """The geo point file of the towers, with towers in the same merge square stored once."""
    positions = np.unique(
        np.column_stack([np.round(latitudes, MERGE_DECIMALS), np.round(longitudes, MERGE_DECIMALS)]),
        axis=0,
    )
    return FILE_FORMAT.pack(positions[:, 0], positions[:, 1])

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
                tower = Tower(float(row['lat']), float(row['lon']), row['changeable'], samples)
                if id in towers:
                    existing = towers[id]
                    if existing.changeable == '0':
                        pbar.update(1)
                        continue
                    # TODO: Potentially average out the location
                    if tower.changeable == '0' or samples > existing.samples:
                        towers[id] = tower
                else:
                    towers[id] = tower
                pbar.update(1)
    return towers