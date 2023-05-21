import csv
import PIL.Image as Image

lon_step = 2
lat_step = 1
min_lat = -60
max_lat = 84
pixels_per_degree = 2

def get_temperature(lat, lon, dataset):
    l = 180 - (lat + 90)
    y = int(l * pixels_per_degree) - 1
    x = int((lon + 180) * pixels_per_degree) - 1

    return dataset[len(dataset) - y - 1][x] * 9/5 + 32

def write_img(year, month, temperatures):
    img = Image.new('L', (len(temperatures[0]), len(temperatures)), color='black')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            t = temperatures[y][x]
            pixels[x, img.size[1] - y - 1] = int(t * 9/5 + 32)
    img.save(f'test.tif')

def get_data(path):
    with open(path, 'r') as csvfile:
        lines = csvfile.readlines()
        return [[float(value) for value in line.split(',')] for line in lines]

data = get_data('csv/1991-2020-1-tmn.csv')
temp = get_temperature(42, -72, data)
write_img(0, 0, data)
print(temp)