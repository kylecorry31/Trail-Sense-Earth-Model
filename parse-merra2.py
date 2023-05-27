import PIL.Image as Image
import numpy as np
from scripts import to_tif, load_pixels
from tqdm import tqdm

# Input
# TODO: Load start and end from filename by default
start_year = 1991
end_year = 2020
data_point = 'T2MMIN'
elevation_image = 'images/dem-land-etopo.tif'
elevation_invalid_value = -99999

############ Program, don't modify ############
Image.MAX_IMAGE_PIXELS = None
sum_values = []
count_values = []
with tqdm(total=1, desc="Loading elevation data") as pbar:
    elevations = load_pixels(elevation_image)
    pbar.update(1)
elevation_w = len(elevations[0])
elevation_h = len(elevations)

def to_sea_level(data):
    w = len(data[0])
    h = len(data)
    for y in range(h):
        for x in range(w):
            elevation_x = int(x / w * elevation_w)
            elevation_y = int(y / h * elevation_h)
            elevation = elevations[elevation_y, elevation_x]
            if elevation == elevation_invalid_value:
                elevation = 0
            # Invert elevation to bring it back down to sea level
            data[y, x] = data[y, x] + 0.0065 * elevation
    return data

def get_data(year, month):
    return load_pixels(f'source/merra2/{year}-{month}-{data_point}.tif')

def write_img(year, month, values):
    to_tif(values, f'images/{year}-{month}-{data_point}.tif')

# Calculate the climate normals
with tqdm(total=(end_year - start_year + 1) * 12, desc=f"Calculating climate normals ({data_point})") as pbar:
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            values = to_sea_level(get_data(year, month))
            if len(sum_values) < month:
                sum_values.append(values)
                count_values.append(1)
            else:
                sum_values[month - 1] += values
                count_values[month - 1] += 1
            pbar.update(1)

# Average the values
for month in range(1, 13):
    sum_values[month - 1] = sum_values[month - 1] / count_values[month - 1]

# Write the average values to a TIF file
with tqdm(total=12, desc=f"Generating images ({data_point})") as pbar:
    for month in range(1, 13):
        write_img(f'{start_year}-{end_year}', month, sum_values[month - 1])
        pbar.update(1)