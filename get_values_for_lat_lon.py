from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

lon_step = 3
lat_step = 1
min_lat = -60
max_lat = 84

def get_temperature(x, y, dataset):
    return dataset[y, x]

def get_data(path):
    im = Image.open(path)
    # im.show()
    return np.array(im)

def has_value(x, y, dataset):
    return dataset[y, x] > -1000

def get_average_temperature(x, y, dataset):
    total = 0
    count = 0
    for x1 in range(x, x + (60 / 10) * lat_step + 1):
        for y1 in range(y, y + (60 / 10) * lon_step + 1):
            if has_value(x, y, dataset):
                total += get_temperature(x1, y1, dataset)
                count += 1
    if count > 0:
        return total / count
    else:
        return -1000

def get_average_temperature_for_lat_lon(lat, lon, dataset):
    l = 180 - (lat + 90)
    y = int(l * 60 / 10) - 1
    x = int((lon + 180) * 60 / 10) - 1
    return get_temperature(x, y, dataset)

# lows = get_data(f'wc2.1_10m_tmax_12.tif')
# print(get_average_temperature_for_lat_lon(42, -72, lows))

# exit()

# Lows
all = ''

for month in range(1, 13):
    lows = get_data(f'wc2.1_10m_tmin_{str(month).zfill(2)}.tif')

    averages = []
    for lat in range(min_lat, max_lat + 1, lat_step):
        for lon in range(-180, 181, lon_step):
            low = get_average_temperature_for_lat_lon(lat, lon, lows)
            if low < -1000:
                low = -1000
            if low == -1000 and len(averages) > 0:
                averages.append(averages[-1])
            elif low == -1000:
                averages.append(0)
            else:
                averages.append(low)
    csv = ''
    for value in averages:
        csv += f'\n{int(round(value * 9/5 + 32))}'
    all += csv
f = open('low_temperatures_global.csv', 'w')
f.write(all.strip())
f.close()

# Highs
all = ''

for month in range(1, 13):
    lows = get_data(f'wc2.1_10m_tmax_{str(month).zfill(2)}.tif')

    averages = []
    for lat in range(min_lat, max_lat, lat_step):
        for lon in range(-180, 181, lon_step):
            low = get_average_temperature_for_lat_lon(lat, lon, lows)
            if low < -1000:
                low = -1000
            if low == -1000 and len(averages) > 0:
                averages.append(averages[-1])
            elif low == -1000:
                averages.append(0)
            else:
                averages.append(low)
    csv = ''
    for value in averages:
        csv += f'\n{int(round(value * 9/5 + 32))}'
    all += csv
f = open('high_temperatures_global.csv', 'w')
f.write(all.strip())
f.close()