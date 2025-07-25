from scripts import visible_earth, natural_earth, compression, progress, load_pixels
import PIL.Image as Image
import numpy as np

visible_earth.download()
visible_earth.process_maps()

colors = [
    (0, 0, 0),  # Water
    (127, 127, 127), # Rock
    (200, 200, 200),  # Ice
    (50, 70, 30),     # Forests
    (160, 120, 80),  # Desert
]

images = []
with progress.progress('Processing world map', 12) as pbar:
    for month in range(1, 13):
        image = load_pixels(f"images/world-map-{month}.tif")
        images.append(image)
        pbar.update(1)

image = np.min(np.array(images), axis=0).astype(np.uint8)
image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)

# Desert
new_image = np.full_like(image, (160, 120, 80))

# Forests (green is a large component, but overall not that bright)
mask = (np.mean(image, axis=-1) < 100) & (image[..., 1] > image[..., 0] * 0.9)
new_image[mask] = (50, 70, 30)

# Rock (red = green = blue)
red_equal = np.isclose(image[..., 0], image[..., 1], atol=10)
green_equal = np.isclose(image[..., 1], image[..., 2], atol=10)
mask = red_equal & green_equal
new_image[mask] = (127, 127, 127)

# Ice (r, g, b above threshold)
threshold = 170
mask = np.all(image >= threshold, axis=-1)
new_image[mask] = (200, 200, 200)

image = new_image

image = Image.fromarray(image)

# Simplify colors
image = compression.restrict_palette(image, colors, smoothing_structure=2, smoothing_iterations=10, format="RGB", ignored_closing_colors=[(0, 0, 0)])
image = np.array(image)

# Remove water
image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)

# Resize
image = Image.fromarray(image)
image.thumbnail((4200, 4200), resample=Image.NEAREST)

image.save("output/world-map.webp", quality=100, lossless=True,
           format='WEBP', method=6, alpha_quality=0, optimize=True, compress_level=9)
