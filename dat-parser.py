import PIL.Image as Image
import re
import os

# Input
start_year = 1991
end_year = 2020
data_point = 'tmx'
scale = 10

############ Program, don't modify ############
lines = []
sum_values = []
count_values = []

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

def write_img(year, month, values):
    img = Image.new('F', (len(values[0]), len(values)), color='black')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            t = values[y][x]
            pixels[x, img.size[1] - y - 1] = t
    if not os.path.exists('images'):
        os.mkdir('images')
    img.save(f'images/{year}-{month}-{data_point}.tif')

def average(arr, counts):
    return [[arr[i][j] / counts[i][j] if counts[i][j] > 0 else -999 for j in range(len(arr[0]))] for i in range(len(arr))]

def add(arr1, arr2):
    return [[arr1[i][j] + arr2[i][j] for j in range(len(arr1[0]))] for i in range(len(arr1))]

def replace_invalid(arr, value):
    return [[value if int(t) == -999 else t for t in row] for row in arr]

def count(arr):
    return [[1 if int(t) != -999 else 0 for t in row] for row in arr]

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        print(f'Processing {year}-{month}')
        values = get_data(year, month, lines)
        if len(sum_values) < month:
            sum_values.append(replace_invalid(values, 0))
            count_values.append(count(values))
        else:
            sum_values[month - 1] = add(sum_values[month - 1], replace_invalid(values, 0))
            count_values[month - 1] = add(count_values[month - 1], count(values))

# Average the values
for month in range(1, 13):
    sum_values[month - 1] = average(sum_values[month - 1], count_values[month - 1])

# Write the average values to a TIF file
for month in range(1, 13):
    write_img(f'{start_year}-{end_year}', month, sum_values[month - 1])

# -999 = no data