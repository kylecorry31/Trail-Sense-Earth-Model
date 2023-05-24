import PIL.Image as Image
import numpy as np
from scripts import to_tif

# Input
# TODO: Load start and end from filename by default
start_year = 1991
end_year = 2020
data_point = 'T2MMIN'
invalid_value = -999

############ Program, don't modify ############
sum_values = []
count_values = []

def get_data(year, month):
    image = Image.open(f'source/{year}-{month}-{data_point}.tif')
    return np.array(image)

def write_img(year, month, values):
    to_tif(values, f'images/{year}-{month}-{data_point}.tif')

def average(arr, counts):
    return [[arr[i][j] / counts[i][j] if counts[i][j] > 0 else invalid_value for j in range(len(arr[0]))] for i in range(len(arr))]

def add(arr1, arr2):
    return [[arr1[i][j] + arr2[i][j] for j in range(len(arr1[0]))] for i in range(len(arr1))]

def replace_invalid(arr, value):
    return [[value if int(t) == invalid_value else t for t in row] for row in arr]

def count(arr):
    return [[1 if int(t) != invalid_value else 0 for t in row] for row in arr]

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        print(f'Processing {year}-{month}')
        values = get_data(year, month)
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