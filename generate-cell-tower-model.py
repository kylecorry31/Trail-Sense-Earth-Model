from scripts import opencellid, fcc, mls, cell_towers
from scripts.operators import process, Tile, Save, BitwiseOr, Type, RemoveOceans
import shutil
import numpy as np

# INPUT
# The size of a pixel (degrees)
resolution = 0.01
# The size of the tiles (pixels)
max_width = 12000
max_height = 9000

######## Program, don't modify ########
fcc.download()
opencellid.download()
# TODO: MLS will likely only be valid for a few more years
mls.download()

fcc.process_towers(resolution)
towers = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
towers = cell_towers.get_all_towers(mls.csv_path, "MLS", towers)
cell_towers.create_tower_image(towers, resolution, "images/cell_towers")

shutil.rmtree("output/towers", ignore_errors=True)

_, results = process(
    ["images/fcc/cell_towers.tif", "images/cell_towers/cell_towers.tif"],
    Type(np.uint8),
    BitwiseOr(),
    RemoveOceans(dilation=0, scale=1),
    Tile((max_height, max_width), max_dimensions=True),
    Save(lambda x: f"output/towers/cell_towers_{x}.webp", quality=100, lossless=True),
    show_progress=True
)

print(results.of(Tile)['tiles'][0])
