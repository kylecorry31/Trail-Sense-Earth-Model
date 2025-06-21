"""
This script generates random points for testing the DEM files, it is not intended to be used for creating a DEM.

Generated with https://open-meteo.com, see their website for more information.

ESA - EUsers, who, in their research, use the Copernicus DEM, are requested to use the following DOI when citing the data source in their publications:

https://doi.org/10.5270/ESA-c5d3d65
"""

import requests
import random
import time
import tqdm

continent_bounds = {
    "Africa": (-30, 30, -15, 45),
    "Asia": (10, 55, 45, 140),
    "Europe": (40, 60, -5, 30),
    "North America": (15, 55, -130, -60),
    "South America": (-40, 5, -75, -50),
    "Australia": (-35, -15, 115, 145),
}

def fetch_elevation_data(num_points=100):
    elevations = []
    zero_count = 0
    with tqdm.tqdm(total=num_points, desc="Fetching Elevation Data") as pbar:
        for _ in range(num_points):
            is_valid = False
            while not is_valid:
                continent = random.choice(list(continent_bounds.keys()))
                lat_min, lat_max, lon_min, lon_max = continent_bounds[continent]
                lat = random.uniform(lat_min, lat_max)
                lon = random.uniform(lon_min, lon_max)

                url = f'https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}'
                time.sleep(0.1)
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        elevation = int(data.get('elevation')[0])
                        if elevation is None or elevation == 0:
                            if zero_count > 8:
                                print("Too many 0s, retrying")
                                continue
                            zero_count += 1

                        if elevation is not None:
                            elevations.append({
                                'latitude': lat,
                                'longitude': lon,
                                'elevation': elevation
                            })
                        is_valid = True
                    else:
                        print(f"Error fetching data for {lat}, {lon}: {response.status_code}")
                except Exception as e:
                    print(f"Exception for {lat}, {lon}: {e}")
                    time.sleep(1)
            pbar.update(1)
    return elevations

def save_to_kotlin_file(elevations, filename='output/elevations.kt'):
    with open(filename, 'w') as f:
        f.write("val elevations = listOf(\n")
        for entry in elevations:
            f.write(f"    Coordinate({entry['latitude']}, {entry['longitude']}) to {entry['elevation']}f,\n")
        f.write(")\n")
    print(f"Data saved to {filename}")

num_points = 3
elevations = fetch_elevation_data(num_points)

if elevations:
    save_to_kotlin_file(elevations)
else:
    print("No elevation data was retrieved.")