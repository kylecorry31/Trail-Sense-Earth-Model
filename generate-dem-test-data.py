"""
This script generates the data for testing the DEM files, it is not intended to be used for creating a DEM.

It outputs three CSV files to output/dem-tests:
- points.csv: random points in hiking areas, grouped by terrain (plus a few over the ocean and well known peaks)
- routes.csv: points every 300 meters along hiking routes, for checking elevation gain and loss
- seams.csv: pairs of nearby points on either side of a tile boundary, along with control pairs of the same size away
  from any boundary to compare them to

Generated with https://open-meteo.com, see their website for more information.

ESA - EUsers, who, in their research, use the Copernicus DEM, are requested to use the following DOI when citing the data source in their publications:

https://doi.org/10.5270/ESA-c5d3d65
"""

import csv
import json
import math
import os
import random
import time

import requests
import tqdm

output_directory = "output/dem-tests"
cache_path = f"{output_directory}/elevation-cache.json"
random.seed(42)

# (name, terrain, min latitude, max latitude, min longitude, max longitude, number of points)
areas = [
    ("Colorado Rockies", "mountains", 37.5, 40.5, -107.5, -105.5, 14),
    ("Sierra Nevada", "mountains", 36.0, 38.5, -119.5, -118.0, 14),
    ("Washington Cascades", "mountains", 46.5, 48.8, -122.0, -120.5, 14),
    ("Alps", "mountains", 45.5, 47.5, 6.5, 11.5, 16),
    ("Pyrenees", "mountains", 42.5, 42.9, -1.0, 2.0, 10),
    ("Nepal Himalaya", "mountains", 27.5, 29.0, 83.0, 87.0, 16),
    ("Cusco Andes", "mountains", -13.8, -12.8, -73.0, -71.5, 12),
    ("Patagonia", "mountains", -51.2, -49.8, -73.5, -72.3, 10),
    ("Jotunheimen", "mountains", 61.3, 61.9, 7.5, 9.0, 10),
    ("Tien Shan", "mountains", 41.5, 42.5, 74.0, 78.0, 10),
    ("Southern Alps", "mountains", -44.5, -43.2, 169.0, 171.5, 10),
    ("Japan Alps", "mountains", 35.5, 36.8, 137.3, 138.3, 10),
    ("Alaska Range", "mountains", 62.5, 63.5, -152.0, -149.0, 8),
    ("Simien Mountains", "mountains", 13.0, 13.5, 37.8, 38.5, 8),
    ("Mount Kilimanjaro", "mountains", -3.5, -2.8, 36.8, 37.6, 8),
    ("Scottish Highlands", "mountains", 56.5, 57.2, -5.5, -3.5, 10),
    ("Great Smoky Mountains", "hills", 34.8, 36.2, -84.0, -81.8, 12),
    ("White Mountains", "hills", 44.0, 44.6, -71.8, -70.8, 12),
    ("Adirondacks", "hills", 43.8, 44.5, -74.5, -73.2, 10),
    ("Ozarks", "hills", 36.0, 37.0, -94.0, -91.5, 8),
    ("Lake District", "hills", 54.3, 54.7, -3.4, -2.8, 8),
    ("Blue Ridge", "hills", 37.5, 38.8, -79.0, -78.0, 8),
    ("Tasmania", "hills", -43.3, -41.5, 145.5, 147.0, 8),
    ("Blue Mountains", "hills", -34.0, -33.4, 150.0, 151.0, 8),
    ("Black Forest", "hills", 47.8, 48.5, 7.8, 8.5, 8),
    ("Galicia", "hills", 42.5, 43.0, -8.0, -7.0, 8),
    ("US Midwest", "flat", 40.0, 42.0, -96.0, -92.0, 10),
    ("North Sea Plain", "flat", 52.0, 53.0, 5.0, 10.0, 8),
    ("Canadian Prairies", "flat", 50.0, 52.0, -105.0, -102.0, 8),
    ("Pampas", "flat", -35.0, -33.0, -64.0, -60.0, 8),
    ("West Siberian Plain", "flat", 56.0, 58.0, 70.0, 74.0, 8),
    ("Australian Outback", "flat", -27.0, -24.0, 135.0, 138.0, 8),
    ("Amazon Basin", "flat", -4.0, -2.0, -62.0, -58.0, 8),
    ("Central India", "flat", 21.0, 23.0, 78.0, 80.0, 8),
]

# Open ocean, which the DEM should report as sea level
ocean_points = [
    (35.0, -40.0), (-20.0, -30.0), (10.0, -140.0), (-35.0, -120.0), (0.0, 80.0),
    (-30.0, 80.0), (36.0, 18.0), (60.0, -30.0), (20.0, 160.0), (-55.0, 0.0),
]

