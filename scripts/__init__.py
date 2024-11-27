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
    new_im.save(output_filename, quality=quality, lossless=lossless, format='WEBP')

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

def to_tif(values, output, is_inverted=False, x_shift=0, masked_value_replacement=0):
    values_array = np.ma.masked_invalid(values)
    values_array = np.where(values_array.mask, masked_value_replacement, values_array)

    if x_shift != 0:
        values_array = np.roll(values_array, x_shift, axis=1)
    
    if is_inverted:
        values_array = np.flipud(values_array)

    values_array = values_array.astype(np.float32)
    img = Image.fromarray(values_array, mode='F')
    if not os.path.exists(output.rsplit('/', 1)[0]):
        os.makedirs(output.rsplit('/', 1)[0])
    img.save(output, format='TIFF')
    img.save(output + '.webp', format='WEBP')
    return values_array

def resize(path, output, size):
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(path)
    im = im.resize(size, Image.NEAREST)
    im.save(output, format='TIFF')
    im.save(output + '.webp', format='WEBP')