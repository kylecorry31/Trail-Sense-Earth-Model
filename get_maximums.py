from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

def get_temperature(x, y, dataset):
    return dataset[y, x]

def get_data(path):
    im = Image.open(path)
    # im.show()
    return np.array(im)

def has_value(x, y, dataset):
    return dataset[y, x] > -1000

def get_average_temperature(y, dataset):
    total = 0
    count = 0
    for x in range(0, dataset[y].shape[0]):
        if has_value(x, y, dataset):
            total += get_temperature(x, y, dataset)
            count += 1
    if count > 0:
        return total / count
    else:
        return -1000

def get_average_temperature_for_lat(lat, dataset):
    l = 180 - (lat + 90)
    y = int(l * 60 / 10) - 1
    return get_average_temperature(y, dataset)


all = ''

for month in range(1, 13):
    highs = get_data(f'wc2.1_10m_tmax_{str(month).zfill(2)}.tif')

    averages = []
    for lat in range(-90, 91):
        high = get_average_temperature_for_lat(lat, highs)
        if high == -1000 and len(averages) > 0:
            averages.append(averages[-1])
        elif high == -1000:
            averages.append(0)
        else:
            averages.append(high)
    csv = ''
    for lat in range(-90, 91):
        csv += f'\n{int(round(averages[lat + 90] * 9/5 + 32))}'
    all += csv
    # plt.plot(range(-90, 91), averages)
    # plt.show()
f = open('high_temperatures.csv', 'w')
f.write(all.strip())
f.close()