from PIL import Image
import numpy as np

latitude_pixels_per_degree = 2
longitude_pixels_per_degree = 2
high = 'tmx'
low = 'tmn'

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
    y = int(l * latitude_pixels_per_degree)
    x = int((lon + 180) * longitude_pixels_per_degree)
    c = get_temperature(x, y, dataset)
    return truncate(c - 0.0065 * elevation, 1) * 9/5 + 32

def format_kotlin(arr):
    return 'arrayOf(' + ', '.join(map(lambda a: str(a) + 'f', arr)) + ')'

location = [42, -72]
elevation = 151

lat = location[0]
lon = location[1]
low_temps = []
high_temps = []

for month in range(1, 13):
    lows = get_data(f'images/1991-2020-{str(month)}-{low}.tif')
    low_temps.append(get_temperature_for_lat_lon(lat, lon, elevation, lows))

for month in range(1, 13):
    highs = get_data(f'images/1991-2020-{str(month)}-{high}.tif')
    high_temps.append(get_temperature_for_lat_lon(lat, lon, elevation, highs))

print(low_temps)
print(high_temps)

# print(format_kotlin(low_temps))
# print(format_kotlin(high_temps))