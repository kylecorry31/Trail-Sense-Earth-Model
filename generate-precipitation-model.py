from scripts import era5
from scripts.operators import (
    process,
    Reshape,
    Map,
    Type,
    LinearCompression,
    Save,
)
from PIL import Image
import numpy as np

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

files = [
    f"images/{start_year}-{end_year}-{month}-total_precipitation.tif"
    for month in range(1, 13)
]

# The source is in meters per day. Precipitation is stored as its square root so that the error is
# proportional to the amount (dry places keep their detail, wet places don't waste bits). The largest
# monthly total is about 3,350 mm, which is 57.9 when square rooted.
mm_per_month = 1000 * 30
compression = 4.4

process(
    files,
    Reshape((width, height), Image.BOX),
    Map(lambda image: np.sqrt(np.maximum(image, 0) * mm_per_month)),
    LinearCompression(compression, 0),
    Map(np.rint),
    Type(np.uint8),
    Save(
        "output/precipitation/precipitation-{i}.webp",
        quality=quality,
        lossless=False,
        adaptive_quantization=False,
    ),
    show_progress=True,
)

print(f"precipitation (mm per month) = (pixel / {compression}) ^ 2")
