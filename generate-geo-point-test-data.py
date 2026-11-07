from scripts.geo_points import Field, GeoPointFormat
import os

# A small geo point file which the app's tests read, to check that it reads what the generator writes
file_format = GeoPointFormat(
    cell_degrees=5,
    decimals=6,
    fields=(Field("kind", bytes=1), Field("height", bytes=2, step=0.5, offset=-100)),
    # Small blocks, so the file has more than one
    block_points=2,
    properties={"type": "test", "radius_meters": 1234.5},
)
points = [
    (44.270583, -71.303333, 3, 1916.5),
    (44.27, -71.3, 4, 1000),
    (-33.9249, 18.4241, 1, 12),
    (10, 179.999999, 2, -100),
    (-90, -180, 0, 0),
]

os.makedirs("output", exist_ok=True)
data = file_format.pack(
    [p[0] for p in points],
    [p[1] for p in points],
    {"kind": [p[2] for p in points], "height": [p[3] for p in points]},
)
with open("output/generator_sample.tsgeo", "wb") as f:
    f.write(data)
print(f"Saved output/generator_sample.tsgeo ({len(data)} bytes)")
