"""
This script generates the data for testing the cell tower model, it is not intended to be used for creating one.

It outputs output/cell-tower-tests/points.csv with the position of random towers from the source data (FCC,
OpenCelliD, and MLS, after the same filters the model uses). The model is tested by how far each tower is from the
closest tower in the model, so the tests show the error added by merging the towers into the model.
"""

import csv
import os
import random

from scripts import fcc, mls, opencellid, cell_towers

# INPUT
tower_points = 200

######## Program, don't modify ########
output_directory = "output/cell-tower-tests"
random.seed(42)

os.makedirs(output_directory, exist_ok=True)
fcc.download()
opencellid.download()
mls.download()

locations = fcc.get_tower_locations()
records = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
records = cell_towers.get_all_towers(mls.csv_path, "MLS", records)
latitudes, longitudes = cell_towers.select_towers(records)
locations += list(zip(latitudes.tolist(), longitudes.tolist()))

with open(f"{output_directory}/points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["latitude", "longitude"])
    for latitude, longitude in random.sample(locations, tower_points):
        writer.writerow([round(latitude, 5), round(longitude, 5)])
print(f"Points: {tower_points}")
