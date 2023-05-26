from scripts import load, to_tif
import numpy as np

# INPUT
elevation_filename = 'source/worldclim/wc2.1_10m_elev.tif'
new_size = (576, 361)

######## Program, don't modify ########
output_filename = 'images/dem-worldclim.tif'

def get_data(path):
    im = load(path)
    arr = np.array(im)
    arr[arr == -32768] = 0
    return arr

elevations = get_data(elevation_filename)

to_tif(elevations, output_filename)