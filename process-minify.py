from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

lon_step = 2
lat_step = 1
min_lat = -56
max_lat = 83
latitude_pixels_per_degree = 2
longitude_pixels_per_degree = 2 # NASA 1.6, CRU 2
data_point_min = 'tmn'
data_point_max = 'tmx'
data_point_delta = 'tdelta'
filename_format = 'images/1991-2020-{month}-{data_point}.tif'
output_filename = f'{data_point_min}.csv'


######## Program, don't modify ########

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

def get_start_latitude(dataset, from_top=True):
    for lat in range(-90, 91):
        for lon in range(-180, 181):
            if get_value_lat_lon(-lat if from_top else lat, lon, dataset, False) is not None:
                return -lat if from_top else lat
    return None

def get_value_lat_lon(lat, lon, dataset, replace_none=True):
    l = 180 - (lat + 90)
    y = int(l * latitude_pixels_per_degree) - 1
    x = int((lon + 180) * longitude_pixels_per_degree) - 1
    value =  get_value(x, y, dataset)
    if value is None and replace_none:
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

def get_values(data_point):
    count_none = 0
    all_values = []
    for month in range(1, 13):
        values = get_data(filename_format.format(month=month, data_point=data_point))
        print(f'Processing {data_point} for month {month}')
        # print(f"Start: {get_start_latitude(values)}, End: {get_start_latitude(values, False)}")

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
        all_values.append(parsed_values)
    print(f'None: {count_none}')
    return all_values

def write_csv(values, filename):
    min_value = 100000
    max_value = -100000
    raw_min = 100000
    raw_max = -100000
    csv = ''
    for month in values:
        for value in month:
            output_value = int(round(value))
            if output_value > raw_max:
                raw_max = output_value
            if output_value < raw_min:
                raw_min = output_value
    for month in values:
        for value in month:
            output_value = int(round(value)) - raw_min
            csv += f'\n{output_value}'
            if output_value > max_value:
                max_value = output_value
            if output_value < min_value:
                min_value = output_value
    print(f'{filename} Min: {min_value}, Max: {max_value}, Raw Min: {raw_min}, Raw Max: {raw_max}, Offset {-raw_min}')
    f = open(filename, 'w')
    f.write(csv.strip())
    f.close()


highs = get_values(data_point_max)
lows = get_values(data_point_min)

# Calculate delta
deltas = []
for i in range(0, len(highs)):
    delta = []
    for j in range(0, len(highs[i])):
        delta.append(highs[i][j] - lows[i][j])
    deltas.append(delta)

write_csv(lows, f'{data_point_min}.csv')
write_csv(highs, f'{data_point_max}.csv')
write_csv(deltas, f'{data_point_delta}.csv')