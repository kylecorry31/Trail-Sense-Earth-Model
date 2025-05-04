from scripts import era5, compression, etopo, natural_earth

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
etopo.download()
natural_earth.download()

# etopo.process_dem()
era5.process_dew_point(start_year, end_year)

files = [f'images/{start_year}-{end_year}-{month}-2m_dewpoint_temperature.tif' for month in range(1, 13)]
compression.minify_multiple(files, lambda x: x, -999, 'dewpoint', True, 100, False, (360, 180))