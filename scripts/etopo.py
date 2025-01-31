from .progress import progress
import os
import requests
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask

shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"
surface_path = "source/etopo/ETOPO_2022_v1_60s_N90W180_surface.tif"
geoid_path = "source/etopo/ETOPO_2022_v1_60s_N90W180_geoid.tif"
dem_path = "images/dem-etopo.tif"
dem_land_path = "images/dem-land-etopo.tif"

def __get_url(latitude, longitude, grid, data_type, type_path=None):
    lat = ('N' if latitude >= 0 else 'S') + str(abs(latitude)).zfill(2)
    lon = ('E' if longitude >= 0 else 'W') + str(abs(longitude)).zfill(3)
    url = f'https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/{grid}s/{grid}s_{data_type if type_path is None else type_path}_gtif/ETOPO_2022_v1_{grid}s_{lat}{lon}_{data_type}.tif'
    return url

def __download(url, redownload=False):
    filename = url.split('/')[-1]
    if not os.path.exists(f'source/etopo'):
        os.makedirs(f'source/etopo')
    if not os.path.exists(f'source/etopo/{filename}') or redownload:
        r = requests.get(url)
        if r.status_code == 200:
            with open(f'source/etopo/{filename}', 'wb') as f:
                f.write(r.content)
        else:
            raise Exception(f'Error {r.status_code} downloading {url}')

def download(redownload=False):
    with progress("Downloading ETOPO data", 2) as pbar:
        __download(__get_url(90, -180, 60, 'geoid'), redownload)
        pbar.update(1)
        __download(__get_url(90, -180, 60, 'surface', 'surface_elev'), redownload)
        pbar.update(1)

def process_dem(include_islands=True):
    with progress("Loading land masks", 2) as pbar:
        gdf = gpd.read_file(shapefile_path)
        pbar.update(1)
        gdf_islands = gpd.read_file(island_shapefile_path)
        pbar.update(1)
    with progress("Masking elevation data", 1) as pbar:
        with rasterio.open(surface_path) as src:
            gdf = gdf.to_crs(src.crs)
            if include_islands:
                gdf_islands = gdf_islands.to_crs(src.crs)
                gdf = gpd.GeoDataFrame(pd.concat([gdf, gdf_islands], ignore_index=True), crs=src.crs)

            masked_image, masked_transform = mask(src, gdf.geometry)
            metadata = src.meta.copy()
            print(src.meta)
            metadata.update({"driver": "GTiff",
                            "height": masked_image.shape[1],
                            "width": masked_image.shape[2],
                            "transform": masked_transform,
                            "crs": src.crs})
            with rasterio.open(dem_land_path, 'w', **metadata) as dst:
                dst.write(masked_image)
        pbar.update(1)