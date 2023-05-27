import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from rasterio.features import rasterize
import numpy as np


shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"
include_islands = True
resolution = 0.01

def add_to_image(image, shapefile_path):
    gdf = gpd.read_file(shapefile_path)
    rasterize([(geom, 255) for geom in gdf.geometry], out=image, transform=transform)


output_tif_path = "images/land-ne.tif"

xmin, ymin, xmax, ymax = -180, -90, 180, 90

width = int((xmax - xmin) / resolution)
height = int((ymax - ymin) / resolution)

transform = from_bounds(xmin, ymin, xmax, ymax, width, height)
image = np.zeros((height, width), dtype=np.uint8)
add_to_image(image, shapefile_path)
if include_islands:
    add_to_image(image, island_shapefile_path)

with rasterio.open(output_tif_path, 'w', driver='GTiff', height=height, width=width, count=1, dtype=rasterio.uint8,
                   crs='EPSG:4326', transform=transform) as dst:
    dst.write(image, 1)
