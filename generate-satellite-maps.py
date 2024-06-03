from scripts import visible_earth
import PIL.Image as Image

visible_earth.download()
visible_earth.process_maps(0)

for i in range(1, 13):
    image = Image.open(f"images/world-map-{i}.tif")
    image.thumbnail((3600, 3600))
    image.save(f"output/world-map-{i}.webp", quality=75, lossless=False, format='WEBP')
