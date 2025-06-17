from scripts import etopo, compression, natural_earth, progress, clip, to_tif
from PIL import Image
import numpy as np
import os
import re
import json
import zipfile

scale=1.0
compress_images = True
compression_quality = 100
ignore_threshold = 2
version = '0.2.0'

# High resolution: resolution = 15, scale = 1.0, quality = 100, ignore_threshold = 2, compress_images = True
# Low resolution: resolution = 15, scale = 0.2, quality = 60, ignore_threshold = 10, compress_images = True

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None

resolution = 15
true_resolution = int(resolution / scale)

etopo.download(surface_resolution=resolution)
natural_earth.download()

files = etopo.get_file_paths(resolution, 'surface')

if not os.path.exists('output/dem'):
    os.makedirs('output/dem')

with progress.progress('Processing DEM files', len(files)) as pbar:
    compression_factors = []
    for file in files:
        region = file.split('_')[-2]

        if region.startswith('S60') or region.startswith('S75') or region.startswith('N90'):
            pbar.update(1)
            continue

        # First letter is either N or S followed by 2 digits and E or W and then 3 digits
        regex = r'([NS]\d{2})([EW]\d{3})'
        match = re.search(regex, region)
        if not match:
            print(f'Invalid region format: {region}')
            pbar.update(1)
            continue
        latitude, longitude = match.groups()

        latitude = int(latitude[1:]) * (1 if latitude[0] == 'N' else -1)
        longitude = int(longitude[1:]) * (1 if longitude[0] == 'E' else -1)

        end_latitude = latitude - resolution
        end_longitude = longitude + resolution

        initial_size = 3600
        image_size = (int(initial_size * scale), int(initial_size * scale)) if scale is not None else None
        image = natural_earth.remove_oceans_from_tif(file, 'images/dem_no_oceans.tif', scale=4, bbox=(longitude, end_latitude, end_longitude, latitude), resize=image_size, dilation=-20)
        image = natural_earth.remove_inland_water(image, scale=4, bbox=(longitude, end_latitude, end_longitude, latitude), replacement=0)

        # If all pixels are black, skip
        if np.all(image < ignore_threshold):
            pbar.update(1)
            continue

        # Image is not allowed to be lower than the lowest place on land
        image[image < -430.5] = 0
        to_tif(image, 'images/dem_no_oceans.tif')

        if compress_images:
            a, b = compression.minify('images/dem_no_oceans.tif', lambda x: x, -99999, f'output/dem/{region}.webp', compression_quality, False, should_print=False)
            compression_factors.append({
                "filename": f'{region}.webp',
                "a": float(a),
                "b": float(b),
                "latitude_start": float(latitude),
                "longitude_start": float(longitude),
                "latitude_end": float(end_latitude),
                "longitude_end": float(end_longitude),
                "width": int(image.shape[1]),
                "height": int(image.shape[0])
            })
        else:
            a = 0.125
            b = -compression.get_min_max(['images/dem_no_oceans.tif'])[0]
            compression_factors.append({
                "filename": f'{region}.webp',
                "a": float(a),
                "b": float(b),
                "latitude_start": float(latitude),
                "longitude_start": float(longitude),
                "latitude_end": float(end_latitude),
                "longitude_end": float(end_longitude),
                "width": int(image.shape[1]),
                "height": int(image.shape[0])
            })
            compression.split_16_bits('images/dem_no_oceans.tif', 'images/dem_lower.tif', 'images/dem_upper.tif', a, b)
            compression.minify_multiple(['images/dem_lower.tif', 'images/dem_upper.tif'], None, None, f'dem-{region}', True, 100, True, should_print=False, a_override=1, b_override=0)
            os.rename(f'output/dem-{region}-1-3.webp', f'output/dem/{region}.webp')
        pbar.update(1)

with open('output/dem/index.json', 'w') as f:
    json.dump({
        "compression_method": "8-bit" if compress_images else "16-bit",
        "version": version,
        "resolution_arc_seconds": true_resolution,
        "files": compression_factors
    }, f, indent=4)

# Compress the contents of the dem directory to a zip file
with zipfile.ZipFile(f'output/dem-{version}-{"8bit" if compress_images else "16bit"}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('output/dem'):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'output/dem'))