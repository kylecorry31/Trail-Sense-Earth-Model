from scripts import to_tif, load_pixels
from PIL import Image
import numpy as np

# INPUT
new_size = (1440, 720)#(2160, 1080)
land_mask_filename = 'images/land-ne.tif'

######## Program, don't modify ########
Image.MAX_IMAGE_PIXELS = None

geoids = load_pixels('source/etopo/ETOPO_2022_v1_60s_N90W180_geoid.tif', new_size)
elevations = load_pixels('source/etopo/ETOPO_2022_v1_60s_N90W180_surface.tif', new_size)
mask = load_pixels(land_mask_filename, new_size)

output_filename = 'images/dem-etopo.tif'

print(f"Min: {np.min(elevations)} Max: {np.max(elevations)}")

# Add the geoids
elevations += geoids

print(f"Min: {np.min(elevations)} Max: {np.max(elevations)}")

# Set the pixels to 0 if the mask is 0
elevations[mask < 127] = 0
# elevations[elevations < -440] = 0

print(f"Min: {np.min(elevations)} Max: {np.max(elevations)}")

to_tif(elevations, output_filename)