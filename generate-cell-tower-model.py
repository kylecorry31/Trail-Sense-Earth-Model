from scripts import opencellid, compression, load_pixels, fcc
from scripts.operators import process
from scripts.operators.basic import Tile, Save, BitwiseOr
import os
import shutil
from PIL import Image
import numpy as np

resolution = 0.02

fcc.download()
fcc.process_towers(resolution)

opencellid.download()
opencellid.process_towers(resolution)

Image.MAX_IMAGE_PIXELS = None

fcc_image = load_pixels('images/fcc/cell_towers.tif').astype(np.uint8)
openceillid_image = load_pixels('images/opencellid/cell_towers.tif').astype(np.uint8)
shutil.rmtree('images/cell_towers_processed/towers', ignore_errors=True)
os.makedirs('images/cell_towers_processed/towers', exist_ok=True)

shutil.rmtree('output/towers', ignore_errors=True)
os.makedirs('output/towers', exist_ok=True)

process(
    [fcc_image, openceillid_image],
    BitwiseOr(),
    Tile((4500, 9000)),
    Save(lambda x: f'images/cell_towers_processed/towers/cell_towers_{x}.tif', mode='F')
)

paths = [f'images/cell_towers_processed/towers/{path}' for path in os.listdir('images/cell_towers_processed/towers')]

for path in paths:
    compression.minify(path, lambda x: x, -99999, path.replace('images/cell_towers_processed/towers/', 'output/towers/').replace('.tif', '.webp'), 100, True, a_override=1, b_override=0)
