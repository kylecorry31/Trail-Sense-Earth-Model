from scripts import compression, eot20, natural_earth, load_pixels
from scripts.operators import process
from scripts.operators.compression import LinearCompression
from scripts.operators.basic import Group, Replace, Save
import numpy as np

natural_earth.download()
eot20.download()
amplitudes, large_amplitudes = eot20.process_ocean_tides((720, 360))

def get_file_index(i, group_size):
    start = i * group_size + 1
    end = start + group_size - 1
    return f"{start}-{end}"

constituents = [
    "2N2",
    "J1",
    "K1",
    "K2",
    "M2",
    "M4",
    "MF",
    "MM",
    "N2",
    "O1",
    "P1",
    "Q1",
    "S1",
    "S2",
    "SA",
    "SSA",
    "T2",
]

scale_map = {}

files = [f"images/eot20/{constituent}-amplitude.tif" for constituent in constituents]
images = [load_pixels(file) for file in files]
process(
    images,
    Replace(100000),
    LinearCompression(a=255, b=0),
    Group(3),
    Save(lambda i: f"output/tides/tide-amplitudes-{get_file_index(i, 3)}.webp", quality=100, lossless=True),
)

files = [f"images/eot20/{constituent}-phase.tif" for constituent in constituents]
images = [load_pixels(file) for file in files]
process(
    images,
    Replace(100000),
    LinearCompression(a=255, b=0),
    Group(3),
    Save(lambda i: f"output/tides/tide-phases-{get_file_index(i, 3)}.webp", quality=100, lossless=True),
)

files = ["images/eot20/indices-x.tif", "images/eot20/indices-y.tif"]
images = [load_pixels(file) for file in files]
process(
    images,
    Group(2),
    Save(lambda i: f"output/tides/tide-indices-{get_file_index(i, 2)}.webp", quality=100, lossless=True),
)

print()
print("A = 255, B = 0")
print()

# Print the amplitudes as a kotlin map
print("private val amplitudes = mapOf(")

for constituent, amplitude in amplitudes.items():
    print(
        f"    TideConstituent.{f'_2N2' if constituent == '2N2' else constituent} to {amplitude},"
    )

print(")")

print()

# Print the large amplitudes
print("private val largeAmplitudes = listOf(")

for amplitude in large_amplitudes:
    print(
        f"    listOf(TideConstituent.{f'_2N2' if amplitude[0] == '2N2' else amplitude[0]}, {amplitude[1]}, {amplitude[2]}, {amplitude[3]}),"
    )

print(")")
