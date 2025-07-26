from scripts import compression, natural_earth, to_tif
from PIL import Image
import numpy as np
import os

pixels_per_degree = 15

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None

natural_earth.download()

if not os.path.exists('output'):
    os.makedirs('output')

# Create a white image of 360x180
image = np.full((2100, 4200), 255, dtype=np.uint8)

image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
to_tif(image, 'images/land.tif')

compression.minify('images/land.tif', lambda x: x, -99999, 'output/land.webp', 100, True, a_override=1, b_override=0)
