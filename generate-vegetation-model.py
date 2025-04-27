from scripts import era5, compression
import os

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
era5.process_vegetation(end_year)

files = [f'images/{end_year}-{end_year}-7-high_vegetation.tif',
         f'images/{end_year}-{end_year}-7-low_vegetation.tif']
compression.minify_multiple(files, lambda x: x, -999, 'vegetation',
                            True, 100, True, (576, 361), a_override=1, b_override=0)

os.rename('output/vegetation-1-3.webp', 'output/vegetation.webp')
