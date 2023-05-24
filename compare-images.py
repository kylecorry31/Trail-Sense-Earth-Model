from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import os

# INPUT

latitude_pixels_per_degree = 2
longitude_pixels_per_degree = 1.6 # NASA 1.6, CRU 2
data_point_min = 'T2MMIN'
data_point_max = 'T2MMAX'
filename_format = 'images/1991-2020-{month}-{data_point}.tif'
output_dir = 'temp'
quality = 100
invalid_value = -999
grouping = 3

map_point = lambda x: int(x * 9/5 + 32)

######## Program, don't modify ########

diff_map = {}

def get_offset(paths):
    min_value = 1000
    max_value = -1000
    for path in paths:
        im = Image.open(path)
        for x in range(im.size[0]):
            for y in range(im.size[1]):
                t = im.getpixel((x, y))
                if t != -999:
                    min_value = min(min_value, map_point(t))
                    max_value = max(max_value, map_point(t))
    return (min_value, max_value)

def create_image(paths, offset, output, lossless=False):
    images = [Image.open(path) for path in paths]
    new_im = Image.new('RGB' if len(images) == 3 else 'L', (images[0].size[0], images[0].size[1]), color='black')
    pixels = new_im.load()

    for x in range(new_im.size[0]):
        for y in range(new_im.size[1]):
            ts = [im.getpixel((x, y)) for im in images]
            if invalid_value in ts:
                if len(images) == 1:
                    pixels[x, y] = 0
                else:
                    pixels[x, y] = (0, 0, 0)
            else:
                mapped = [map_point(t) - offset for t in ts]
                if len(images) == 1:
                    pixels[x, y] = mapped[0]
                else:
                    pixels[x, y] = (mapped[0], mapped[1], mapped[2])
    new_im.save(output, quality=quality, lossless=lossless, format='WEBP')

def compare_images(path1, path2):
    global diff_map
    im1 = Image.open(path1)
    im2 = Image.open(path2)
    for x in range(im1.size[0]):
        for y in range(im1.size[1]):
            t1 = im1.getpixel((x, y))
            t2 = im2.getpixel((x, y))
            r = abs(t1[0] - t2[0])
            g = abs(t1[1] - t2[1])
            b = abs(t1[2] - t2[2])
            
            if r in diff_map:
                diff_map[r] += 1
            else:
                diff_map[r] = 1
            
            if g in diff_map:
                diff_map[g] += 1
            else:
                diff_map[g] = 1

            if b in diff_map:
                diff_map[b] += 1
            else:
                diff_map[b] = 1

    

def check(data_point):
    files = [filename_format.format(month=month, data_point=data_point) for month in range(1, 13)]
    offset = get_offset(files)

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    for i in range(0, len(files), grouping):
        create_image(files[i:i+grouping], offset[0], f'{output_dir}/{data_point}-{i + 1}-{i + grouping}.webp')
        create_image(files[i:i+grouping], offset[0], f'{output_dir}/{data_point}-{i + 1}-{i + grouping}-lossless.webp', True)
        compare_images(f'{output_dir}/{data_point}-{i + 1}-{i + grouping}.webp', f'{output_dir}/{data_point}-{i + 1}-{i + grouping}-lossless.webp')
    
    # Delete output directory
    for file in os.listdir(output_dir):
        os.remove(f'{output_dir}/{file}')
    os.rmdir(output_dir)


check(data_point_max)
check(data_point_min)

total_count = sum(diff_map.values())

diff_str = ""
for key in sorted(diff_map.keys()):
    diff_str += f'{key}: {round(100 * diff_map[key] / total_count, 2)}\n'

print(diff_str)