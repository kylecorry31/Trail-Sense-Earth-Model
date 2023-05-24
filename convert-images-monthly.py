from scripts import compress_to_webp, get_min_max

# INPUT
data_point_min = 'T2MMIN'
data_point_max = 'T2MMAX'
filename_format = 'images/1991-2020-{month}-{data_point}.tif'
output_dir = 'output'
quality = 100
invalid_value = -999
use_rgb = True
lossless = False

map_point = lambda x: int(x * 9/5 + 32)

######## Program, don't modify ########
def create_image(paths, offset, output):
    compress_to_webp(paths, output, map_point, offset, invalid_value, quality, lossless)

def minify(data_point):
    files = [filename_format.format(month=month, data_point=data_point) for month in range(1, 13)]
    offset = get_min_max(files, map_point, invalid_value)

    print(f'Offset: {-offset[0]} for {data_point} (Min: {offset[0]}, Max: {offset[1]})')

    grouping = 3 if use_rgb else 1
    
    for i in range(0, len(files), grouping):
        create_image(files[i:i+grouping], offset[0], f'{output_dir}/{data_point}-{i + 1}-{i + grouping}.webp')


minify(data_point_max)
minify(data_point_min)