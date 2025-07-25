from scripts import visible_earth, natural_earth, clip, progress
import PIL.Image as Image
import numpy as np

visible_earth.download()
visible_earth.process_maps(0)

# Create an 8x1 image with custom colors that I can use as the reference
reference = Image.new("RGB", (8, 1), (0, 0, 0))
reference.putpixel((0, 0), (200, 200, 200))
reference.putpixel((1, 0), (0, 0, 0))
reference.putpixel((2, 0), (50, 70, 30))   # Forests
reference.putpixel((3, 0), (30, 50, 10))    # Rainforests
reference.putpixel((4, 0), (190, 160, 120)) # Desert
reference.putpixel((5, 0), (160, 120, 80))   # Desert 2
reference.putpixel((6, 0), (110, 65, 35)) # Red sand
reference.putpixel((7, 0), (80, 70, 40))  # Alpine

# Scale reference image to 100x100 (nearest)
reference = reference.resize((100, 1), resample=Image.NEAREST)

images = []
with progress.progress('Processing world map', 4) as pbar:
    for month in range(6, 10):
        image = Image.open(f"images/world-map-{month}.tif")

        # Remove water
        image = np.array(image)
        image = natural_earth.remove_oceans(image, scale=2, dilation=0)
        image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
        image = Image.fromarray(image)

        images.append(image)
        pbar.update(1)

image = np.median(np.array(images), axis=0).astype(np.uint8)
image = Image.fromarray(image)

# Simplify colors
image = visible_earth.__simplify(reference, image, 8, 2, 10, format="RGB")
image.thumbnail((4200, 4200), resample=Image.NEAREST)

# Reapply water removal
image = np.array(image)
image = natural_earth.remove_oceans(image, scale=2, dilation=0)
image = natural_earth.remove_inland_water(image, scale=2, dilation=0)

# TODO: Replace certain colors near the poles - only white, brown, gray

# image = clip.clip_uninhabitable_areas(image)

image = Image.fromarray(image)
image.save("output/world-map.webp", quality=100, lossless=True, format='WEBP', method=6, alpha_quality=0, optimize=True, compress_level=9)
