from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import os

latitude_pixels_per_degree = 2
longitude_pixels_per_degree = 2 # NASA 1.6, CRU 2
data_point_min = 'tmn'
data_point_max = 'tmx'
filename_format = 'images/1991-2020-{month}-{data_point}.tif'
output_dir = 'output'
quality = 100
invalid_value = -999
grouping = 3

map_point = lambda x: int(x * 9/5 + 32)

######## Program, don't modify ########

def get_offset(paths):
    min_value = 1000
    for path in paths:
        im = Image.open(path)
        for x in range(im.size[0]):
            for y in range(im.size[1]):
                t = im.getpixel((x, y))
                if t != -999:
                    min_value = min(min_value, map_point(t))
    return min_value

def create_image(paths, offset, output):
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
    new_im.save(output, quality=quality)

def minify(data_point):
    files = [filename_format.format(month=month, data_point=data_point) for month in range(1, 13)]
    offset = get_offset(files)

    print(f'Offset: {-offset} for {data_point}')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    for i in range(0, len(files), grouping):
        create_image(files[i:i+grouping], offset, f'{output_dir}/{data_point}-{i + 1}-{i + grouping}.webp')


minify(data_point_max)
minify(data_point_min)