"""
This script generates the data for testing the cell tower model, it is not intended to be used for creating one.

It outputs output/cell-tower-tests/points.csv with the exact location of random towers from the same sources as the
model, so the tests show the error added by storing the towers in cells.
"""

import csv
import os
import random

from scripts import opencellid, fcc, mls, cell_towers

# INPUT
count = 100

######## Program, don't modify ########
output_directory = "output/cell-tower-tests"
random.seed(42)

towers = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
towers = cell_towers.get_all_towers(mls.csv_path, "MLS", towers)
locations = cell_towers.get_locations(towers) + fcc.get_towers()
locations = [
    (lat, lon) for lat, lon in locations if abs(lat) <= 90 and abs(lon) <= 180
]

os.makedirs(output_directory, exist_ok=True)
with open(f"{output_directory}/points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["latitude", "longitude"])
    for latitude, longitude in random.sample(locations, count):
        writer.writerow([round(latitude, 6), round(longitude, 6)])
print(f"Points: {count}")
