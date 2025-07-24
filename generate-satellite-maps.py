from scripts import visible_earth, natural_earth
import PIL.Image as Image
import numpy as np

visible_earth.download()
visible_earth.process_maps(0)

month = 7
image = Image.open(f"images/world-map-{month}.tif")

# Remove water
image = np.array(image)
image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
image = Image.fromarray(image)

# Simplify colors
image.thumbnail((3600, 3600))
image = visible_earth.__simplify(image, image, 8)
image.thumbnail((2400, 2400), resample=Image.NEAREST)

image.save(f"output/world-map-{month}.webp", quality=100, lossless=True, format='WEBP', method=6, alpha_quality=0, optimize=True, compress_level=9)
