from scripts import to_tif
import numpy as np

start = -89.875
filename = 'source/woa/landsea_04.msk.txt'
resolution = 0.125

### Program ###

total_x = int(180 / resolution)
total_y = int(90 / resolution)

def get_x(longitude):
    return int((longitude - resolution + 180) / resolution / 2)

def get_y(latitude):
    return int((latitude - resolution + 90) / resolution / 2)

with open(filename, 'r') as file:
    lines = file.readlines()[2:]

values = [line.split(',') for line in lines]

ele = np.zeros((total_y, total_x))

last_latitude = start
for value in values:
    latitude = float(value[0])
    longitude = float(value[1])
    ele[get_y(latitude)][get_x(longitude)] = float(value[2])

to_tif(ele, 'images/dem-woa.tif', is_inverted=True)

# Land mask
land = np.zeros((len(ele), len(ele[0])))
land[ele == 1] = 255
to_tif(land, 'images/land-woa.tif', is_inverted=True)

# Sea mask
sea = np.zeros((len(ele), len(ele[0])))
sea[ele != 1] = 255
to_tif(sea, 'images/sea-woa.tif', is_inverted=True)