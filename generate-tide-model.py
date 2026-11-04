from scripts import eot20, natural_earth
from scripts.report import print_stretch, kotlin_map, kotlin_list
from scripts.operators import (
    process,
    Crop,
    FlipY,
    ShiftX,
    ReplaceInvalid,
    RemoveOceans,
    PolarToCartesian,
    CartesianToPolar,
    Quadtree,
    HilbertOrder,
    CondenseLabels,
    SnapToNeighbors,
    LabelIndices,
    ReplaceLargeValues,
    SplitProcessing,
    Normalize,
    Replace,
    LinearCompression,
    Stretch,
    Type,
    Save,
)
import numpy as np

# INPUT
# The number of cells in the model, which sets its size (about 19 bytes per cell in total)
cell_budget = 22000
# Cells start at the base size and are split in half down to the min size where the tide varies more between neighbors
base_degrees = 1.0
min_degrees = 0.25

######## Program, don't modify ########
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

invalid_value = 100000
# Amplitudes (cm) above this are too large to store in the images, so they are listed separately
large_amplitude_threshold = 500
# The smallest phasor magnitude (cm) to measure the change in tide between cells against
error_floor = 10
# Tide values are replaced by a neighbor's when it changes the tide at that cell by less than this fraction, which makes
# the model compress better (higher values compress better but are less accurate)
snap_tolerance = 0.01
# The width of the images that hold the cells (this needs to be less than 255)
final_width = 128

natural_earth.download()
eot20.download()

# Load the amplitude and phase of each constituent as a phasor (x, y), so cells can be averaged
phasors = []
for constituent in constituents:
    images, _ = process(
        eot20.load(constituent),
        ReplaceInvalid(invalid_value),
        # The source grid includes the -90 degree row and a duplicate 360 degree column
        Crop(top=1, right=1),
        ShiftX(0.5, True),
        FlipY(),
        # all_touched keeps the ocean around islands smaller than a pixel
        RemoveOceans(dilation=5, replacement=invalid_value, all_touched=True),
        PolarToCartesian(invalid_value),
        Type(np.float32),
    )
    phasors.extend(images)

# Cells are base_degrees where the tide varies slowly and are split in half, down to min_degrees, where it varies more.
# The cells are ordered along a curve so neighboring cells are next to each other, which helps the model compress.
degrees_per_pixel = 360 / phasors[0].shape[1]
labels, _ = process(
    phasors,
    Quadtree(
        round(base_degrees / degrees_per_pixel),
        round(min_degrees / degrees_per_pixel),
        cell_budget,
        invalid_value,
        reference_floor=error_floor,
    ),
    HilbertOrder(),
    show_progress=True,
)

# Set each cell to the average of the source cells it covers
cells, _ = process(
    phasors,
    CondenseLabels(labels[0], final_width, invalid_value),
    CartesianToPolar(invalid_value),
    SnapToNeighbors(snap_tolerance, invalid_value, large_amplitude_threshold),
)
del phasors
amplitudes = cells[0::2]
phases = cells[1::2]

# Maps each pixel to its cell
process(
    labels,
    LabelIndices(final_width),
    Save("output/tides/tide-indices-{range}.webp", group=2),
)

# Amplitudes are normalized by the max amplitude of each constituent (stored in the app)
_, amplitude_results = process(
    amplitudes,
    ReplaceLargeValues(large_amplitude_threshold, invalid_value=invalid_value),
    SplitProcessing(Normalize(0.0, invalid_value=invalid_value)),
    Replace(invalid_value),
    Stretch(a=255, b=0),
    Save("output/tides/tide-amplitudes-{range}.webp", group=3),
)

process(
    phases,
    Normalize(-180.0, 180.0, invalid_value),
    Replace(invalid_value),
    Stretch(a=255, b=0),
    Save("output/tides/tide-phases-{range}.webp", group=3),
)

max_amplitudes = {
    constituent: float(data[0]["maximum"])
    for constituent, data in zip(constituents, amplitude_results.of(SplitProcessing)["data"])
}

# Values are (row, column, amplitude), but the app looks them up by (x, y)
large_amplitudes = [
    (constituent, column, row, int(amplitude))
    for constituent, values in zip(constituents, amplitude_results.of(ReplaceLargeValues)["large_values"])
    for row, column, amplitude in values
]


def kotlin_name(constituent):
    return f"_{constituent}" if constituent == "2N2" else constituent


print()
# The amplitudes and phases are stretched the same
print_stretch("tide amplitudes and phases", amplitude_results.of(LinearCompression)["coefficients"][:1])
print()
print(
    kotlin_map(
        "amplitudes",
        {f"TideConstituent.{kotlin_name(c)}": amplitude for c, amplitude in max_amplitudes.items()},
    )
)
print()
print(
    kotlin_list(
        "largeAmplitudes",
        [[f"TideConstituent.{kotlin_name(c)}", column, row, amplitude] for c, column, row, amplitude in large_amplitudes],
    )
)
