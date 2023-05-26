from PIL import Image
from scripts import load, load_pixels, to_tif, compress_to_webp
import numpy as np

# INPUT
new_size = (720, 360)
resolution = 15
include_bathymetry = False
image_filename_format = 'source/etopo/ETOPO_2022_v1_{grid_size}s_{latitude}{longitude}_{type}.tif' 

# Images are 3600x3600
# 240 pixels per degree

######## Program, don't modify ########
output_filename = 'images/dem.tif'
new_image = np.array(Image.new('F', new_size))

pixels_per_degree = 3600 / resolution

total_width = pixels_per_degree * 360
total_height = pixels_per_degree * 180

# TODO: Scale using total_width and total_height or set new resolution

num_tiles_lat = int(180 / resolution)
num_tiles_lon = int(360 / resolution)

individual_image_size = (int(new_size[0] / num_tiles_lon) + 1, int(new_size[1] / num_tiles_lat) + 1)

Image.MAX_IMAGE_PIXELS = None

def apply_geoid(elevations, geoids):
    for x in range(len(elevations)):
        for y in range(len(elevations[0])):
            elevations[x][y] += geoids[x][y]

def get_data(path):
    im = load(path, new_size)
    return np.array(im)

def update_image(latitude, longitude):
    lat = ('N' if latitude >= 0 else 'S') + str(abs(latitude)).zfill(2)
    lon = ('E' if longitude >= 0 else 'W') + str(abs(longitude)).zfill(3)
    img = load_pixels(image_filename_format.format(grid_size=resolution, latitude=lat, longitude=lon, type='surface'), individual_image_size)
    geoid = load_pixels(image_filename_format.format(grid_size=resolution, latitude=lat, longitude=lon, type='geoid'), individual_image_size)
    img = np.add(img, geoid)
    if not include_bathymetry:
        sid = load_pixels(image_filename_format.format(grid_size=resolution, latitude=lat, longitude=lon, type='surface_sid'), individual_image_size)
        # Set the pixel to 0 if the sid is for bathymetry
        img[sid < 9] = 0
        # img[sid == 12] = 0
    
    # Add it to the new image
    start_y = int((180 - (latitude + 90)) * new_size[1] / 181.0)
    start_x = int((longitude + 180) * new_size[0] / 361.0)
    # img = np.ones((individual_image_size[1], individual_image_size[0])) * 255
    print(start_x, start_y, latitude, longitude)
    new_image[start_y:start_y + individual_image_size[1], start_x:start_x + individual_image_size[0]] = img


for latitude in range(90, -90, -resolution):
    for longitude in range(-180, 180, resolution):
        update_image(latitude, longitude)

to_tif(new_image, output_filename)
compress_to_webp([output_filename], 'test.webp', lambda x: int(x))