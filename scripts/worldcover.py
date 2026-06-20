import os
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import rasterio
import requests
from rasterio.enums import Resampling
from rasterio.transform import from_origin

from .progress import progress


SOURCE_DIRECTORY = "source/worldcover"
OUTPUT_PATH = "images/worldcover-map.tif"
BUCKET_URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com"
DATASET_PREFIX = "v200/2021/map/"
TILE_PATTERN = re.compile(r"_([NS])(\d{2})([EW])(\d{3})_Map\.tif$")

# Preserve more WorldCover detail without making the global smoothing pipeline
# operate on the full 10 m dataset.
PIXELS_PER_DEGREE = 30
OUTPUT_WIDTH = 360 * PIXELS_PER_DEGREE
OUTPUT_HEIGHT = 180 * PIXELS_PER_DEGREE
TILE_SIZE_DEGREES = 3
TILE_SIZE_PIXELS = TILE_SIZE_DEGREES * PIXELS_PER_DEGREE


def _list_tiles():
    tiles = []
    continuation_token = None

    while True:
        params = {
            "list-type": "2",
            "prefix": DATASET_PREFIX,
            "max-keys": 1000,
        }
        if continuation_token is not None:
            params["continuation-token"] = continuation_token

        response = requests.get(BUCKET_URL, params=params, timeout=60)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        namespace = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

        for item in root.findall("s3:Contents", namespace):
            key = item.findtext("s3:Key", namespaces=namespace)
            if key is not None and key.endswith("_Map.tif"):
                tiles.append(key)

        if root.findtext("s3:IsTruncated", namespaces=namespace) != "true":
            break

        continuation_token = root.findtext(
            "s3:NextContinuationToken", namespaces=namespace
        )
        if continuation_token is None:
            raise RuntimeError("WorldCover tile listing was truncated without a token")

    return tiles


def _download_tile(key, redownload):
    filename = os.path.basename(key)
    path = os.path.join(SOURCE_DIRECTORY, filename)

    if not redownload and os.path.exists(path):
        with rasterio.open(path) as source:
            if source.shape == (TILE_SIZE_PIXELS, TILE_SIZE_PIXELS):
                return

    latitude, longitude = _tile_coordinates(filename)
    metadata = {
        "driver": "GTiff",
        "height": TILE_SIZE_PIXELS,
        "width": TILE_SIZE_PIXELS,
        "count": 1,
        "dtype": np.uint8,
        "crs": "EPSG:4326",
        "transform": from_origin(
            longitude,
            latitude + TILE_SIZE_DEGREES,
            1 / PIXELS_PER_DEGREE,
            1 / PIXELS_PER_DEGREE,
        ),
        "compress": "lzw",
        "nodata": 0,
    }

    temporary_path = f"{path}.part"
    for attempt in range(3):
        try:
            # WorldCover tiles are Cloud-Optimized GeoTIFFs. Rasterio uses HTTP
            # range requests and the built-in overviews, so only enough data for
            # the requested reduced categorical tile is transferred.
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
                with rasterio.open(f"{BUCKET_URL}/{key}") as source:
                    tile = source.read(
                        1,
                        out_shape=(TILE_SIZE_PIXELS, TILE_SIZE_PIXELS),
                        resampling=Resampling.mode,
                    )

            with rasterio.open(temporary_path, "w", **metadata) as destination:
                destination.write(tile, 1)

            os.replace(temporary_path, path)
            return
        except (OSError, rasterio.errors.RasterioError):
            if os.path.exists(temporary_path):
                os.remove(temporary_path)
            if attempt == 2:
                raise


def download(redownload=False, workers=8):
    """Download WorldCover 2021 v200 at the resolution used by this project."""
    os.makedirs(SOURCE_DIRECTORY, exist_ok=True)
    tiles = _list_tiles()

    with progress("Downloading WorldCover tiles", len(tiles)) as pbar:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(_download_tile, key, redownload) for key in tiles
            ]
            for future in as_completed(futures):
                future.result()
                pbar.update(1)


def _tile_coordinates(filename):
    match = TILE_PATTERN.search(filename)
    if match is None:
        raise ValueError(f"Invalid WorldCover tile filename: {filename}")

    latitude = int(match.group(2))
    if match.group(1) == "S":
        latitude = -latitude

    longitude = int(match.group(4))
    if match.group(3) == "W":
        longitude = -longitude

    return latitude, longitude


def process_map():
    """Create a low-resolution global categorical raster from downloaded tiles."""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    filenames = sorted(
        filename
        for filename in os.listdir(SOURCE_DIRECTORY)
        if TILE_PATTERN.search(filename)
    )
    if not filenames:
        raise RuntimeError("No WorldCover tiles found; run worldcover.download() first")

    metadata = {
        "driver": "GTiff",
        "height": OUTPUT_HEIGHT,
        "width": OUTPUT_WIDTH,
        "count": 1,
        "dtype": np.uint8,
        "crs": "EPSG:4326",
        "transform": from_origin(
            -180, 90, 1 / PIXELS_PER_DEGREE, 1 / PIXELS_PER_DEGREE
        ),
        "compress": "lzw",
        "nodata": 0,
    }

    with rasterio.open(OUTPUT_PATH, "w", **metadata) as destination:
        with progress("Processing WorldCover tiles", len(filenames)) as pbar:
            for filename in filenames:
                latitude, longitude = _tile_coordinates(filename)
                row = (90 - latitude - TILE_SIZE_DEGREES) * PIXELS_PER_DEGREE
                column = (longitude + 180) * PIXELS_PER_DEGREE

                with rasterio.open(os.path.join(SOURCE_DIRECTORY, filename)) as source:
                    tile = source.read(1)

                destination.write(
                    tile,
                    1,
                    window=(
                        (row, row + TILE_SIZE_PIXELS),
                        (column, column + TILE_SIZE_PIXELS),
                    ),
                )
                pbar.update(1)
