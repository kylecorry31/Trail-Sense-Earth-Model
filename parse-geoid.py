from scripts import to_tif

with open('datfiles/geoids.csv', 'r') as file:
    lines = file.readlines()

values = [line.split(',') for line in lines]

geoids = [[]]
last_latitude = -90
for value in values:
    if int(value[0]) != last_latitude:
        geoids.append([])
        last_latitude = int(value[0])
    geoids[-1].append(float(value[2]))

to_tif(geoids, 'images/geoids.tif', is_inverted=True)
