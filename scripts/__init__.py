from PIL import Image
import os
import numpy as np
import math


def load(path, resize=None):
    im = Image.open(path)
    if resize is not None and im.size != resize:
        im = im.resize(resize, Image.NEAREST)
    return im

def load_pixels(path, resize=None):
    im = load(path, resize)
    return np.array(im)

def compress_to_webp2(paths, output_filename, map_point=lambda x: x, a=1, b=0, invalid_value=-999, quality=100, lossless=False, resize_source=None):
    if '/' in output_filename and not os.path.exists(output_filename.rsplit('/', 1)[0]):
        os.makedirs(output_filename.rsplit('/', 1)[0])
    images = [load(path, resize_source) for path in paths]

    image_arrays = [np.array(im) for im in images]
    # Skip extra calculations if no transformations are needed
    if map_point is None and invalid_value is None and a == 1 and b == 0:
        if len(images) == 1:
            new_im = images[0].convert('L')
        else:
            # Stack images into RGBA
            if len(images) == 3:
                r, g, b = images
                new_im = Image.merge('RGB', (r.convert('L'), g.convert('L'), b.convert('L')))
            elif len(images) == 4:
                r, g, b, a = images
                new_im = Image.merge('RGBA', (r.convert('L'), g.convert('L'), b.convert('L'), a.convert('L')))
            else:
                # Fallback for other cases
                mapped = np.zeros((*image_arrays[0].shape, 4), dtype=np.uint8)
                mapped[..., 3] = 255
                for i in range(len(images)):
                    mapped[..., i] = image_arrays[i]
                new_im = Image.fromarray(mapped)
    else:
        # Original calculation logic
        if len(images) == 1:
            image_arrays = image_arrays[0]
            mask = (image_arrays == invalid_value) | np.isnan(image_arrays)
            mapped = np.where(mask, 0, np.int32(a * (map_point(image_arrays) + b)))
            new_im = Image.fromarray(mapped.astype(np.uint8), mode='L')
        else:
            mask = np.any([(image_arrays[i] == invalid_value) | np.isnan(image_arrays[i]) for i in range(len(images))], axis=0)
            mapped = np.zeros((*image_arrays[0].shape, 4), dtype=np.uint8)
            mapped[..., 3] = 255
            for i in range(len(images)):
                mapped[..., i] = np.where(mask, 0, np.int32(a * (map_point(image_arrays[i]) + b)))
            new_im = Image.fromarray(mapped, mode='RGBA')
    new_im.save(output_filename, quality=quality, lossless=lossless, format='PNG' if output_filename.endswith('png') else 'WEBP', method=6, alpha_quality=0 if len(images) < 3 else quality, optimize=True, compress_level=9)

def compress_to_webp(paths, output_filename, map_point=lambda x: x, offset=0, invalid_value=-999, quality=100, lossless=False, resize_source=None):
    if '/' in output_filename and not os.path.exists(output_filename.rsplit('/', 1)[0]):
        os.makedirs(output_filename.rsplit('/', 1)[0])
    images = [load(path, resize_source) for path in paths]
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
    new_im.save(output_filename, quality=quality, lossless=lossless, format='WEBP')

def get_min_max(paths, map_point=lambda x: x, invalid_value=-999, resize=None):
    min_value = 100000
    max_value = -100000
    for path in paths:
        im = load_pixels(path, resize)
        min_value = min(min_value, np.min(im[im != invalid_value]))
        max_value = max(max_value, np.max(im[im != invalid_value]))
    return (map_point(min_value), map_point(max_value))

def flip_vertical(image):
    return np.flipud(image)

def shift_x(image, x_shift):
    return np.roll(image, x_shift, axis=1)

def replace_invalid(image, replacement=0):
    values_array = np.ma.masked_invalid(image)
    values_array = np.where(values_array.mask, replacement, values_array)
    return values_array

def to_float(image):
    return image.astype(np.float32)

def to_tif(values, output=None, is_inverted=False, x_shift=0, masked_value_replacement=0, generate_webp=False):
    values_array = replace_invalid(values, masked_value_replacement)

    if x_shift != 0:
        values_array = shift_x(values_array, x_shift)
    
    if is_inverted:
        values_array = flip_vertical(values_array)

    values_array = to_float(values_array)
    img = Image.fromarray(values_array, mode='F')
    if output is not None:
        if not os.path.exists(output.rsplit('/', 1)[0]):
            os.makedirs(output.rsplit('/', 1)[0])
        img.save(output, format='TIFF', compression='tiff_lzw')
        if generate_webp:
            # Scale values from min/max to 0-255 for WebP
            min_val = np.min(values_array)
            max_val = np.max(values_array)
            if max_val > min_val:
                scaled_values = ((values_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            else:
                scaled_values = np.zeros_like(values_array, dtype=np.uint8)
            scaled_img = Image.fromarray(scaled_values, mode='L')
            scaled_img.thumbnail((4000, 4000))
            scaled_img.save(output + '.webp', format='WEBP')
    return values_array

def resize(path, output, size):
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(path)
    im = im.resize(size, Image.NEAREST)
    im.save(output, format='TIFF')
    im.save(output + '.webp', format='WEBP')

def reshape(image, shape):
    if shape is not None:
        img = Image.fromarray(image).resize(shape, Image.NEAREST)
        return np.array(img).reshape((shape[1], shape[0]))
    return image

def replace_color(image, old_color, new_color):
    mask = np.linalg.norm(image - old_color, axis=-1) <= 5
    image[mask] = new_color
    return image