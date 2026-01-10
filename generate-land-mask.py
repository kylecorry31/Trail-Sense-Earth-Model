from scripts import natural_earth, to_tif, load_pixels
from scripts.operators import process
from scripts.operators.compression import LinearCompression
from scripts.operators.basic import Save
from PIL import Image
import numpy as np
import os

pixels_per_degree = 15

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None

natural_earth.download()

if not os.path.exists("output"):
    os.makedirs("output")

# Create a white image of 360x180
image = np.full((2100, 4200), 255, dtype=np.uint8)

image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
process([image], Save(["output/land.webp"], quality=100, lossless=True))