# Well known peaks with their official summit elevations (not from the reference data), which show how much of a
# summit the DEM keeps
peaks = [
    ("Mount Washington", 44.2706, -71.3033, 1917),
    ("Mount Everest", 27.9881, 86.925, 8849),
    ("K2", 35.8825, 76.5133, 8611),
    ("Kangchenjunga", 27.7025, 88.1475, 8586),
    ("Denali", 63.0692, -151.0063, 6190),
    ("Aconcagua", -32.6532, -70.0109, 6961),
    ("Kilimanjaro", -3.0674, 37.3556, 5895),
    ("Mont Blanc", 45.8326, 6.8652, 4806),
    ("Matterhorn", 45.9763, 7.6586, 4478),
    ("Mount Elbrus", 43.355, 42.4392, 5642),
    ("Mount Fuji", 35.3606, 138.7274, 3776),
    ("Mount Rainier", 46.8523, -121.7603, 4392),
    ("Mount Whitney", 36.5786, -118.292, 4421),
    ("Mount Kosciuszko", -36.456, 148.2634, 2228),
    ("Aoraki / Mount Cook", -43.595, 170.1418, 3724),
    ("Mount Kenya", -0.1521, 37.3084, 5199),
    ("Mount Kinabalu", 6.0753, 116.5586, 4095),
    ("Puncak Jaya", -4.0833, 137.1833, 4884),
    ("Ben Nevis", 56.7969, -5.0036, 1345),
    ("Mount Elbert", 39.1178, -106.4454, 4401),
    ("Mount Katahdin", 45.9044, -68.9214, 1606),
]

# Routes are straight segments between named waypoints (trailhead, passes, summits), so the elevations are
# from the DEM along the waypoints' line rather than the exact trail
routes = {
    "Mount Washington via Tuckerman Ravine": [(44.2563, -71.2535), (44.2619, -71.2893), (44.2706, -71.3033)],
    "Presidential Range traverse": [(44.2706, -71.3033), (44.3046, -71.3176), (44.3203, -71.2909), (44.3328, -71.2778)],
    "Mist Trail to Half Dome": [(37.7324, -119.5578), (37.7270, -119.5436), (37.7254, -119.5333), (37.7459, -119.5332)],
    "Mount Whitney": [(36.5889, -118.2406), (36.5732, -118.2749), (36.5786, -118.2920)],
    "Tour du Mont Blanc (south)": [(45.8914, 6.7980), (45.7795, 6.7234), (45.7425, 6.8089), (45.7969, 6.9690)],
    "Machame route": [(-3.1925, 37.2447), (-3.0744, 37.2917), (-3.1000, 37.3333), (-3.0833, 37.3500), (-3.0674, 37.3556)],
    "Annapurna Base Camp": [(28.2750, 83.7970), (28.3736, 83.8058), (28.4940, 83.8790), (28.5300, 83.8780)],
    "Everest Base Camp": [(27.6869, 86.7314), (27.8069, 86.7140), (27.8361, 86.7644), (27.8920, 86.8310), (28.0026, 86.8528)],
    "Kungsleden (north)": [(68.3573, 18.7870), (68.2480, 18.2900)],
    "Springer Mountain to Blood Mountain": [(34.6268, -84.1938), (34.7388, -83.9387)],
    "Mount Fuji (Yoshida)": [(35.3939, 138.7326), (35.3606, 138.7274)],
    "Ben Nevis": [(56.8000, -5.0710), (56.7970, -5.0420), (56.7969, -5.0036)],
    "Bright Angel Trail": [(36.0571, -112.1439), (36.0777, -112.1206), (36.0996, -112.0943)],
    "Camino de Santiago (Sarria to Portomarin)": [(42.7770, -7.4140), (42.8070, -7.6160)],
}
route_spacing_meters = 300

# Tile boundaries are every 15 degrees: (axis, boundary, start, end) where the axis is the one the boundary is on
seam_lines = [
    ("longitude", -120.0, 36.0, 47.0),
    ("longitude", -105.0, 37.0, 46.0),
    ("longitude", -75.0, 40.0, 45.0),
    ("longitude", 0.0, 42.5, 43.0),
    ("longitude", 15.0, 46.0, 47.5),
    ("longitude", 75.0, 35.0, 41.0),
    ("longitude", 90.0, 27.0, 31.0),
    ("longitude", -75.0, -14.0, -9.0),
    ("latitude", 45.0, -112.0, -108.0),
    ("latitude", 45.0, 6.0, 8.0),
    ("latitude", 30.0, 80.0, 85.0),
    ("latitude", 30.0, 100.0, 103.0),
    ("latitude", 60.0, 6.0, 8.0),
    ("latitude", 15.0, 37.0, 39.0),
    ("latitude", -30.0, -71.0, -69.0),
    ("latitude", 0.0, -79.0, -77.0),
    ("latitude", -45.0, 168.0, 171.0),
]
seam_offset_degrees = 0.004
seam_pairs_per_line = 4
# Control pairs are this far from the boundary, which is far enough to not cross another one (they are 15 degrees apart)
control_distance_degrees = 0.5

