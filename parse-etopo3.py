import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask
from scripts import resize

# Input GeoTIFF path
surface_path = "source/etopo/ETOPO_2022_v1_60s_N90W180_surface.tif"
geoid_path = "source/etopo/ETOPO_2022_v1_60s_N90W180_geoid.tif"
shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"
include_islands = True
output_adjusted_surface_path = "images/dem-etopo.tif"
output_tif_path = "images/dem-land-etopo.tif"
output_size = (576, 361)

######## Program, don't modify ########

# Read the shapefile using geopandas
gdf = gpd.read_file(shapefile_path)
gdf_islands = gpd.read_file(island_shapefile_path)

# Add geoid to surface
with rasterio.open(geoid_path) as geoids:
    geoids = geoids.read(1)
    with rasterio.open(surface_path) as src:
        surface = src.read(1)
        surface += geoids
        
        # Save the new surface
        metadata = src.profile
        metadata.update(count=1)
        with rasterio.open(output_adjusted_surface_path, 'w', **metadata) as dst:
            dst.write(surface, 1)


# Open the GeoTIFF file
with rasterio.open(output_adjusted_surface_path) as src:
    gdf = gdf.to_crs(src.crs)
    if include_islands:
        gdf_islands = gdf_islands.to_crs(src.crs)
        gdf = gpd.GeoDataFrame(pd.concat([gdf, gdf_islands], ignore_index=True), crs=src.crs)

    masked_image, masked_transform = mask(src, gdf.geometry)
    metadata = src.meta.copy()
    metadata.update({"driver": "GTiff",
                     "height": masked_image.shape[1],
                     "width": masked_image.shape[2],
                     "transform": masked_transform,
                     "crs": src.crs})
    # Create a new GeoTIFF file and write the masked image
    with rasterio.open(output_tif_path, 'w', **metadata) as dst:
        dst.write(masked_image)

# # Resize the images
if output_size is not None:
    resize(output_adjusted_surface_path, output_adjusted_surface_path, output_size)
    resize(output_tif_path, output_tif_path, output_size)