from scripts import etopo, compression, natural_earth, clip, progress
from PIL import Image
import numpy as np
import os

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None

etopo.download()
natural_earth.download()

resolution = (360 * 20, 180 * 20)
with progress.progress('Removing oceans', 1) as pbar:
    natural_earth.remove_oceans_from_tif(etopo.surface_path, 'images/dem_no_oceans.tif', resize=resolution, scale=1)
    pbar.update(1)

dem_app = 'images/dem_no_oceans.tif'#images/dem_app.tif'
# clip.clip_uninhabitable_areas_tif('images/dem_no_oceans.tif', dem_app)

offsets = compression.get_min_max([dem_app])
print(offsets[0])
compression.split_16_bits(dem_app, 'images/dem_lower.tif', 'images/dem_upper.tif', 0.05, -offsets[0])

compression.minify_multiple(['images/dem_lower.tif', 'images/dem_upper.tif'], lambda x: x, -99999, 'dem', True, 100, True, grouping=2, a_override=1, b_override=0)


os.rename('output/dem-1-2.webp', 'output/dem.webp')