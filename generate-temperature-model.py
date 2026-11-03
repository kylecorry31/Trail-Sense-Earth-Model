from scripts import etopo, merra2
from scripts.operators import (
    process,
    FourierSeries,
    RemoveLatitudeTrend,
    LinearCompression,
    Map,
    Type,
    WebpQualityOptions,
)
from scripts.size_budget import fit_to_budget
import numpy as np
import os

# INPUT
start_year = 1991
end_year = 2020
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

etopo.process_dem()
merra2.process_temperatures(start_year, end_year)

quantities = {
    "T2MMAX": [f"images/{start_year}-{end_year}-{month}-T2MMAX.tif" for month in range(1, 13)],
    "T2MMIN": [f"images/{start_year}-{end_year}-{month}-T2MMIN.tif" for month in range(1, 13)],
}

mean_index = 0
images_per_quantity = 1 + 2 * harmonics
rows = 361
latitudes = 90 - 180 * np.arange(rows) / (rows - 1)
# Errors are weighted by the ground area of each row
weights = np.maximum(np.cos(np.radians(latitudes)), 0.01)[:, None] * np.ones((1, 576))

options = []
constants = {}
for name, files in quantities.items():
    images, results = process(
        files,
        FourierSeries(harmonics),
        RemoveLatitudeTrend(trend_degree, [mean_index]),
        show_progress=True,
    )
    trends = results[1]["trends"]
    compressed, results = process(
        images,
        LinearCompression(calculate_per_image=True),
        Map(np.rint),
        Type(np.uint8),
    )
    coefficients = results[0]["coefficients"]
    _, results = process(
        compressed,
        WebpQualityOptions(qualities, images, coefficients, weights),
    )
    constants[name] = (coefficients, trends[mean_index])
    for i, image_options in enumerate(results[0]["options"]):
        # The mean counts in every month, while each cosine and sine counts in half of them on average
        importance = 1 if i == mean_index else 0.5
        for option in image_options:
            options.append((name, i, option, importance))

groups = []
for name in quantities:
    for i in range(images_per_quantity):
        groups.append([o for o in options if o[0] == name and o[1] == i])
chosen = fit_to_budget(
    groups,
    size_budget_bytes,
    size=lambda o: len(o[2]["data"]),
    cost=lambda o: o[3] * o[2]["squared_error"],
)

os.makedirs("output/temperatures", exist_ok=True)
for name, i, option, _ in chosen:
    with open(f"output/temperatures/{name}-{i}.webp", "wb") as f:
        f.write(option["data"])

total_size = sum(len(o[2]["data"]) for o in chosen)
print(f"Saved {total_size / 1000:.0f} KB of the {size_budget_bytes / 1000:.0f} KB budget")
print("Qualities:", [o[2]["quality"] for o in chosen])
print()

# Each image is value = pixel / a - b
for name, (coefficients, trend) in constants.items():
    print(f"{name} (images 0 to {images_per_quantity - 1}: the mean, then the cosine and sine of each harmonic)")
    print("    a:", [c["a"] for c in coefficients])
    print("    b:", [c["b"] for c in coefficients])
    print("    mean latitude trend (lowest power of sin(latitude) first):", trend)
