from . import get_min_max, compress_to_webp
from .progress import progress
from PIL import Image

def minify_multiple(files, map_point, invalid_value, data_point, use_rgb, quality, lossless, size=None):
    Image.MAX_IMAGE_PIXELS = None
    with progress('Calculating compression offset', 1) as pbar:
        offset = get_min_max(files, map_point, invalid_value, size)
        pbar.update(1)

    print(f'Offset ({data_point}): {-offset[0]} for {data_point} (Min: {offset[0]}, Max: {offset[1]}, New Min: 0, New Max: {min(offset[1] - offset[0], 255)})')

    grouping = 3 if use_rgb else 1
    
    with progress('Compressing', len(files) // grouping) as pbar:
        for i in range(0, len(files), grouping):
            compress_to_webp(files[i:i+grouping], f'output/{data_point}-{i + 1}-{i + grouping}.webp', map_point, offset[0], invalid_value, quality, lossless, size)
            pbar.update(grouping)

def minify(path, map_point, invalid_value, output_filename, quality, lossless, size=None):
    Image.MAX_IMAGE_PIXELS = None
    with progress('Calculating compression offset', 1) as pbar:
        offset = get_min_max([path], map_point, invalid_value)
        pbar.update(1)

    print(f'Offset: {-offset[0]} (Min: {offset[0]}, Max: {offset[1]}, New Min: 0, New Max: {min(offset[1] - offset[0], 255)})')
    
    with progress('Compressing', 1) as pbar:
        compress_to_webp([path], output_filename, map_point, offset[0], invalid_value, quality, lossless, size)
        pbar.update(1)