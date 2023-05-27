from scripts import to_tif
from scripts.progress import progress

with open('source/geoids.csv', 'r') as file:
    lines = file.readlines()

values = [line.split(',') for line in lines]

geoids = [[]]
last_latitude = -90
with progress("Loading geoid data", len(values)) as pbar:
    for value in values:
        if int(value[0]) != last_latitude:
            geoids.append([])
            last_latitude = int(value[0])
        geoids[-1].append(float(value[2]))
        pbar.update(1)

with progress("Creating geoids image", 1) as pbar:
    to_tif(geoids, 'images/geoids.tif', is_inverted=True)
    pbar.update(1)
