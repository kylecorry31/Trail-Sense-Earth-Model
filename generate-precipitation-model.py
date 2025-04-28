from scripts import era5, compression, natural_earth, load, to_tif, progress
import numpy as np

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
natural_earth.download()
era5.process_precipitation(start_year, end_year)

files = [
    f'images/{start_year}-{end_year}-{month}-total_precipitation.tif' for month in range(1, 13)]

# Zero out the oceans of each file
with progress.progress('Removing oceans', len(files)) as pbar:
    for file in files:
        image = np.array(load(file))
        image = natural_earth.remove_oceans(image, 0)
        to_tif(image, file.replace(
            'total_precipitation', 'total_precipitation_land'))
        pbar.update(1)

files = [
    f'images/{start_year}-{end_year}-{month}-total_precipitation_land.tif' for month in range(1, 13)]
compression.minify_multiple(
    files,
    lambda x: x * 1000,
    -999,
    'precipitation',
    True,
    100,
    False,
    (720, 360)
)
