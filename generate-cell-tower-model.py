from scripts import opencellid, compression, load_pixels
from scripts.operators import process
from scripts.operators.basic import Tile, Save
import numpy as np
import os
import shutil
from PIL import Image

opencellid.download()
opencellid.process_towers(0.015)

Image.MAX_IMAGE_PIXELS = None

image = load_pixels('images/opencellid/cell_towers.tif')
shutil.rmtree('images/opencellid/towers', ignore_errors=True)
os.makedirs('images/opencellid/towers', exist_ok=True)

shutil.rmtree('output/towers', ignore_errors=True)
os.makedirs('output/towers', exist_ok=True)

process(
    [image],
    Tile((6000, 12000)),
    Save(lambda x: f'images/opencellid/towers/cell_towers_{x}.tif', mode='F')
)

paths = [f'images/opencellid/towers/{path}' for path in os.listdir('images/opencellid/towers')]

for path in paths:
    compression.minify(path, lambda x: x, -99999, path.replace('images/opencellid/towers/', 'output/towers/').replace('.tif', '.webp'), 100, True, a_override=1, b_override=0)
