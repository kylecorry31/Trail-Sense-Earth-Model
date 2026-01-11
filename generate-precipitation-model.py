from scripts import era5, natural_earth
from scripts.operators import (
    process,
    Split16Bits,
    Save,
    Resize,
    RemoveOceans,
    Type,
    Map,
    LinearCompression,
)
import numpy as np

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
natural_earth.download()
era5.process_precipitation(start_year, end_year)

files = [
    f"images/{start_year}-{end_year}-{month}-total_precipitation.tif"
    for month in range(1, 13)
]

compression_index = 1
_, metadata = process(
    files,
    RemoveOceans(),
    LinearCompression(1000 * 30, 0),
    Map(lambda image: np.rint(image)),
    Resize((360, 180), exact=True),
    Type(np.uint16),
    Split16Bits(),
    Save(
        lambda i: f"output/precipitation/precipitation-{i+1}.webp",
        quality=100,
        lossless=True,
    ),
    show_progress=True,
)
print(metadata[compression_index])