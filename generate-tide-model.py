from scripts import compression, got, eot20, natural_earth


# got or eot20
source = 'eot20'


natural_earth.download()
if source == 'eot20':
    eot20.download()
else:
    got.download()

if source == 'eot20':
    amplitudes, large_amplitudes = eot20.process_ocean_tides((720, 360))
else:
    amplitudes, large_amplitudes = got.process_ocean_tides((720, 360))

constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'MS4', 'MU2', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA',
                'SSA'] if source == 'got' else ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

directory = f'images/{source}'

scale_map = {}

files = [f'{directory}/{constituent}-amplitude.tif' for constituent in constituents]
compression.minify_multiple(files, lambda x: x, 100000, 'tide-amplitudes', True, 100, True, None, 3, should_print=False, a_override=255, b_override=0)

files = [f'{directory}/{constituent}-phase.tif' for constituent in constituents]
compression.minify_multiple(files, lambda x: x, 100000, 'tide-phases', True, 100, True, None, 3, should_print=False, a_override=255, b_override=0)

files = [f'{directory}/indices-x.tif', f'{directory}/indices-y.tif']
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
    print(f'    listOf(TideConstituent.{f'_2N2' if amplitude[0] == '2N2' else amplitude[0]}, {
          amplitude[1]}, {amplitude[2]}, {amplitude[3]}),')

print(')')
