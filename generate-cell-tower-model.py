from scripts import opencellid, fcc, mls, cell_towers
import os
import shutil
import numpy as np

######## Program, don't modify ########
fcc.download()
opencellid.download()
# TODO: MLS will likely only be valid for a few more years
mls.download()

fcc_locations = np.array(fcc.get_tower_locations())
records = cell_towers.get_all_towers(opencellid.csv_path, "OpenCellID")
records = cell_towers.get_all_towers(mls.csv_path, "MLS", records)

shutil.rmtree("output/towers", ignore_errors=True)

tower_latitudes, tower_longitudes = cell_towers.select_towers(records)
latitudes = np.r_[fcc_locations[:, 0], tower_latitudes]
longitudes = np.r_[fcc_locations[:, 1], tower_longitudes]
points = cell_towers.create_tower_points(latitudes, longitudes)
os.makedirs("output/towers", exist_ok=True)
with open(f"output/towers/{cell_towers.FILENAME}", "wb") as f:
    f.write(points)
print(f"Saved {len(points) / 1000:.0f} KB of towers")
