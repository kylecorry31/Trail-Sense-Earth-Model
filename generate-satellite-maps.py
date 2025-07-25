from scripts import visible_earth, natural_earth, clip, progress
import PIL.Image as Image
import numpy as np

visible_earth.download()
visible_earth.process_maps(0)

reference = Image.open("images/world-map-7.tif")
# Remove water
reference = np.array(reference)
reference = natural_earth.remove_oceans(reference, scale=2, dilation=0)
reference = natural_earth.remove_inland_water(reference, scale=2, dilation=0)
reference = Image.fromarray(reference)

images = []
with progress.progress('Processing world map', 6) as pbar:
    for month in range(4, 10):
        image = Image.open(f"images/world-map-{month}.tif")

        # Remove water
        image = np.array(image)
        image = natural_earth.remove_oceans(image, scale=2, dilation=0)
        image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
        image = Image.fromarray(image)

        # Simplify colors
        # TODO: Color based on climate zone instead or paint by hand
        image = visible_earth.__simplify(reference, image, 8, 4, 4, format="RGB")
        image.thumbnail((3600, 3600), resample=Image.NEAREST)

        # Reapply water removal
        image = np.array(image)
        image = natural_earth.remove_oceans(image, scale=2, dilation=0)
        image = natural_earth.remove_inland_water(image, scale=2, dilation=0)
        image = Image.fromarray(image)

        images.append(image)
        pbar.update(1)

image = np.median(np.array(images), axis=0).astype(np.uint8)
image = Image.fromarray(image)

image.save("output/world-map.webp", quality=100, lossless=True, format='WEBP', method=6, alpha_quality=0, optimize=True, compress_level=9)
