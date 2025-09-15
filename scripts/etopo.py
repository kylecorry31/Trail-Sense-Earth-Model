from .progress import progress
import os
import requests
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask
import PIL.Image as Image
from scripts import to_tif, load_pixels
from scripts.progress import progress

shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"
surface_path = "source/etopo/ETOPO_2022_v1_60s_N90W180_surface.tif"
surface_path_30 = "source/etopo/ETOPO_2022_v1_30s_N90W180_surface.tif"
geoid_path = "source/etopo/ETOPO_2022_v1_60s_N90W180_geoid.tif"
dem_path = "images/dem-etopo.tif"
dem_land_path = "images/dem-land-etopo.tif"
elevation_invalid_value = -99999

elevations = None

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
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    with open(f'source/etopo/{filename}', 'wb') as f:
                        f.write(r.content)
                        break
                else:
                    raise Exception(f'Error {r.status_code} downloading {url}')
            except Exception as e:
                if attempt == max_retries:
                    raise e

def get_file_paths(resolution, model):
    regions = []
    if resolution != 15:
        regions.append([90, -180])
    else:
        for lat in range(-90+resolution, 91, resolution):
            for lon in range(-180, 180, resolution):
                regions.append([lat, lon])
    
    urls = []
    for region in regions:
        urls.append(__get_url(region[0], region[1], resolution, model, 'surface_elev' if model == 'surface' else None))
    
    return [f'source/etopo/{url.split('/')[-1]}' for url in urls]


def download(redownload=False, geoid_resolution=60, surface_resolution=15):
    surface_regions = []
    if surface_resolution != 15:
        surface_regions.append([90, -180])
    else:
        for lat in range(-90+surface_resolution, 91, surface_resolution):
            for lon in range(-180, 180, surface_resolution):
                surface_regions.append([lat, lon])

    with progress("Downloading ETOPO data", 1 + len(surface_regions)) as pbar:
        __download(__get_url(90, -180, geoid_resolution, 'geoid'), redownload)
        pbar.update(1)
        for region in surface_regions:
            __download(__get_url(region[0], region[1], surface_resolution, 'surface', 'surface_elev'), redownload)
            __download(__get_url(region[0], region[1], surface_resolution, 'surface_sid'), redownload)
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
            metadata.update({"driver": "GTiff",
                            "height": masked_image.shape[1],
                            "width": masked_image.shape[2],
                            "transform": masked_transform,
                            "crs": src.crs})
            with rasterio.open(dem_land_path, 'w', **metadata) as dst:
                dst.write(masked_image)
        pbar.update(1)

def adjust_for_elevation(data, map_fn):
    global elevations
    if elevations is None:
        Image.MAX_IMAGE_PIXELS = None
        elevations = load_pixels(dem_land_path)
    w = len(data[0])
    h = len(data)
    for y in range(h):
        for x in range(w):
            elevation_x = int(x / w * len(elevations[0]))
            elevation_y = int(y / h * len(elevations))
            elevation = elevations[elevation_y, elevation_x]
            if elevation == elevation_invalid_value:
                elevation = 0
            data[y, x] = map_fn(data[y, x], elevation)
    return data