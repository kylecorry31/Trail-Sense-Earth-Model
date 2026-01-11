from scripts import era5, etopo, natural_earth
from scripts.operators import (
    process,
    LinearCompression,
    Replace,
    Resize,
    Type,
    Group,
    Save,
)
import numpy as np

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
etopo.download()
natural_earth.download()

etopo.process_dem()
era5.process_dew_point(start_year, end_year)


def get_file_index(i, group_size):
    start = i * group_size + 1
    end = start + group_size - 1
    return f"{start}-{end}"


files = [
    f"images/{start_year}-{end_year}-{month}-2m_dewpoint_temperature.tif"
    for month in range(1, 13)
]

compression_index = 1

_, metadata = process(
    files,
    Replace(-999, 0),
    LinearCompression(),
    Resize((360, 180)),
    Type(np.uint8),
    Group(3),
    Save(
        lambda i: f"output/dewpoint/dewpoint-{get_file_index(i, 3)}.webp",
        quality=100,
        lossless=False,
    ),
)

print("Dewpoint:", metadata[compression_index])
