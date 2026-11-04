"""
This script generates the data for testing the temperature model, it is not intended to be used for creating one.

It outputs output/temperature-tests/points.csv with the average daily high and low (°C, at sea level) of each month
at the same points as the precipitation tests (so generate-precipitation-test-data.py must be run first). The
reference is the bilinear interpolation of the full precision MERRA-2 climate normals (generate-temperature-model.py
creates them), which is how the model is read, so the tests show the error added by shrinking the model.
"""

import csv
import os

import numpy as np
from scipy.ndimage import map_coordinates

from scripts import load_pixels
from scripts.files import monthly_files

# INPUT
start_year = 1991
end_year = 2020

######## Program, don't modify ########
output_directory = "output/temperature-tests"
os.makedirs(output_directory, exist_ok=True)

with open("output/precipitation-tests/points.csv") as f:
    points = [(float(row["latitude"]), float(row["longitude"])) for row in csv.DictReader(f)]

months = {
    quantity: [load_pixels(path) for path in monthly_files(start_year, end_year, quantity)]
    for quantity in ("T2MMAX", "T2MMIN")
}
height, width = months["T2MMAX"][0].shape

# The grid nodes are 0.5 degrees of latitude and 360 / width degrees of longitude apart, and it wraps around
rows = [(90 - latitude) * (height - 1) / 180 for latitude, _ in points]
columns = [(longitude + 180) / 360 * width for _, longitude in points]


def sample(image):
    padded = np.concatenate([image, image[:, :1]], axis=1)
    return map_coordinates(padded, [rows, np.mod(columns, width)], order=1, mode="nearest")


with open(f"{output_directory}/points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    names = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    writer.writerow(
        ["latitude", "longitude"]
        + [f"high_{name}" for name in names]
        + [f"low_{name}" for name in names]
    )
    highs = np.array([sample(image) for image in months["T2MMAX"]])
    lows = np.array([sample(image) for image in months["T2MMIN"]])
    for i, (latitude, longitude) in enumerate(points):
        writer.writerow(
            [latitude, longitude]
            + [round(float(v), 2) for v in highs[:, i]]
            + [round(float(v), 2) for v in lows[:, i]]
        )
print(f"Points: {len(points)}")
