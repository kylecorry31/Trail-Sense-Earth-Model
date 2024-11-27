from scripts import compression, eot20, natural_earth

natural_earth.download()
eot20.download()
amplitudes, large_amplitudes = eot20.process_ocean_tides((720, 360))

constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

scale_map = {}

files = [f'images/eot20/{constituent}-amplitude.tif' for constituent in constituents]
compression.minify_multiple(files, lambda x: x, 100000, 'tide-amplitudes', True, 100, True, None, 3, should_print=False, a_override=255, b_override=0)

files = [f'images/eot20/{constituent}-phase.tif' for constituent in constituents]
compression.minify_multiple(files, lambda x: x, 100000, 'tide-phases', True, 100, True, None, 3, should_print=False, a_override=255, b_override=0)

files = ['images/eot20/indices-x.tif', 'images/eot20/indices-y.tif']
compression.minify_multiple(files, lambda x: x, 100000, 'tide-indices', True, 100, True, None, 2, should_print=False, a_override=1, b_override=0)

print()
print('A = 255, B = 0')
print()

# Print the amplitudes as a kotlin map
print('private val amplitudes = mapOf(')

for constituent, amplitude in amplitudes.items():
    print(f'    TideConstituent.{f'_2N2' if constituent == '2N2' else constituent} to {amplitude},')

print(')')

print()

# Print the large amplitudes
print('private val largeAmplitudes = listOf(')

for amplitude in large_amplitudes:
    print(f'    listOf(TideConstituent.{f'_2N2' if amplitude[0] == '2N2' else amplitude[0]}, {amplitude[1]}, {amplitude[2]}, {amplitude[3]}),')

print(')')

