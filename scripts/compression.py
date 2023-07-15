from . import get_min_max, compress_to_webp2, compress_to_webp
from .progress import progress
from PIL import Image

# Pixel = a * value + b
# Value = (pixel - b) / a

def minify_multiple(files, map_point, invalid_value, data_point, use_rgb, quality, lossless, size=None):
    Image.MAX_IMAGE_PIXELS = None
    with progress(f'Calculating compression offset ({data_point})', 1) as pbar:
        offset = get_min_max(files, map_point, invalid_value, size)
        pbar.update(1)

    b = -offset[0]
    # Map to 0-255 after subtracting the offset
    a = 255 / (offset[1] + b)

    print(f'A: {a}, B: {b}')

    grouping = 3 if use_rgb else 1
    
    with progress(f'Compressing ({data_point})', len(files) // grouping) as pbar:
        for i in range(0, len(files), grouping):
            compress_to_webp2(files[i:i+grouping], f'output/{data_point}-{i + 1}-{i + grouping}.webp', map_point, a, b, invalid_value, quality, lossless, size)
            pbar.update(grouping)

def minify(path, map_point, invalid_value, output_filename, quality, lossless, size=None):
    Image.MAX_IMAGE_PIXELS = None
    with progress('Calculating compression offset', 1) as pbar:
        offset = get_min_max([path], map_point, invalid_value)
        pbar.update(1)

    b = -offset[0]
    # Map to 0-255 after subtracting the offset
    a = 255 / (offset[1] + b)

    print(f'A: {a}, B: {b}')
    
    with progress('Compressing', 1) as pbar:
        compress_to_webp2([path], output_filename, map_point, a, b, invalid_value, quality, lossless, size)
        pbar.update(1)