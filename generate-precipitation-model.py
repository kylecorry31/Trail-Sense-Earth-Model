from scripts import era5, compression

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
era5.process_precipitation(start_year, end_year)

files = [f'images/{start_year}-{end_year}-{month}-total_precipitation.tif' for month in range(1, 13)]
compression.minify_multiple(files, lambda x: x, -999, 'precipitation', True, 100, False, (576, 361))