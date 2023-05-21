import PIL.Image as Image
import re
import os

# Input
start_year = 1991
end_year = 2021
data_point = 'tmx'
write_images = False
scale = 10

############ Program, don't modify ############
years = float(end_year - start_year)
lines = []
global_temperatures = []

files = list(filter(lambda x: x.endswith(f'.{data_point}.dat'), os.listdir('datfiles')))
files.sort()

for file in files:
    with open(f'datfiles/{file}', 'r') as datfile:
        lines += datfile.readlines()


def get_data(year, month, lines):
    year = year - start_year
    month -= 1
    start = 360 * year * 12 + month * 360
    end = start + 360
    temperatures = []
    for line in lines[start:end]:
        values = re.split(r'\s+', line.strip())
        temperatures.append([-999 if int(value) == -999 else (float(value) / scale) for value in values])
    return temperatures

def write_img(year, month, temperatures):
    img = Image.new('F', (len(temperatures[0]), len(temperatures)), color='black')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            t = temperatures[y][x]
            pixels[x, img.size[1] - y - 1] = t
    if not os.path.exists('images'):
        os.mkdir('images')
    img.save(f'images/{year}-{month}-{data_point}.tif')

def divide(temperatures, value):
    return [[t / value for t in row] for row in temperatures]

def add(t1, t2):
    return [[t1[i][j] + t2[i][j] for j in range(len(t1[0]))] for i in range(len(t1))]

for year in range(start_year, end_year):
    for month in range(1, 13):
        print(f'Processing {year}-{month}')
        temperatures = get_data(year, month, lines)
        if len(global_temperatures) < month:
            global_temperatures.append(temperatures)
        else:
            global_temperatures[month - 1] = add(global_temperatures[month - 1], temperatures)
        if write_images:
            write_img(year, month, temperatures)

# Average the temperatures
for month in range(1, 13):
    global_temperatures[month - 1] = divide(global_temperatures[month - 1], years)

# Write the average temperatures to a TIF file
for month in range(1, 13):
    write_img(f'{start_year}-{end_year}', month, global_temperatures[month - 1])

# -999 = no data