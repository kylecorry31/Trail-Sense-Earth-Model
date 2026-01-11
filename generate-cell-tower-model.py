from scripts import opencellid, load_pixels, fcc, mls, cell_towers
from scripts.operators import process
from scripts.operators.basic import Tile, Save, BitwiseOr, Type
import os
import shutil
from PIL import Image
import numpy as np
from scripts.operators.masking import RemoveOceans

resolution = 0.01


fcc.download()
opencellid.download()
# TODO: MLS will likely only be valid for a few more years
mls.download()

fcc.process_towers(resolution)
towers = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
towers = cell_towers.get_all_towers(mls.csv_path, "MLS", towers)
cell_towers.create_tower_image(towers, resolution, "images/cell_towers")

max_width = 12000
max_height = 9000

shutil.rmtree("output/towers", ignore_errors=True)

tile_operator_index = 3

_, metadata = process(
    ["images/fcc/cell_towers.tif", "images/cell_towers/cell_towers.tif"],
    Type(np.uint8),
    BitwiseOr(),
    RemoveOceans(dilation=0, scale=1),
    Tile((max_height, max_width), max_dimensions=True),
    Save(lambda x: f"output/towers/cell_towers_{x}.webp", quality=100, lossless=True),
    show_progress=True
)

print(metadata[tile_operator_index]['tiles'][0])
