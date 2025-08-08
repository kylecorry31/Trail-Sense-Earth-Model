from .progress import progress
from . import to_tif, load_pixels
import os
import zipfile
import numpy as np

INVALID_VALUE = -32768
SOURCE_DIRECTORY = 'source/srtm'
MERGED_DIRECTORY = 'source/srtm-merged'


def __hgt_to_tif(hgt_filepath, tif_filepath):
    # Read the hgt bytes
    with open(hgt_filepath, 'rb') as f:
        hgt_data = f.read()

    # Big endian 2 bytes per pixel
    data = np.frombuffer(hgt_data, dtype='>i2').copy()
    size = int(np.sqrt(len(data)))
    data = data.reshape((size, size))
    to_tif(data, tif_filepath)


def get_file_paths():
    return [os.path.join(MERGED_DIRECTORY, f) for f in os.listdir(MERGED_DIRECTORY) if f.endswith('.tif')]


def download(redownload=False):
    if not os.path.exists(SOURCE_DIRECTORY):
        os.makedirs(SOURCE_DIRECTORY)

    # TODO: Convert the download script to python

    # Unzip all files
    files = [f for f in os.listdir(SOURCE_DIRECTORY) if f.endswith('.zip')]
    with progress('Unzipping SRTM files', total=len(files)) as pbar:
        for file in files:
            with zipfile.ZipFile(os.path.join(SOURCE_DIRECTORY, file), 'r') as zip_ref:
                zip_ref.extractall(SOURCE_DIRECTORY)
            os.remove(os.path.join(SOURCE_DIRECTORY, file))
            pbar.update(1)

    # Convert hgt to tif
    hgt_files = [f for f in os.listdir(SOURCE_DIRECTORY) if f.endswith('.hgt')]
    with progress('Converting SRTM HGT files to TIFF', total=len(hgt_files)) as pbar:
        for hgt_file in hgt_files:
            hgt_filepath = os.path.join(SOURCE_DIRECTORY, hgt_file)
            tif_filepath = os.path.join(
                SOURCE_DIRECTORY, hgt_file.replace('.hgt', '.tif'))
            __hgt_to_tif(hgt_filepath, tif_filepath)
            os.remove(hgt_filepath)
            pbar.update(1)

    # TODO: Merge into 5x5 grid
    if not os.path.exists(MERGED_DIRECTORY):
        os.makedirs(MERGED_DIRECTORY)
    
    regions = []
    resolution = 10
    for lat in range(-90+resolution, 91, resolution):
        for lon in range(-180, 180, resolution):
            regions.append([lat, lon, lat + resolution, lon + resolution])
    
    with progress('Merging SRTM files', total=len(regions)) as pbar:
        files = [f for f in os.listdir(SOURCE_DIRECTORY) if f.endswith('.tif')]
        for region in regions:
            lat_min, lon_min, lat_max, lon_max = region
            rows = (lat_max - lat_min)
            cols = (lon_max - lon_min)
            merged = None

            ns = f'N{abs(lat_min):02d}' if lat_min >= 0 else f'S{abs(lat_min):02d}'
            ew = f'E{abs(lon_min):03d}' if lon_min >= 0 else f'W{abs(lon_min):03d}'
            output_name = f'{ns}{ew}.tif'
            output_path = os.path.join(MERGED_DIRECTORY, output_name)

            if os.path.exists(output_path):
                pbar.update(1)
                continue

            for lat in range(lat_min, lat_max):
                for lon in range(lon_min, lon_max):
                    ns = f'N{abs(lat):02d}' if lat >= 0 else f'S{abs(lat):02d}'
                    ew = f'E{abs(lon):03d}' if lon >= 0 else f'W{abs(lon):03d}'
                    filename = f'{ns}{ew}.tif'
                    filepath = os.path.join(SOURCE_DIRECTORY, filename)
                    row = lat_max - lat - 1  # southern tiles go at the bottom
                    col = lon - lon_min

                    if os.path.exists(filepath):
                        try:
                            pixels = load_pixels(filepath)
                            if merged is None:
                                height, width = pixels.shape
                                merged = np.full((rows * height, cols * width), 0, dtype=np.float32)
                            merged[row * height:(row + 1) * height, col * width:(col + 1) * width] = pixels
                        except Exception as e:
                            print(f'Failed to load {filename}: {e}')
            if merged is not None:
                to_tif(merged, output_path)
            pbar.update(1)