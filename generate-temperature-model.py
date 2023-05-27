from scripts import etopo, merra2, compression, natural_earth

merra2.download()
etopo.download()
natural_earth.download()

etopo.process_dem()
merra2.process_temperatures()

high_files = [f'images/1991-2020-{month}-T2MMAX.tif' for month in range(1, 13)]
low_files = [f'images/1991-2020-{month}-T2MMIN.tif' for month in range(1, 13)]
compression.minify_multiple(high_files, lambda x: int(x * 9/5 + 32), -999, 'T2MMAX', True, 100, False, (576, 361))
compression.minify_multiple(low_files, lambda x: int(x * 9/5 + 32), -999, 'T2MMIN', True, 100, False, (576, 361))