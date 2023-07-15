from PIL import Image
import os
import numpy as np


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
                mapped = [int(a * (map_point(t) + b)) for t in ts]
                if len(images) == 1:
                    pixels[x, y] = mapped[0]
                else:
                    pixels[x, y] = (mapped[0], mapped[1], mapped[2])
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


    # min_value = 100000
    # max_value = -100000
    # for path in paths:
    #     im = load(path, resize)
    #     for x in range(im.size[0]):
    #         for y in range(im.size[1]):
    #             t = im.getpixel((x, y))
    #             if t != invalid_value:
    #                 min_value = min(min_value, map_point(t))
    #                 max_value = max(max_value, map_point(t))
    # return (min_value, max_value)

def to_tif(values, output, map_point=lambda x: x, is_inverted=False):
    img = Image.new('F', (len(values[0]), len(values)), color='black')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if is_inverted:
                pixels[x, img.size[1] - y - 1] = map_point(values[y][x])
            else:
                pixels[x, y] = map_point(values[y][x])
    if not os.path.exists(output.rsplit('/', 1)[0]):
        os.makedirs(output.rsplit('/', 1)[0])
    img.save(output, format='TIFF')

def resize(path, output, size):
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(path)
    im = im.resize(size, Image.NEAREST)
    im.save(output, format='TIFF')