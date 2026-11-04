"""
This script generates the data for testing the precipitation model, it is not intended to be used for creating one.

It outputs output/precipitation-tests/points.csv with the ERA5 monthly precipitation (mm, using the same days per
month as Trail Sense) of points in hiking areas (the land points from the DEM test data, so generate-dem-test-data.py
must be run first) and points spread randomly over the land of the world. The
reference is the full resolution (0.25 degree) ERA5 cell containing the point, so the tests show the error added by
shrinking the model.
"""

import csv
import math
import os
import random

import geopandas as gpd
from shapely.geometry import Point

from scripts import era5, load_pixels, natural_earth
from scripts.files import monthly_files

# INPUT
start_year = 1991
end_year = 2020
hiking_points = 60
global_points = 40
# The model has little to say about these latitudes
min_latitude, max_latitude = -58, 72

######## Program, don't modify ########
output_directory = "output/precipitation-tests"
meters_to_millimeters = 1000
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
random.seed(42)

os.makedirs(output_directory, exist_ok=True)
era5.download(start_year, end_year)
natural_earth.download()
era5.process_precipitation(start_year, end_year)

land = gpd.read_file("source/natural-earth/ne_10m_land.shp").union_all()

with open("output/dem-tests/points.csv") as f:
    hiking = [
        (float(row["latitude"]), float(row["longitude"]))
        for row in csv.DictReader(f)
        if row["terrain"] != "ocean"
    ]
points = random.sample(hiking, hiking_points)

while len(points) < hiking_points + global_points:
    # Uniform over the surface of the world rather than over the map
    latitude = math.degrees(
        math.asin(random.uniform(math.sin(math.radians(min_latitude)), math.sin(math.radians(max_latitude))))
    )
    longitude = random.uniform(-180, 180)
    if land.contains(Point(longitude, latitude)):
        points.append((round(latitude, 3), round(longitude, 3)))

# Meters per day
months = [load_pixels(path) for path in monthly_files(start_year, end_year, "total_precipitation")]
height, width = months[0].shape

with open(f"{output_directory}/points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        ["latitude", "longitude"]
        + ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    )
    for latitude, longitude in points:
        row = min(int((90 - latitude) / 180 * height), height - 1)
        column = min(int((longitude + 180) / 360 * width), width - 1)
        values = [
            round(float(month[row, column]) * meters_to_millimeters * days, 1)
            for month, days in zip(months, days_in_month)
        ]
        writer.writerow([latitude, longitude] + values)
print(f"Points: {len(points)}")
