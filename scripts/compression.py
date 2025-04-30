from . import get_min_max, compress_to_webp2, load_pixels, to_tif
from .progress import progress
from PIL import Image
import numpy as np

# Pixel = a * value + b
# Value = (pixel - b) / a

def minify_multiple(files, map_point, invalid_value, data_point, use_rgb, quality, lossless, size=None, grouping=3, should_print=True, a_override=None, b_override=None):
    Image.MAX_IMAGE_PIXELS = None
    if a_override is not None and b_override is not None:
        a = a_override
        b = b_override
    else:
        with progress(f'Calculating compression offset ({data_point})', 1) as pbar:
            offset = get_min_max(files, map_point, invalid_value, size)
            pbar.update(1)

        b = -offset[0]
        # Map to 0-255 after subtracting the offset
        a = 255 / (offset[1] + b)
        if np.isinf(a):
            a = 1

        if should_print:
            print(f'A: {a}, B: {b}')

    grouping = grouping if use_rgb else 1
    
    with progress(f'Compressing ({data_point})', len(files)) as pbar:
        for i in range(0, len(files), grouping):
            compress_to_webp2(files[i:i+grouping], f'output/{data_point}-{i + 1}-{i + grouping}.webp', map_point, a, b, invalid_value, quality, lossless, size)
            pbar.update(grouping)
    
    return float(a), float(b)

def minify(path, map_point, invalid_value, output_filename, quality, lossless, size=None, a_override=None, b_override=None):
    Image.MAX_IMAGE_PIXELS = None
    if a_override is not None and b_override is not None:
        a = a_override
        b = b_override
    else:
        with progress('Calculating compression offset', 1) as pbar:
            offset = get_min_max([path], map_point, invalid_value)
            pbar.update(1)

        b = -offset[0]
        # Map to 0-255 after subtracting the offset
        a = 255 / (offset[1] + b)
        if np.isinf(a):
            a = 1

    print(f'A: {a}, B: {b}')
    
    with progress('Compressing', 1) as pbar:
        compress_to_webp2([path], output_filename, map_point, a, b, invalid_value, quality, lossless, size)
        pbar.update(1)

def split_16_bits(path, output_path_lower, output_path_upper, a=1, b=0):
    # Load the TIF
    image = load_pixels(path)
    image = np.rint(a * (image + b))
    image = image.astype(np.uint16)

    # Create 2 images: 1 for the lower 8 bits and one for the upper 8 bits
    lower_image = np.zeros(image.shape, dtype=np.uint8)
    upper_image = np.zeros(image.shape, dtype=np.uint8)

    # Split the 16-bit image into 2 8-bit images
    lower_image = image & 0x00FF
    upper_image = (image >> 8) & 0x00FF

    # Save both images
    to_tif(lower_image, output_path_lower)
    to_tif(upper_image, output_path_upper)