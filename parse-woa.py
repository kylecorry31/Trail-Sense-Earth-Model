from scripts import to_tif
import numpy as np

start = -89.875 # -89.5
filename = 'source/woa/landsea_04.msk.txt'

with open(filename, 'r') as file:
    lines = file.readlines()[2:]

values = [line.split(',') for line in lines]

ele = [[]]
last_latitude = start
for value in values:
    if float(value[0]) != last_latitude:
        ele.append([])
        last_latitude = float(value[0])
    ele[-1].append(float(value[2]))

ele = np.array(ele)

to_tif(ele, 'images/dem-woa.tif', is_inverted=True)

# Land mask
land = np.zeros((len(ele), len(ele[0])))
land[ele == 1] = 255
to_tif(land, 'images/land-woa.tif', is_inverted=True)

# Sea mask
sea = np.zeros((len(ele), len(ele[0])))
sea[ele != 1] = 255
to_tif(sea, 'images/sea-woa.tif', is_inverted=True)