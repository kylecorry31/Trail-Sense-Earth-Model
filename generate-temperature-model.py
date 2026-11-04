from scripts import etopo, merra2
from scripts.files import monthly_files
from scripts.grid import area_weights
from scripts.report import print_stretch
from scripts.operators import (
    process,
    Replace,
    GridCellMean,
    AdjustForElevation,
    ClimateNormal,
    ClimateHarmonics,
    RemoveLatitudeTrend,
    WebpQualityOptions,
    Stretch,
    FitToBudget,
    Save,
)

# INPUT
start_year = 1991
end_year = 2020
# Set to False to reuse the climate normals saved by a previous run
recalculate_normals = True
# The number of annual cycles (harmonics) kept for each month's temperatures, more are more accurate and larger
harmonics = 4
# The degree of the polynomial of the sine of the latitude that is removed from each mean (it narrows the range)
trend_degree = 4
# The size of the model, in bytes. The quality of each image is chosen to get the lowest error within it.
size_budget_bytes = 150_000
qualities = [20, 30, 40, 50, 60, 70, 80, 85, 90, 93, 96, 99]

######## Program, don't modify ########
merra2.download(start_year, end_year)
etopo.download()

rows, columns = 361, 576
elevation_invalid_value = -99999
# The temperature drops 6.5 degrees per km of elevation
lapse_rate = 0.0065

names = ["T2MMAX", "T2MMIN"]
quantities = {name: monthly_files(start_year, end_year, name) for name in names}


def calculate_climate_normals():
    """Saves the climate normals at sea level at full precision (they are also the reference for the test data)."""
    etopo.process_dem()

    # Each MERRA-2 temperature is the mean of its whole cell, so it is brought to sea level with the mean elevation of
    # the cell
    elevations, _ = process(
        [etopo.dem_land_path],
        Replace(elevation_invalid_value),
        GridCellMean((rows, columns)),
        show_progress=True,
    )
    for name in names:
        process(
            [
                f"source/merra2/{year}-{month}-{name}.tif"
                for year in range(start_year, end_year + 1)
                for month in range(1, 13)
            ],
            AdjustForElevation(elevations[0], lapse_rate),
            ClimateNormal(),
            Save(f"images/{start_year}-{end_year}-{{i}}-{name}.tif"),
            show_progress=True,
        )


if recalculate_normals:
    calculate_climate_normals()

mean_index = ClimateHarmonics.MEAN_INDEX
images_per_quantity = 1 + 2 * harmonics
# Errors are weighted by the ground area of each pixel
weights = area_weights(rows, columns)

# The mean counts in every month, while each cosine and sine counts in half of them on average
importance_per_quantity = [1 if i == mean_index else 0.5 for i in range(images_per_quantity)]

harmonic_images = []
trends = {}
for name, files in quantities.items():
    images, results = process(
        files,
        ClimateHarmonics(harmonics, trend_degree),
        show_progress=True,
    )
    harmonic_images += images
    trends[name] = results.of(RemoveLatitudeTrend)["trends"][mean_index]

# The images of both quantities share the size budget
_, results = process(
    harmonic_images,
    FitToBudget(
        WebpQualityOptions(qualities, Stretch(calculate_per_image=True), weights=weights),
        size_budget_bytes,
        importance=importance_per_quantity * len(quantities),
    ),
    Save(lambda i: f"output/temperatures/{names[i // images_per_quantity]}-{i % images_per_quantity}.webp"),
)
chosen = results.of(FitToBudget)["chosen"]

total_size = sum(len(option["data"]) for option in chosen)
print(f"Saved {total_size / 1000:.0f} KB of the {size_budget_bytes / 1000:.0f} KB budget")
print("Qualities:", [option["quality"] for option in chosen])
print()

# Each image is value = pixel / a - b
coefficients = results.of(FitToBudget)["coefficients"]
for index, name in enumerate(names):
    name_coefficients = coefficients[index * images_per_quantity:(index + 1) * images_per_quantity]
    print_stretch(
        name,
        name_coefficients,
        f"images 0 to {images_per_quantity - 1}: the mean, then the cosine and sine of each harmonic. value = pixel / a - b",
    )
    print("    mean latitude trend (lowest power of sin(latitude) first):", trends[name])
