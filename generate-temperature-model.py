from scripts import etopo, merra2, compression, natural_earth
import numpy as np

start_year = 1991
end_year = 2020

merra2.download(start_year, end_year)
etopo.download()
natural_earth.download()

etopo.process_dem()
merra2.process_temperatures(start_year, end_year)

high_files = [f'images/{start_year}-{end_year}-{month}-T2MMAX.tif' for month in range(1, 13)]
low_files = [f'images/{start_year}-{end_year}-{month}-T2MMIN.tif' for month in range(1, 13)]
compression.minify_multiple(high_files, lambda x: np.floor(x * 9/5 + 32), -999, 'T2MMAX', True, 100, False, (576, 361))
compression.minify_multiple(low_files, lambda x: np.floor(x * 9/5 + 32), -999, 'T2MMIN', True, 100, False, (576, 361))