os.makedirs(output_directory, exist_ok=True)
cache = {}
if os.path.exists(cache_path):
    with open(cache_path) as f:
        cache = json.load(f)


def key(latitude, longitude):
    return f"{latitude:.5f},{longitude:.5f}"


def fetch_elevations(coordinates):
    missing = [c for c in coordinates if key(*c) not in cache]
    for start in tqdm.tqdm(range(0, len(missing), 100), desc="Fetching elevations"):
        batch = missing[start : start + 100]
        url = (
            "https://api.open-meteo.com/v1/elevation"
            f"?latitude={','.join(f'{c[0]:.5f}' for c in batch)}"
            f"&longitude={','.join(f'{c[1]:.5f}' for c in batch)}"
        )
        for attempt in range(8):
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                for coordinate, elevation in zip(batch, response.json()["elevation"]):
                    cache[key(*coordinate)] = elevation
                break
            # The free tier limits requests per minute
            time.sleep(65 if response.status_code == 429 else 2**attempt)
        else:
            raise Exception(f"Failed to fetch elevations: {response.status_code}")
        with open(cache_path, "w") as f:
            json.dump(cache, f)
        time.sleep(12)
    return [cache[key(*c)] for c in coordinates]


def distance_meters(a, b):
    meters_per_degree = 111320
    dy = (b[0] - a[0]) * meters_per_degree
    dx = (b[1] - a[1]) * meters_per_degree * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dx, dy)


def densify(waypoints):
    points = [waypoints[0]]
    for start, end in zip(waypoints, waypoints[1:]):
        steps = max(int(distance_meters(start, end) // route_spacing_meters), 1)
        for i in range(1, steps + 1):
            t = i / steps
            points.append(
                (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)
            )
    return points


# Points in hiking areas
area_points = []
for name, terrain, lat_min, lat_max, lon_min, lon_max, count in areas:
    for _ in range(count):
        area_points.append(
            (terrain, random.uniform(lat_min, lat_max), random.uniform(lon_min, lon_max))
        )
elevations = fetch_elevations([(lat, lon) for _, lat, lon in area_points])
with open(f"{output_directory}/points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["terrain", "latitude", "longitude", "elevation"])
    skipped = 0
    for (terrain, lat, lon), elevation in zip(area_points, elevations):
        # Water inside an area is not the terrain being tested
        if elevation is None or elevation == 0:
            skipped += 1
            continue
        writer.writerow([terrain, round(lat, 5), round(lon, 5), int(elevation)])
    for lat, lon in ocean_points:
        writer.writerow(["ocean", lat, lon, 0])
    for _, lat, lon, elevation in peaks:
        writer.writerow(["peaks", lat, lon, elevation])
print(
    f"Points: {len(area_points) - skipped} land, {len(ocean_points)} ocean, {len(peaks)} peaks ({skipped} water points skipped)"
)

# Routes
route_points = [(name, c) for name, waypoints in routes.items() for c in densify(waypoints)]
elevations = fetch_elevations([c for _, c in route_points])
with open(f"{output_directory}/routes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["route", "latitude", "longitude", "elevation"])
    for (name, (lat, lon)), elevation in zip(route_points, elevations):
        writer.writerow([name, round(lat, 5), round(lon, 5), elevation])
print(f"Routes: {len(routes)} routes, {len(route_points)} points")

# Seams
candidates = []
for axis, boundary, start, end in seam_lines:
    line_candidates = []
    for _ in range(seam_pairs_per_line * 4):
        along = random.uniform(start, end)

        def pair(across):
            if axis == "longitude":
                return (along, across - seam_offset_degrees), (along, across + seam_offset_degrees)
            return (across - seam_offset_degrees, along), (across + seam_offset_degrees, along)

        line_candidates.append((pair(boundary), pair(boundary + control_distance_degrees)))
    candidates.append(line_candidates)
flat = [c for line in candidates for pairs in line for pair in pairs for c in pair]
fetch_elevations(flat)
with open(f"{output_directory}/seams.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["kind", "latitude_a", "longitude_a", "elevation_a", "latitude_b", "longitude_b", "elevation_b"])
    count = 0
    for line in candidates:
        kept = 0
        for seam, control in line:
            pairs = [("seam", seam), ("control", control)]
            elevations = [(cache[key(*a)], cache[key(*b)]) for _, (a, b) in pairs]
            if any(e < 100 for pair_elevations in elevations for e in pair_elevations):
                continue
            for (kind, (a, b)), (elevation_a, elevation_b) in zip(pairs, elevations):
                writer.writerow([kind, round(a[0], 5), round(a[1], 5), int(elevation_a), round(b[0], 5), round(b[1], 5), int(elevation_b)])
            kept += 1
            count += 1
            if kept == seam_pairs_per_line:
                break
print(f"Seams: {count} pairs")
