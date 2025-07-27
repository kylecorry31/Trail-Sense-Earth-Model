from scripts import visible_earth, natural_earth, compression, progress, load_pixels
import PIL.Image as Image
import numpy as np

visible_earth.download()
visible_earth.process_maps()

colors = [
    (0, 0, 0),  # Water
    (200, 200, 200),  # Ice
    (50, 70, 30),     # Forests
    (160, 120, 80),  # Desert
]

images = []
with progress.progress('Loading world map', 12) as pbar:
    for month in range(1, 13):
        image = load_pixels(f"images/world-map-{month}.tif")
        images.append(image)
        pbar.update(1)

with progress.progress('Processing world map', 7) as pbar:
    image = np.min(np.array(images), axis=0).astype(np.uint8)
    image = natural_earth.remove_oceans(image, scale=2, dilation=0)
    image = natural_earth.remove_inland_water(image, scale=2, dilation=0)

    # Desert
    new_image = np.full_like(image, (180, 135, 90))
    pbar.update(1)

    # Forests (green is a large component, but overall not that bright)
    mask = (np.mean(image, axis=-1) < 100) & (image[..., 1] > image[..., 0] * 0.9)
    new_image[mask] = (50, 70, 30)
    pbar.update(1)

    # Rainforests
    mask = (mask) & (image[..., 1] < 40) & (image[..., 2] < 10) & (image[..., 0] < 30)
    new_image[mask] = (30, 50, 20)
    pbar.update(1)

    # # Arid
    # mask = (image[..., 0] > image[..., 1]) & (image[..., 0] > image[..., 2] * 1.2) & (np.mean(image, axis=-1) < 90)
    # new_image[mask] = (120, 100, 70)

    # Red sand
    mask = (image[..., 0] > image[..., 1] * 1.4) & (image[..., 0] > image[..., 2] * 1.4)
    new_image[mask] = (130, 80, 40)
    pbar.update(1)

    # Ice (r, g, b above threshold)
    threshold = 150
    mask = np.all(image >= threshold, axis=-1)
    new_image[mask] = (200, 200, 200)
    pbar.update(1)

    # Fill all pixels below -60 lat or above 72 lat with white
    north = 72
    south = -60
    height = image.shape[0]
    north_pixel = max(0, min(height, int((90 - north) / 180
        * height)))
    south_pixel = max(0, min(height, int((90 - south) / 180 * height)))
    new_image[:north_pixel, :] = (200, 200, 200)
    new_image[south_pixel:, :] = (200, 200, 200)
    pbar.update(1)

    image = new_image

    image = natural_earth.remove_oceans(image, scale=2, dilation=0)
    image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
    pbar.update(1)

smoothing_order = [
    (200, 200, 200),  # Ice
    (30, 50, 20),     # Rainforests
    (50, 70, 30),     # Forests
    (130, 80, 40),    # Red sand
    (180, 135, 90),   # Desert
]

image_area = np.prod(mask.shape)
min_hole_size = image_area * 0.007
smoothing_iterations = 5

with progress.progress('Smoothing world map', len(smoothing_order) * 4) as pbar:
    for color in smoothing_order:
        image = compression.smooth_color(image, color, smoothing_structure=None, smoothing_iterations=smoothing_iterations, min_hole_size=min_hole_size)
        pbar.update(1)

    for color in reversed(smoothing_order):
        image = compression.smooth_color(image, color, smoothing_structure=None, smoothing_iterations=smoothing_iterations, min_hole_size=min_hole_size)
        pbar.update(1)

    # Fill noise
    for color in smoothing_order:
        image = compression.remove_small_regions(image, color, 60, invalid_colors=[(0, 0, 0)], search_space=30)
        pbar.update(1)

    # Grow all colors for extra noise reduction
    for color in smoothing_order:
        image = compression.grow_color(image, color, structure=np.ones((3, 3)), iterations=8)
        pbar.update(1)

# Remove water
image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)

# Resize
image = Image.fromarray(image)
image.thumbnail((3800, 3800), resample=Image.NEAREST)

image.save("output/world-map.webp", quality=100, lossless=True,
           format='WEBP', method=6, alpha_quality=0, optimize=True, compress_level=9)
