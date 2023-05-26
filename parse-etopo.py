from PIL import Image
from scripts import load, to_tif
import numpy as np

# INPUT
elevation_filename = 'source/etopo/ETOPO_2022_v1_60s_N90W180_surface.tif'
geoid_filename = 'source/etopo/ETOPO_2022_v1_60s_N90W180_geoid.tif'
new_size = (576, 361)

######## Program, don't modify ########
output_filename = 'images/dem.tif'

Image.MAX_IMAGE_PIXELS = None

def apply_geoid(elevations, geoids):
    for x in range(len(elevations)):
        for y in range(len(elevations[0])):
            elevations[x][y] += geoids[x][y]

def get_data(path):
    im = load(path, new_size)
    return np.array(im)

elevations = get_data(elevation_filename)
geoids = get_data(geoid_filename)

apply_geoid(elevations, geoids)

to_tif(elevations, output_filename)