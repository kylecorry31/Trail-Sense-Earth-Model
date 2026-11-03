from scripts import eot20, natural_earth
import numpy as np
from scripts.operators import process, LinearCompression, Map, Replace, Save

# INPUT
# The number of cells in the model, which sets its size (about 19 bytes per cell in total)
cell_budget = 22000
# Cells start at the base size and are split in half down to the min size where the tide varies more between neighbors
base_degrees = 1.0
min_degrees = 0.25

######## Program, don't modify ########
natural_earth.download()
eot20.download()
amplitudes, large_amplitudes = eot20.process_ocean_tides(cell_budget, base_degrees, min_degrees)

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


amplitude_and_phase_steps = [
    Replace(100000),
    LinearCompression(a=255, b=0),
    Map(np.round),
]

process(
    [f"images/eot20/{c}-amplitude.tif" for c in constituents],
    amplitude_and_phase_steps,
    Save("output/tides/tide-amplitudes-{range}.webp", group=3),
)

process(
    [f"images/eot20/{c}-phase.tif" for c in constituents],
    amplitude_and_phase_steps,
    Save("output/tides/tide-phases-{range}.webp", group=3),
)

process(
    ["images/eot20/indices-x.tif", "images/eot20/indices-y.tif"],
    Save("output/tides/tide-indices-{range}.webp", group=2),
)

print()
print("A = 255, B = 0")
print()

# Print the amplitudes as a kotlin map
def kotlin_name(constituent):
    return f"_{constituent}" if constituent == "2N2" else constituent


print("private val amplitudes = mapOf(")

for constituent, amplitude in amplitudes.items():
    print(
        f"    TideConstituent.{kotlin_name(constituent)} to {amplitude},"
    )

print(")")

print()

# Print the large amplitudes
print("private val largeAmplitudes = listOf(")

for amplitude in large_amplitudes:
    print(
        f"    listOf(TideConstituent.{kotlin_name(amplitude[0])}, {amplitude[1]}, {amplitude[2]}, {amplitude[3]}),"
    )

print(")")
