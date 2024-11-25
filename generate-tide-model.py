from scripts import compression, eot20
import os

eot20.download()
eot20.process_ocean_tides()

constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

scale_map = {}

for constituent in constituents:
    files = [f'images/eot20/{constituent}-real.tif', f'images/eot20/{constituent}-imaginary.tif']
    scale = compression.minify_multiple(files, lambda x: x, 100000, f'constituents-{constituent}', True, 100, True, (720, 360), 2)
    os.rename(f'output/constituents-{constituent}-1-2.webp', f'output/constituents-{constituent}.webp')
    scale_map[constituent] = scale

# Print as a kotlin dictionary
print('mutableMapOf(')

for constituent, scale in scale_map.items():
    print(f'    TideConstituent.{f'_2N2' if constituent == '2N2' else constituent} to Pair({scale[0]}, {scale[1]}),')

print(')')