import csv
from scripts.progress import progress
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

def get_locations(towers):
    """The (latitude, longitude) of each tower from get_all_towers"""
    return [(float(row['lat']), float(row['lon'])) for row in towers.values()]
