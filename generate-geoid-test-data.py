"""
This script generates the data for testing the geoid model, it is not intended to be used for creating one.

It outputs output/geoid-tests/points.csv with the geoid height (m) at points in hiking areas (the land points from
the DEM test data, so generate-dem-test-data.py must be run first), points spread randomly over the world, a grid
over the world, and points at the extremes (the poles, the antimeridian, and where the geoid is highest, lowest, and
changes the fastest). The reference is the bilinear interpolation of the full resolution (1 arc minute) ETOPO 2022
geoid, so the tests show the error added by shrinking the model.
"""

import csv
import math
import os
import random

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

from scripts import etopo, load_pixels

# INPUT
hiking_points = 150
global_points = 150
# The spacing of the grid (degrees)
grid_latitude_step = 20
grid_longitude_step = 30

######## Program, don't modify ########
output_directory = "output/geoid-tests"
# The full resolution geoid is larger than the default limit
Image.MAX_IMAGE_PIXELS = None
random.seed(42)

os.makedirs(output_directory, exist_ok=True)
etopo.download()

geoid = load_pixels(etopo.geoid_path)
height, width = geoid.shape


def sample(latitude, longitude):
    """The geoid height at a location, interpolated between the centers of the pixels (it wraps around at the antimeridian)."""
    x = (longitude + 180) / 360 * width - 0.5
    y = (90 - latitude) / 180 * height - 0.5
    padded = np.concatenate([geoid[:, -2:], geoid, geoid[:, :2]], axis=1)
    return float(map_coordinates(padded, [[y], [x + 2]], order=1, mode="nearest")[0])


with open("output/dem-tests/points.csv") as f:
    hiking = [
        (float(row["latitude"]), float(row["longitude"]))
        for row in csv.DictReader(f)
        if row["terrain"] != "ocean"
    ]

points = {
    "hiking": random.sample(hiking, hiking_points),
    # Uniform over the surface of the world rather than over the map
    "global": [
        (
            round(math.degrees(math.asin(random.uniform(-1, 1))), 3),
            round(random.uniform(-180, 180), 3),
        )
        for _ in range(global_points)
    ],
    "grid": [
        (float(latitude), float(longitude))
        for latitude in range(-80, 81, grid_latitude_step)
        for longitude in range(-180, 180, grid_longitude_step)
    ],
}

# Where the geoid is highest, lowest, and changes the fastest (per pixel), found on the full resolution image
step = 60
gradient = np.hypot(np.gradient(geoid, axis=0), np.gradient(geoid, axis=1))
extremes = []
for name, image, find in (
    ("highest", geoid, np.argmax),
    ("lowest", geoid, np.argmin),
    ("steepest", gradient, np.argmax),
):
    row, column = np.unravel_index(find(image), image.shape)
    extremes.append((round(90 - (row + 0.5) / height * 180, 3), round((column + 0.5) / width * 360 - 180, 3)))
points["extremes"] = extremes + [
    # The poles and the ends of the image
    (90.0, 0.0),
    (-90.0, 0.0),
    (90.0, 180.0),
    (-90.0, -180.0),
    # Either side of the antimeridian and the prime meridian
    (0.0, 179.99),
    (0.0, -179.99),
    (45.0, 179.99),
    (45.0, -179.99),
    (-45.0, 179.99),
    (-45.0, -179.99),
    (0.0, 0.0),
    (0.0, 0.01),
    (0.0, -0.01),
]

with open(f"{output_directory}/points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["latitude", "longitude", "geoid"])
    for group in points.values():
        for latitude, longitude in group:
            writer.writerow([latitude, longitude, round(sample(latitude, longitude), 2)])
print(f"Points: {sum(len(p) for p in points.values())}")
