from scripts import era5
from scripts.files import monthly_files
from scripts.report import print_stretch
from scripts.operators import (
    process,
    Reshape,
    Clip,
    Scale,
    Sqrt,
    LinearCompression,
    Stretch,
    Save,
)
from PIL import Image

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

# INPUT
start_year = 1991
end_year = 2020
# Size of each month (the source is 1440x720). It must divide the source evenly, since the source pixels are averaged.
width, height = 1440, 720
# WebP quality, which sets the size of the model (higher is larger and more accurate)
quality = 70

######## Program, don't modify ########
era5.download(start_year, end_year)
era5.process_precipitation(start_year, end_year)

# The source is in meters per day. Precipitation is stored as its square root so that the error is
# proportional to the amount (dry places keep their detail, wet places don't waste bits).
mm_per_month = 1000 * 30

_, results = process(
    monthly_files(start_year, end_year, "total_precipitation"),
    Reshape((width, height), Image.BOX),
    Clip(min=0),
    Scale(mm_per_month),
    Sqrt(),
    Stretch(),
    Save(
        "output/precipitation/precipitation-{i}.webp",
        quality=quality,
        lossless=False,
        adaptive_quantization=False,
    ),
    show_progress=True,
)

print_stretch(
    "precipitation",
    # Every month is stretched the same
    results.of(LinearCompression)["coefficients"][:1],
    "mm per month = (pixel / a - b) ^ 2",
)
