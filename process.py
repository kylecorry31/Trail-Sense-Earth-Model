from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

lon_step = 2
lat_step = 1
min_lat = -60
max_lat = 84
latitude_pixels_per_degree = 2
longitude_pixels_per_degree = 1.6 # NASA 1.6, CRU 2
data_point = 'T2MMAX'
filename_format = 'images/1991-2020-{month}-{data_point}.tif'
output_filename = f'{data_point}.csv'

# temperature, range, or none
output_transform = 'temperature'


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
    return y > 0 and y < dataset.shape[0] and x > 0 and x < dataset.shape[1] and dataset[y, x] != -999

def get_value_lat_lon(lat, lon, dataset):
    l = 180 - (lat + 90)
    y = int(l * latitude_pixels_per_degree) - 1
    x = int((lon + 180) * longitude_pixels_per_degree) - 1
    value =  get_value(x, y, dataset)
    if value is None:
        return get_neighbor_value(x, y, dataset, 1, 5)
    return value

def get_neighbor_value(x, y, dataset, search, max_search):
    # Get all points at the given search distance
    points = []
    for i in range(-search, search + 1):
        for j in range(-search, search + 1):
            if abs(i) == search or abs(j) == search:
                if has_value(x + i, y + j, dataset):
                    points.append(get_value(x + i, y + j, dataset))
    if len(points) > 0:
        return sum(points) / len(points)
    if search < max_search:
        return get_neighbor_value(x, y, dataset, search + 1, max_search)
    return None

# Lows
all = ''

count_none = 0

# total = 0
for month in range(1, 13):
    values = get_data(filename_format.format(month=month, data_point=data_point))

    parsed_values = []
    for lat in range(min_lat, max_lat + 1, lat_step):
        for lon in range(-180, 181, lon_step):
            value = get_value_lat_lon(lat, lon, values)
            if value is None and len(parsed_values) > 0:
                count_none += 1
                parsed_values.append(parsed_values[-1])
            elif value is None:
                count_none += 1
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

#213528
print(f'None: {count_none}')
print(f'Min: {min_value}')
print(f'Max: {max_value}')