from . import get_min_max, compress_to_webp2, load_pixels, to_tif
from .progress import progress
from PIL import Image
import numpy as np
import pyshtools
from scipy.ndimage import binary_closing
from skimage.morphology import erosion, dilation, remove_small_holes
from skimage import measure

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
        with progress(f'Calculating compression offset ({data_point})', 1, disable=not should_print) as pbar:
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
    
    with progress(f'Compressing ({data_point})', len(files), disable=not should_print) as pbar:
        for i in range(0, len(files), grouping):
            compress_to_webp2(files[i:i+grouping], f'output/{data_point}-{i + 1}-{i + grouping}.webp', map_point, a, b, invalid_value, quality, lossless, size)
            pbar.update(grouping)
    
    return float(a), float(b)

def minify(path, map_point, invalid_value, output_filename, quality, lossless, size=None, a_override=None, b_override=None, should_print=True):
    Image.MAX_IMAGE_PIXELS = None
    if a_override is not None and b_override is not None:
        a = a_override
        b = b_override
    else:
        with progress('Calculating compression offset', 1, disable=not should_print) as pbar:
            offset = get_min_max([path], map_point, invalid_value)
            pbar.update(1)

        b = -offset[0]
        # Map to 0-255 after subtracting the offset
        a = 255 / (offset[1] + b)
        if np.isinf(a):
            a = 1

    if should_print:
        print(f'A: {a}, B: {b}')
    
    with progress('Compressing', 1, disable=not should_print) as pbar:
        compress_to_webp2([path], output_filename, map_point, a, b, invalid_value, quality, lossless, size)
        pbar.update(1)
    
    return (a, b)

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

def restrict_palette(image, palette_image, smoothing_structure=3, smoothing_iterations=2, format="HSV", ignored_closing_colors=[]):
    # If palette image is an array, construct the image
    if isinstance(palette_image, list) or isinstance(palette_image, np.ndarray):
        reference = Image.new("RGB", (len(palette_image), 1), (0, 0, 0))
        for i in range(len(palette_image)):
            reference.putpixel((i, 0), palette_image[i])
        palette_image = reference

    # TODO: Add option to auto detect palette
    # Get unique colors from reference image
    converted_palette_image = palette_image.convert(format)
    palette_pixels = np.array(converted_palette_image)
    palette_pixels_reshaped = palette_pixels.reshape(-1, 3)
    palette = np.unique(palette_pixels_reshaped, axis=0)

    target_image = image.convert(format)
    target_pixels = np.array(target_image)
    original_shape = target_pixels.shape
    target_pixels_reshaped = target_pixels.reshape(-1, 3)

    # Find closest color for each pixel in the target image
    distances = np.linalg.norm(target_pixels_reshaped[:, np.newaxis].astype(np.int16) - palette[np.newaxis, :].astype(np.int16), axis=2)
    closest_indices = np.argmin(distances, axis=1)
    
    # Replace with closest colors
    compressed_pixels = palette[closest_indices]
    compressed_pixels = compressed_pixels.reshape(original_shape)

    # Close small holes for each color
    for i in range(len(palette)):
        if tuple(palette[i]) in ignored_closing_colors:
            continue
        mask = (compressed_pixels == palette[i]).all(axis=-1)
        closed_mask = binary_closing(mask, structure=np.ones((smoothing_structure, smoothing_structure)), iterations=smoothing_iterations)
        compressed_pixels[closed_mask] = palette[i]

    # Convert the image back to RGB
    compressed_image = Image.fromarray(compressed_pixels, format).convert("RGB")

    return compressed_image

def disk_structure(size):
    y, x = np.ogrid[:size, :size]
    center = size // 2
    mask = (x - center) ** 2 + (y - center) ** 2 <= center ** 2
    return mask.astype(np.uint8)

def smooth_color(image, color, smoothing_structure=None, smoothing_iterations=2, min_hole_size=None):
    distances = np.linalg.norm(image.astype(np.int16) - np.array(color).astype(np.int16), axis=-1)
    mask = distances <= 4
    for _ in range(smoothing_iterations):
        mask = dilation(mask, footprint=smoothing_structure)
    for _ in range(smoothing_iterations):
        mask = erosion(mask, footprint=smoothing_structure)
    if min_hole_size is not None:
        mask = remove_small_holes(mask, max_size=min_hole_size)
    image[mask] = color
    return image

def grow_color(image, color, structure=None, iterations=1):
    distances = np.linalg.norm(image.astype(np.int16) - np.array(color).astype(np.int16), axis=-1)
    mask = distances <= 4
    for _ in range(iterations):
        mask = dilation(mask, footprint=structure)
    image[mask] = color
    return image

def remove_small_regions(image, color, max_size=10, invalid_colors=None, default_fill=None, search_space=2):
    distances = np.linalg.norm(image.astype(np.int16) - np.array(color).astype(np.int16), axis=-1)
    mask = distances <= 4

    # Label connected components
    labeled = measure.label(mask)
    props = sorted(measure.regionprops(labeled), key=lambda r: r.area, reverse=True)

    cleaned = image.copy()

    for region in props:
        if region.area <= max_size:
            # Get coordinates of the small region
            coords = region.coords
            
            # Find the most common neighboring color for the entire region
            all_neighbors = []
            for coord in coords:
                y, x = coord
                # Search eighborhood for non-region pixels
                neighbors = image[max(0, y-(search_space - 1)):y+search_space, max(0, x-(search_space-1)):x+search_space]
                neighbors_mask = labeled[max(0, y-(search_space - 1)):y+search_space, max(0, x-(search_space-1)):x+search_space] != region.label
                valid_neighbors = neighbors[neighbors_mask]
                
                if len(valid_neighbors) > 0:
                    if invalid_colors is None:
                        all_neighbors.extend(valid_neighbors)
                    else:
                        invalid_colors_array = np.array(invalid_colors)
                        valid_mask = ~np.any(np.all(valid_neighbors[:, None] == invalid_colors_array[None, :], axis=-1), axis=1)
                        all_neighbors.extend(valid_neighbors[valid_mask])

            
            if len(all_neighbors) > 0:
                # Find the most frequent neighbor color across all boundary pixels
                all_neighbors = np.array(all_neighbors)
                unique_colors, counts = np.unique(all_neighbors.reshape(-1, 3), axis=0, return_counts=True)
                most_frequent_idx = np.argmax(counts)
                replacement_color = unique_colors[most_frequent_idx]
            else:
                replacement_color = default_fill if default_fill is not None else color
            
            # Fill the entire region with the same color
            for coord in coords:
                y, x = coord
                cleaned[y, x] = replacement_color
    
    return cleaned
