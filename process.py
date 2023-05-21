from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

lon_step = 2
lat_step = 1
min_lat = -60
max_lat = 84
pixels_per_degree = 2
filename_format = 'images/1991-2020-{month}-tmx.tif'
output_filename = 'tmx.csv'

# temperature, range, or none
output_transform = 'range'


######## Program, don't modify ########

min_value = 100000
max_value = -100000

def get_value(x, y, dataset):
    t = dataset[y, x]
    if t == -999:
        return None
    return t

def get_data(path):
    im = Image.open(path)
    return np.array(im)

def has_value(x, y, dataset):
    return dataset[y, x] > -1000

def get_value_lat_lon(lat, lon, dataset):
    l = 180 - (lat + 90)
    y = int(l * pixels_per_degree) - 1
    x = int((lon + 180) * pixels_per_degree) - 1
    return get_value(x, y, dataset)

# Lows
all = ''

# total = 0
for month in range(1, 13):
    values = get_data(filename_format.format(month=month))

    parsed_values = []
    for lat in range(min_lat, max_lat + 1, lat_step):
        for lon in range(-180, 181, lon_step):
            value = get_value_lat_lon(lat, lon, values)
            if value is None and len(parsed_values) > 0:
                parsed_values.append(parsed_values[-1])
            elif value is None:
                parsed_values.append(0)
            else:
                parsed_values.append(value)
    csv = ''
    for value in parsed_values:
        if output_transform == 'temperature':
            output_value = int(round(value * 9/5 + 32))
        elif output_transform == 'range':
            output_value = int(round(value / 2 * 9/5))
        else:
            output_value = int(round(value))
        csv += f'\n{output_value}'
        if output_value > max_value:
            max_value = output_value
        if output_value < min_value:
            min_value = output_value
    all += csv
f = open(output_filename, 'w')
f.write(all.strip())
f.close()

print(f'Min: {min_value}')
print(f'Max: {max_value}')