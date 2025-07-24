import requests
import os
from .progress import progress
from . import load, to_tif
import zipfile
import geopandas as gpd
import rasterio.transform
import rasterio
from scipy.ndimage import binary_dilation, binary_erosion
from rasterio.features import rasterize
import numpy as np

last_mask = None
last_mask_replacement = None
last_mask_inverted = False
last_mask_x_scale = None
last_mask_y_scale = None
last_mask_dilation = None
last_mask_scale = None

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
        'https://naciscdn.org/naturalearth/10m/physical/ne_10m_lakes.zip',
        'https://naciscdn.org/naturalearth/10m/physical/ne_10m_rivers_lake_centerlines.zip'
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

def remove_oceans_from_tif(image_path, output_path, resize=None, replacement=0, inverted=False, x_scale=None, y_scale=None, dilation=5, scale=4, bbox=None, only_replace_negative_pixels=False, mode='F'):
    image = np.array(load(image_path, resize))
    image = remove_oceans(image, replacement, inverted, x_scale, y_scale, dilation, scale, bbox, only_replace_negative_pixels)
    to_tif(image, output_path, mode=mode)
    return image

def remove_oceans(image, replacement=0, inverted=False, x_scale=None, y_scale=None, dilation=5, scale=4, bbox=None, only_replace_negative_pixels=False):
    global last_mask, last_mask_replacement, last_mask_inverted, last_mask_x_scale, last_mask_y_scale, last_mask_dilation, last_mask_scale
    # Render the shapefiles to an image
    width = image.shape[1]
    height = image.shape[0]

    # Default to global extent if no bbox specified
    if bbox is None:
        bbox = (-180, -90, 180, 90)  # (west, south, east, north)
    
    west, south, east, north = bbox
    
    if x_scale is None:
        x_scale = (east - west) / width
    
    if y_scale is None:
        y_scale = (north - south) / height

    if last_mask is not None and last_mask_replacement == replacement and last_mask_inverted == inverted and last_mask_x_scale == x_scale and last_mask_y_scale == y_scale and last_mask_dilation == dilation and last_mask_scale == scale and bbox is None:
        mask = last_mask
    else:
        shapefile_path = "source/natural-earth/ne_10m_land.shp"
        island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"

        gdf = gpd.read_file(shapefile_path)
        gdf_islands = gpd.read_file(island_shapefile_path)

        mask = rasterize(gdf.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(west, north, x_scale / scale, y_scale / scale), dtype=np.float32)
        mask[mask > 0] = 255

        img_islands = rasterize(gdf_islands.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(west, north, x_scale / scale, y_scale / scale), dtype=np.float32)
        img_islands[img_islands > 0] = 255

        mask = np.maximum(mask, img_islands)

        # Invert the mask
        if inverted:
            mask = 255 - mask

        # Dilate the image
        mask = mask > 0
        if dilation < 0:
            mask = binary_erosion(mask, iterations=-dilation * scale)
        elif dilation > 0:
            mask = binary_dilation(mask, iterations=dilation * scale)
        mask = mask.astype(np.float32)
        
        # Downsample the image
        mask = mask[::scale, ::scale]

    last_mask = mask
    last_mask_replacement = replacement
    last_mask_inverted = inverted
    last_mask_x_scale = x_scale
    last_mask_y_scale = y_scale
    last_mask_dilation = dilation
    last_mask_scale = scale

    if only_replace_negative_pixels:
        image[(mask == 0) & (image < 0)] = replacement
    else:
        image[mask == 0] = replacement
    return image

def remove_geometry(image, shapefile_path, replacement=0, x_scale=None, y_scale=None, dilation=5, scale=4, bbox=None, only_replace_negative_pixels=False):
    # Render the shapefiles to an image
    width = image.shape[1]
    height = image.shape[0]

    # Default to global extent if no bbox specified
    if bbox is None:
        bbox = (-180, -90, 180, 90)  # (west, south, east, north)
    
    west, south, east, north = bbox
    
    if x_scale is None:
        x_scale = (east - west) / width
    
    if y_scale is None:
        y_scale = (north - south) / height

    gdf = gpd.read_file(shapefile_path)

    mask = rasterize(gdf.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(west, north, x_scale / scale, y_scale / scale), dtype=np.float32)
    mask[mask > 0] = 255

    # Invert the mask
    mask = 255 - mask

    # Dilate the image
    mask = mask > 0
    if dilation < 0:
        mask = binary_erosion(mask, iterations=-dilation * scale)
    elif dilation > 0:
        mask = binary_dilation(mask, iterations=dilation * scale)
    mask = mask.astype(np.float32)
    
    # Downsample the image
    mask = mask[::scale, ::scale]

    if only_replace_negative_pixels:
        image[(mask == 0) & (image < 0)] = replacement
    else:
        image[mask == 0] = replacement
    return image

def remove_inland_water(image, replacement=0, x_scale=None, y_scale=None, dilation=5, scale=4, bbox=None, only_replace_negative_pixels=False, remove_rivers=False):
    new_image = remove_geometry(image, "source/natural-earth/ne_10m_lakes.shp", replacement, x_scale, y_scale, dilation, scale, bbox, only_replace_negative_pixels)
    if remove_rivers:
        new_image = remove_geometry(new_image, "source/natural-earth/ne_10m_rivers_lake_centerlines.shp", replacement, x_scale, y_scale, dilation, scale, bbox, only_replace_negative_pixels)
    return new_image
    
