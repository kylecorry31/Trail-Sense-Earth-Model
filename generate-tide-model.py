from scripts import compression, eot20
import os

eot20.download()
eot20.process_ocean_tides()

constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']
files = []

for constituent in constituents:
    files.append(f'images/eot20/{constituent}-real.tif')
    files.append(f'images/eot20/{constituent}-imaginary.tif')


compression.minify_multiple(files, lambda x: x, 100000, 'constituents', True, 100, True, (720, 360), 2)
i = 0
for consituent in constituents:
    os.rename(f'output/constituents-{i + 1}-{i + 2}.webp', f'output/constituents-{consituent}.webp')
    i += 2