from scripts import opencellid, fcc, mls, cell_towers, cell_tower_index
from scripts.operators import process, Save
import numpy as np

# INPUT
# The cells are 1 / cells_per_degree degrees wide (a smaller cell is more accurate and larger)
cells_per_degree = 192

fcc.download()
opencellid.download()
# TODO: MLS will likely only be valid for a few more years
mls.download()

######## Program, don't modify ########
towers = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
towers = cell_towers.get_all_towers(mls.csv_path, "MLS", towers)
locations = np.array(cell_towers.get_locations(towers) + fcc.get_towers())
locations = locations[(np.abs(locations[:, 0]) <= 90) & (np.abs(locations[:, 1]) <= 180)]

rows, columns = cell_tower_index.to_cells(locations[:, 0], locations[:, 1], cells_per_degree)
data = cell_tower_index.encode(rows, columns, cells_per_degree)

image = cell_tower_index.to_image(data)
process([image], Save(["output/cell_towers.webp"], quality=100, lossless=True))
print(f"{len(locations)} towers in {len(rows)} cells, image size (width, height): {image.shape[::-1]}")
