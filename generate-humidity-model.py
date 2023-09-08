from scripts import merra2, compression

start_year = 1991
end_year = 2020

merra2.download(start_year, end_year)
merra2.process_humidity()

point = 'QV'

files = [f'images/1981-{month}-{point}.tif' for month in range(1, 13)]
compression.minify_multiple(files, lambda x: int(x * 1000), -9999, point, True, 100, False, (576, 361))