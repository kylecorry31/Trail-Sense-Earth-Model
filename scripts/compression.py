from . import get_min_max, compress_to_webp2, load_pixels, to_tif
from .progress import progress
from PIL import Image
import numpy as np
import pyshtools

# Pixel = a * value + b
# Value = (pixel - b) / a

def scale(value, a, b):
    return np.round(a * (value + b))

def unscale(value, a, b):
    return value / a - b

def spherical_harmonics(file, map_point, invalid_value, resolution_meters, reconstructed_output_filename=None, should_scale=False):
    Image.MAX_IMAGE_PIXELS = None
    pixels = map_point(load_pixels(file))
    pixels[pixels == invalid_value] = 0

    R = 6371200
    min_order = (-1 + np.sqrt(1 + 4 * np.square(2 * np.pi * R / resolution_meters))) / 2
    lmax = min(int(np.ceil(min_order)), 359)

    

    grid = pyshtools.SHGrid.from_array(pixels)

    clm = grid.expand(normalization='schmidt', lmax_calc=lmax)

    g = clm.coeffs[0]
    h = clm.coeffs[1]
    minimum = np.inf
    maximum = -np.inf

    new_g = []
    new_h = []
    i = 0

    while i <= lmax:
        j = 0
        new_g.append([])
        new_h.append([])
        while j <= i:
            new_g[-1].append(g[i][j])
            new_h[-1].append(h[i][j])
            minimum = min(minimum, min(g[i][j], h[i][j]))
            maximum = max(maximum, max(g[i][j], h[i][j]))
            j += 1
        i += 1

    b = -minimum
    a = 255 / (maximum + b)

    if should_scale:
        print(f'A = {a}, B = {b}')
        for row in new_g:
            for i in range(len(row)):
                row[i] = scale(row[i], a, b)
        for row in new_h:
            for i in range(len(row)):
                row[i] = scale(row[i], a, b)
    
    if reconstructed_output_filename:
        # Convert it back to an image and write to disk
        trunc_clm = pyshtools.SHCoeffs.from_array(np.array([g, h]), normalization='schmidt')

        # Scale and unscale to match the compressed model'
        if should_scale:
            for n in range(lmax + 1):
                for m in range(n + 1):
                    trunc_clm.coeffs[0, n, m] = unscale(scale(trunc_clm.coeffs[0, n, m], a, b), a, b)
                    trunc_clm.coeffs[1, n, m] = unscale(scale(trunc_clm.coeffs[1, n, m], a, b), a, b)

        # Reconstruct the grid from the truncated coefficients
        trunc_grid = trunc_clm.expand(grid='DH2')

        # Convert back to numpy array for saving
        reconstructed_array = trunc_grid.to_array()
        reconstructed_array_norm = reconstructed_array - np.min(reconstructed_array)
        reconstructed_array_norm /= np.max(reconstructed_array_norm)
        reconstructed_array_uint8 = (reconstructed_array_norm * 255).astype(np.uint8)

        # Save as image
        img = Image.fromarray(reconstructed_array_uint8)
        img.save(reconstructed_output_filename)
    
    return {
        'g': new_g,
        'h': new_h
    }


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

def __create_condensed_image(image, valid_indices, final_width=250):
    updated = image[valid_indices]
    total_values = len(updated)
    updated = np.append(updated, np.zeros(final_width - (total_values % final_width)))
    updated = updated.reshape((-1, final_width))
    return updated

def index(image, ignored_value, final_width):
    non_zero_bool_array = image != ignored_value
    indices_x = np.zeros(image.shape)
    indices_y = np.zeros(image.shape)
    non_zero_indices = np.argwhere(non_zero_bool_array)
    for i in range(len(non_zero_indices)):
        source_x = non_zero_indices[i][1]
        source_y = non_zero_indices[i][0]
        destination_x = i % final_width + 1
        destination_y = i // final_width + 1
        indices_x[source_y, source_x] = destination_x
        indices_y[source_y, source_x] = destination_y
    return indices_x, indices_y, lambda i: __create_condensed_image(i, non_zero_bool_array, final_width), non_zero_bool_array

def normalize(image, minimum, maximum, ignored_value = None):
    if minimum is None:
        minimum = np.min(image[image != ignored_value]) if ignored_value is not None else np.min(image)
    if maximum is None:
        maximum = np.max(image[image != ignored_value]) if ignored_value is not None else np.max(image)

    if ignored_value is None:
        return (image - minimum) / (maximum - minimum), minimum, maximum
    normalized = (image[image != ignored_value] - minimum) / (maximum - minimum)
    normalized[normalized < 0] = 0
    result = image.copy()
    result[result != ignored_value] = normalized
    return result, minimum, maximum

def extract_large_values(image, threshold, replacement = 0, ignored_value = None):
    large_values = []
    result = image.copy()
    large_amplitude_indices = np.argwhere((image > threshold) & (image != ignored_value))
    for idx in large_amplitude_indices:
        large_values.append((int(idx[0]), int(idx[1]), image[idx[0], idx[1]]))
        if replacement is not None:
            result[idx[0], idx[1]] = replacement
    return result, large_values