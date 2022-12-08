from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

def get_temperature(x, y, dataset):
    return dataset[y, x]

def get_data(path):
    im = Image.open(path)
    return np.array(im)

def truncate(n, places):
    multiplier = 10 ** places
    return int(n * multiplier) / multiplier

def get_temperature_for_lat_lon(lat, lon, elevation, dataset):
    l = 180 - (lat + 90)
    y = int(l * 60 / 10) - 1
    x = int((lon + 180) * 60 / 10) - 1
    return get_temperature(x, y, dataset)

month = 1
x = []
y = []

jan = get_data(f'wc2.1_10m_tmin_01.tif')
jul = get_data(f'wc2.1_10m_tmin_07.tif')

for lat in range(-90, 91):
    for lon in range(-180, 181):
        temp1 = get_temperature_for_lat_lon(lat, lon, 0, jan)
        temp2 = get_temperature_for_lat_lon(lat, lon, 0, jul)
        if temp1 < -100 or temp2 < -100:
            continue
        x.append(lat)
        y.append(temp2)

plt.plot(x, y)
plt.show()




# for month in range(1, 13):
#     lows = get_data(f'wc2.1_10m_tmin_{str(month).zfill(2)}.tif')
#     low_temps.append(get_temperature_for_lat_lon(lat, lon, elevation, lows))