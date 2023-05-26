from scripts import compress_to_webp, get_min_max

# INPUT
input_filename = 'images/dem.tif'
output_filename = 'output/dem.webp'
quality = 100
invalid_value = -999
lossless = False

map_point = lambda x: int(x)

######## Program, don't modify ########
def create_image(path, offset, output):
    compress_to_webp([path], output, map_point, offset, invalid_value, quality, lossless)

def minify():
    offset = get_min_max([input_filename], map_point, invalid_value)

    print(f'Offset: {-offset[0]} (Min: {offset[0]}, Max: {offset[1]})')
    
    create_image(input_filename, offset[0], output_filename)


minify()