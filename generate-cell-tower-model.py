from scripts import opencellid, fcc, mls, cell_towers
import os
import shutil
import numpy as np

######## Program, don't modify ########
fcc.download()
opencellid.download()
# TODO: MLS will likely only be valid for a few more years
mls.download()

fcc_locations = fcc.get_tower_locations()
towers = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
towers = cell_towers.get_all_towers(mls.csv_path, "MLS", towers)

shutil.rmtree("output/towers", ignore_errors=True)

latitudes = [lat for lat, _ in fcc_locations] + [row.latitude for row in towers.values()]
longitudes = [lon for _, lon in fcc_locations] + [row.longitude for row in towers.values()]
points = cell_towers.create_tower_points(np.array(latitudes), np.array(longitudes))
os.makedirs("output/towers", exist_ok=True)
with open(f"output/towers/{cell_towers.FILENAME}", "wb") as f:
    f.write(points)
print(f"Saved {len(points) / 1000:.0f} KB of towers")
