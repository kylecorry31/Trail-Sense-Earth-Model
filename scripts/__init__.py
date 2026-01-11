from PIL import Image
import os
import numpy as np


def load_pixels(path, resize=None):
    im = Image.open(path)
    if resize is not None and im.size != resize:
        im = im.resize(resize, Image.NEAREST)
    return np.array(im)


def __flip_vertical(image):
    return np.flipud(image)


def __shift_x(image, x_shift):
    return np.roll(image, x_shift, axis=1)


def __replace_invalid(image, replacement=0):
    values_array = np.ma.masked_invalid(image)
    values_array = np.where(values_array.mask, replacement, values_array)
    return values_array


def to_tif(
    values,
    output=None,
    is_inverted=False,
    x_shift=0,
    masked_value_replacement=0,
    generate_webp=False,
):
    values_array = __replace_invalid(values, masked_value_replacement)

    if x_shift != 0:
        values_array = __shift_x(values_array, x_shift)

    if is_inverted:
        values_array = __flip_vertical(values_array)

    values_array = values_array.astype(np.float32)
    img = Image.fromarray(values_array, mode="F")
    if output is not None:
        if not os.path.exists(output.rsplit("/", 1)[0]):
            os.makedirs(output.rsplit("/", 1)[0])
        img.save(output, format="TIFF", compression="tiff_lzw")
        if generate_webp:
            # Scale values from min/max to 0-255 for WebP
            min_val = np.min(values_array)
            max_val = np.max(values_array)
            if max_val > min_val:
                scaled_values = (
                    (values_array - min_val) / (max_val - min_val) * 255
                ).astype(np.uint8)
            else:
                scaled_values = np.zeros_like(values_array, dtype=np.uint8)
            scaled_img = Image.fromarray(scaled_values, mode="L")
            scaled_img.thumbnail((4000, 4000))
            scaled_img.save(output + ".webp", format="WEBP")
    return values_array
