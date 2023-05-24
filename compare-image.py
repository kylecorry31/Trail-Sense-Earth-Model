from PIL import Image
import os
from scripts import compress_to_webp, get_min_max

# INPUT
input_filename = 'images/geoids.tif'
quality = 100
invalid_value = -999
max_acceptable_error = 3

map_point = lambda x: int(x)

######## Program, don't modify ########
output_dir = 'temp'
error_image = None
diff_map = {}
lossy_filesize = 0
lossless_filesize = 0

def create_image(path, offset, output, lossless=False):
    compress_to_webp([path], output, map_point, offset, invalid_value, quality, lossless)

def compare_images(path1, path2):
    global diff_map
    global lossy_filesize
    global lossless_filesize
    global error_image

    lossy_filesize += os.path.getsize(path1)
    lossless_filesize += os.path.getsize(path2)

    im1 = Image.open(path1)
    im2 = Image.open(path2)

    if not error_image:
        error_image = Image.new('L', (im1.size[0], im1.size[1]), color='black')

    for x in range(im1.size[0]):
        for y in range(im1.size[1]):
            t1 = im1.getpixel((x, y))
            t2 = im2.getpixel((x, y))
            r = abs(t1[0] - t2[0])
            g = abs(t1[1] - t2[1])
            b = abs(t1[2] - t2[2])

            error_image.putpixel((x, y), max([10 * r, 10 * g, 10 * b, error_image.getpixel((x, y))]))

            if r > max_acceptable_error or g > max_acceptable_error or b > max_acceptable_error:
                print(f'Error at {x}, {y}: {t1} vs {t2}')
            
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

    

def check():
    offset = get_min_max([input_filename], map_point, invalid_value)
    print(f'Offset: {-offset[0]} (Min: {offset[0]}, Max: {offset[1]})')
    
    create_image(input_filename, offset[0], f'{output_dir}/temp.webp')
    create_image(input_filename, offset[0], f'{output_dir}/temp-lossless.webp', True)
    compare_images(f'{output_dir}/temp.webp', f'{output_dir}/temp-lossless.webp')
    
    # Delete output directory
    for file in os.listdir(output_dir):
        os.remove(f'{output_dir}/{file}')
    os.rmdir(output_dir)


check()

total_count = sum(diff_map.values())

diff_str = ""
for key in sorted(diff_map.keys()):
    diff_str += f'{key}: {round(100 * diff_map[key] / total_count, 2)} %\n'

print(diff_str)

# Average error
total_error = 0
for key in diff_map.keys():
    total_error += key * diff_map[key]

average = total_error / total_count

print(f'Average error: {round(average, 2)}')

# Standard deviation
total_squared_error = 0
for key in diff_map.keys():
    total_squared_error += (key - average) ** 2 * diff_map[key]

standard_deviation = (total_squared_error / total_count) ** 0.5

print(f'Standard deviation: {round(standard_deviation, 2)}')

print(f'Lossy filesize: {round(lossy_filesize / 1024, 2)} KB')
print(f'Lossless filesize: {round(lossless_filesize / 1024, 2)} KB')
print(f'Compression ratio: {round(100 * lossy_filesize / lossless_filesize, 2)} %')

error_image.save(f'output/error.png')