from scripts import era5, compression, natural_earth, to_tif, progress, load_pixels
import numpy as np
import os

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020
remove_oceans = True

era5.download(start_year, end_year)
natural_earth.download()
era5.process_precipitation(start_year, end_year)

files = [
    f'images/{start_year}-{end_year}-{month}-total_precipitation.tif' for month in range(1, 13)]

# Zero out the oceans of each file
if remove_oceans:
    with progress.progress('Removing oceans', len(files)) as pbar:
        for file in files:
            natural_earth.remove_oceans_from_tif(file, file.replace(
                'total_precipitation', 'total_precipitation_land'))
            pbar.update(1)

files = [
    f'images/{start_year}-{end_year}-{month}-{'total_precipitation_land' if remove_oceans else 'total_precipitation'}.tif' for month in range(1, 13)]


new_files = []
with progress.progress('Splitting images', len(files)) as pbar:
    for file in files:
        # Split the 16-bit image into 2 8-bit images
        compression.split_16_bits(file, file.replace('.tif', '_lower.tif'),
                      file.replace('.tif', '_upper.tif'), 1000 * 30)
        new_files.append(file.replace('.tif', '_lower.tif'))
        new_files.append(file.replace('.tif', '_upper.tif'))
        pbar.update(1)

compression.minify_multiple(
    new_files,
    lambda x: x,
    -999,
    'precipitation',
    True,
    100,
    True,
    (360, 180),
    grouping=2,
    a_override=1,
    b_override=0
)

# Rename to be the month numbers (instead of 2 * m-2*m + 1)
for i in range(12):
    first = i * 2 + 1
    second = first + 1
    file_name = f'output/precipitation-{first}-{second}.webp'
    new_file_name = f'output/precipitation-{i + 1}.webp'
    os.rename(file_name, new_file_name)
