from scripts import etopo, merra2, natural_earth
from scripts.operators import process, Map, Replace, Resize, Save, LinearCompression, Type, Group
import numpy as np

start_year = 1991
end_year = 2020

def get_file_index(i, group_size):
    start = i * group_size + 1
    end = start + group_size - 1
    return f"{start}-{end}"


merra2.download(start_year, end_year)
etopo.download()
natural_earth.download()

etopo.process_dem()
merra2.process_temperatures(start_year, end_year)

high_files = [f'images/{start_year}-{end_year}-{month}-T2MMAX.tif' for month in range(1, 13)]
low_files = [f'images/{start_year}-{end_year}-{month}-T2MMIN.tif' for month in range(1, 13)]

compression_index = 2

_, metadata_high = process(
    high_files,
    Replace(-999, 0),
    Map(lambda x: np.floor(x * 9/5 + 32)),
    LinearCompression(),
    Resize((576, 361)),
    Type(np.uint8),
    Group(3),
    Save(lambda i: f'output/temperatures/T2MMAX-{get_file_index(i, 3)}.webp', quality=100, lossless=False)
)

_, metadata_low = process(
    low_files,
    Replace(-999, 0),
    Map(lambda x: np.floor(x * 9/5 + 32)),
    LinearCompression(),
    Resize((576, 361)),
    Type(np.uint8),
    Group(3),
    Save(lambda i: f'output/temperatures/T2MMIN-{get_file_index(i, 3)}.webp', quality=100, lossless=False)
)

print("High:", metadata_high[compression_index])
print("Low:", metadata_low[compression_index])