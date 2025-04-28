import requests
import os
from .progress import progress
import zipfile
import geopandas as gpd
import rasterio.transform
import rasterio
from scipy.ndimage import binary_dilation
from rasterio.features import rasterize
import numpy as np

def __download(url, redownload=False):
    filename = url.split('/')[-1]
    if not os.path.exists(f'source/natural-earth'):
        os.makedirs(f'source/natural-earth')
    if not os.path.exists(f'source/natural-earth/{filename}') or redownload:
        r = requests.get(url)
        if r.status_code == 200:
            with open(f'source/natural-earth/{filename}', 'wb') as f:
                f.write(r.content)
        else:
            raise Exception(f'Error {r.status_code} downloading {url}')

def download(redownload=False):
    files = [
        'https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip',
        'https://naciscdn.org/naturalearth/10m/physical/ne_10m_minor_islands.zip',
    ]
    with progress("Downloading Natural Earth data", len(files)) as pbar:
        for file in files:
            __download(file, redownload)
            pbar.update(1)
    
    # unzip the files
    with progress("Unzipping Natural Earth data", len(files)) as pbar:
        for file in files:
            filename = file.split('/')[-1]
            with zipfile.ZipFile(f'source/natural-earth/{filename}', 'r') as zip_ref:
                zip_ref.extractall(f'source/natural-earth')
            pbar.update(1)

def remove_oceans(image, replacement=0, inverted=False, x_scale=0.25, y_scale=0.25, dilation=5):
    shapefile_path = "source/natural-earth/ne_10m_land.shp"
    island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"

    gdf = gpd.read_file(shapefile_path)
    gdf_islands = gpd.read_file(island_shapefile_path)

    # Render the shapefiles to an image
    width = image.shape[1]
    height = image.shape[0]
    scale = 4
    mask = rasterize(gdf.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(-180, 90, x_scale / scale, y_scale / scale), dtype=np.float32)
    mask[mask > 0] = 255

    img_islands = rasterize(gdf_islands.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(-180, 90, x_scale / scale, y_scale / scale), dtype=np.float32)
    img_islands[img_islands > 0] = 255

    mask = np.maximum(mask, img_islands)

    # Invert the mask
    if inverted:
        mask = 255 - mask

    # Dilate the image
    mask = mask > 0
    mask = binary_dilation(mask, iterations=dilation * scale)
    mask = mask.astype(np.float32)
    
    # Downsample the image
    mask = mask[::scale, ::scale]

    
    image = image * mask
    image[mask == 0] = replacement
    return image
    
