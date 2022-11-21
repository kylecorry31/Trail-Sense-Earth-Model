from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

def get_pressure(x, y, dataset):
    return dataset[y, x]

def get_data(path):
    im = Image.open(path)
    # im.show()
    return np.array(im)

def has_value(x, y, dataset):
    return dataset[y, x] > -1000

def get_average_pressure(y, dataset):
    total = 0
    count = 0
    for x in range(0, dataset[y].shape[0]):
        if has_value(x, y, dataset):
            total += get_pressure(x, y, dataset)
            count += 1
    if count > 0:
        return total / count
    else:
        return 0

def get_average_pressure_for_lat(lat, dataset):
    l = 180 - (lat + 90)
    y = int(l * 60 / 10) - 1
    return get_average_pressure(y, dataset)


all = ''

for month in range(1, 13):
    temps = get_data(f'wc2.1_10m_vapr_{str(month).zfill(2)}.tif')

    averages = []
    for lat in range(-90, 91):
        averages.append(get_average_pressure_for_lat(lat, temps))
    csv = ''
    for lat in range(-90, 91):
        csv += f'\n{int(round(averages[lat + 90] * 50))}'
    all += csv
    # plt.plot(range(-90, 91), averages)
    # plt.show()
f = open('vapor_pressures.csv', 'w')
f.write(all.strip())
f.close()