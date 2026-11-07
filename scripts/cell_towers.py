import csv
import datetime
from array import array

import numpy as np

from scripts.progress import progress
from .geo_points import GeoPointFormat

FILENAME = "cell_towers.tsgeo"
# The type tells the app how to use the file, so a change in what the points mean needs a new type
FILE_FORMAT = GeoPointFormat(cell_degrees=5, decimals=2, properties={"type": "cell_towers"})
# Towers within the same square of this size (degrees) are merged into one point, at the square's center
MERGE_DEGREES = 0.01

# Areas are below this, so a network, country, and area fit in one integer
AREA_LIMIT = 2 ** 32
# Towers with a coverage range (meters) above this have too uncertain a position to keep
MAX_RANGE_METERS = 20_000


class TowerRecords:
    """
    The rows of the datasets that pass the filters, kept in arrays rather than objects, since the MLS export has too
    many rows for an object per row to fit in memory.
    """

    def __init__(self):
        self.keys = array("q")
        self.latitudes = array("d")
        self.longitudes = array("d")
        self.unchangeable = array("b")
        self.samples = array("i")

    def __len__(self):
        return len(self.keys)


def get_all_towers(csv_path, name, records=None):
    """
    Adds the towers of a dataset to the records (which can come from an earlier dataset). Only towers updated in the
    past 5 years are taken (to avoid outdated towers).
    """
    if records is None:
        records = TowerRecords()
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
                unchangeable = row['changeable'] == '0'
                # Exclude towers without enough samples, these are likely not accurate
                if samples < 3 and not unchangeable:
                    pbar.update(1)
                    continue
                if int(row['range']) > MAX_RANGE_METERS:
                    pbar.update(1)
                    continue
                area = int(row['area'])
                if area >= AREA_LIMIT:
                    raise ValueError(f"The area {area} is too large to key")
                key = ((int(row['net']) * 1000 + int(row['mcc'])) * AREA_LIMIT) + area
                records.keys.append(key)
                records.latitudes.append(float(row['lat']))
                records.longitudes.append(float(row['lon']))
                records.unchangeable.append(unchangeable)
                records.samples.append(samples)
                pbar.update(1)
    return records


def select_towers(records):
    """
    The latitudes and longitudes of the towers, with one tower per network, country, and area: the first unchangeable
    row, or else the row with the most samples (the earliest of those). The towers are in the order they first appear.
    """
    keys = np.frombuffer(records.keys, dtype=np.int64)
    latitudes = np.frombuffer(records.latitudes, dtype=np.float64)
    longitudes = np.frombuffer(records.longitudes, dtype=np.float64)
    unchangeable = np.frombuffer(records.unchangeable, dtype=np.int8).astype(bool)
    samples = np.frombuffer(records.samples, dtype=np.int32)

    rows = np.arange(len(keys))
    # Sorted by key, then unchangeable first, then the most samples (unchangeable rows are ordered by row alone)
    most_samples = np.where(unchangeable, 0, -samples.astype(np.int64))
    order = np.lexsort((rows, most_samples, ~unchangeable, keys))
    sorted_keys = keys[order]
    is_first = np.r_[True, sorted_keys[1:] != sorted_keys[:-1]]
    winners = order[is_first]

    # Each key's first row, which gives the order the towers first appear in
    _, first_rows = np.unique(keys, return_index=True)
    winners = winners[np.argsort(first_rows)]
    return latitudes[winners], longitudes[winners]


def create_tower_points(latitudes, longitudes):
    """The geo point file of the towers, with towers in the same merge square stored once."""
    positions = np.unique(
        np.column_stack([
            np.round(np.asarray(latitudes) / MERGE_DEGREES) * MERGE_DEGREES,
            np.round(np.asarray(longitudes) / MERGE_DEGREES) * MERGE_DEGREES,
        ]).round(FILE_FORMAT.decimals),
        axis=0,
    )
    return FILE_FORMAT.pack(positions[:, 0], positions[:, 1])
