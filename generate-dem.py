from scripts import etopo, compression, natural_earth, clip, progress
from PIL import Image
import numpy as np

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None

etopo.download()
natural_earth.download()

resolution = (360 * 40, 180 * 40)
with progress.progress('Removing oceans', 1) as pbar:
    natural_earth.remove_oceans_from_tif(etopo.surface_path, 'images/dem_no_oceans.tif', resize=resolution, scale=1)
    pbar.update(1)

dem_app = 'images/dem_no_oceans.tif'#images/dem_app.tif'
# clip.clip_uninhabitable_areas_tif('images/dem_no_oceans.tif', dem_app)

compression.minify(dem_app, lambda x: np.clip(x, -10000, 0), -99999, 'output/dem-1.webp', 100, True)
compression.minify(dem_app, lambda x: np.clip(x, 0, 800), -99999, 'output/dem-2.webp', 100, True)
compression.minify(dem_app, lambda x: np.clip(x, 800, 10000), -99999, 'output/dem-3.webp', 100, True)

def merge_images_into_channels(red: str, green: str, blue: str, output_path: str):
    red_image = Image.open(red).convert("L")
    green_image = Image.open(green).convert("L")
    blue_image = Image.open(blue).convert("L")

    # Merge into a single image
    merged_image = Image.merge("RGB", (red_image, green_image, blue_image))
    merged_image.save(output_path, quality=90, lossless=False, format='WEBP')


merge_images_into_channels('output/dem-1.webp', 'output/dem-2.webp', 'output/dem-3.webp', 'output/dem.webp')