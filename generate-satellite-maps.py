from scripts import visible_earth, natural_earth, compression, progress, load_pixels
import PIL.Image as Image
import numpy as np

visible_earth.download()
visible_earth.process_maps(0)

# Create an 8x1 image with custom colors that I can use as the reference
colors = [
    (200, 200, 200),  # Ice
    (80, 100, 60),    # Grass
    (50, 70, 30),     # Forests
    (30, 50, 10),     # Rainforests
    (190, 160, 120),  # Desert
    (160, 120, 80),   # Desert 2
    (110, 80, 50),   # Red sand
]

reference = Image.new("RGB", (len(colors), 1), (0, 0, 0))
for i in range(len(colors)):
    reference.putpixel((i, 0), colors[i])

images = []
with progress.progress('Processing world map', 4) as pbar:
    for month in range(6, 10):
        image = load_pixels(f"images/world-map-{month}.tif")
        images.append(image)
        pbar.update(1)

image = np.median(np.array(images), axis=0).astype(np.uint8)
image = Image.fromarray(image)

# Simplify colors
image = compression.restrict_palette(image, reference, 2, 8, format="HSV")

# Remove water
image = np.array(image)
image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)

# Resize
image = Image.fromarray(image)
image.thumbnail((4200, 4200), resample=Image.NEAREST)

image.save("output/world-map.webp", quality=100, lossless=True, format='WEBP', method=6, alpha_quality=0, optimize=True, compress_level=9)
