from scripts import opencellid, compression, load_pixels, fcc, mls, cell_towers
from scripts.operators import process
from scripts.operators.basic import Tile, Save, BitwiseOr
import os
import shutil
from PIL import Image
import numpy as np
from scripts.operators.masking import RemoveOceans

resolution = 0.01

def get_tile_size(width, height, max_width, max_height):
    dividers = [5, 4, 3, 2, 1]
    new_width = width
    new_height = height
    for divider in dividers:
        if width % divider == 0 and width // divider < max_width:
            new_width = width // divider
        if height % divider == 0 and height // divider < max_height:
            new_height = height // divider
    return new_width, new_height


fcc.download()
opencellid.download()
# TODO: MLS will likely only be valid for a few more years
mls.download()

fcc.process_towers(resolution)
towers = cell_towers.get_all_towers(opencellid.csv_path, 'OpenCellID')
towers = cell_towers.get_all_towers(mls.csv_path, 'MLS', towers)
cell_towers.create_tower_image(towers, resolution, 'images/cell_towers')

Image.MAX_IMAGE_PIXELS = None

fcc_image = load_pixels('images/fcc/cell_towers.tif').astype(np.uint8)
cell_towers_image = load_pixels('images/cell_towers/cell_towers.tif').astype(np.uint8)

total_width = fcc_image.shape[1]
total_height = fcc_image.shape[0]
max_width = 12000
max_height = 9000

tile_width, tile_height = get_tile_size(total_width, total_height, max_width, max_height)
print(f'Tiling into {tile_width}x{tile_height} tiles')
print(f'Rows: {total_height // tile_height}, Columns: {total_width // tile_width}')

shutil.rmtree('images/cell_towers_processed/towers', ignore_errors=True)
os.makedirs('images/cell_towers_processed/towers', exist_ok=True)

shutil.rmtree('output/towers', ignore_errors=True)
os.makedirs('output/towers', exist_ok=True)

process(
    [fcc_image, cell_towers_image],
    BitwiseOr(),
    RemoveOceans(dilation=0, scale=1),
    Tile((tile_height, tile_width)),
    Save(lambda x: f'images/cell_towers_processed/towers/cell_towers_{x}.tif', mode='F')
)

paths = [f'images/cell_towers_processed/towers/{path}' for path in os.listdir('images/cell_towers_processed/towers')]

for path in paths:
    compression.minify(path, lambda x: x, -99999, path.replace('images/cell_towers_processed/towers/', 'output/towers/').replace('.tif', '.webp'), 100, True, a_override=1, b_override=0)

shutil.rmtree('images/cell_towers_processed', ignore_errors=True)
