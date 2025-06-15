from scripts import etopo, compression, natural_earth, progress
from PIL import Image
import numpy as np
import os
import re
import json
import zipfile

resolution = 15
image_resolution = (360 * 40, 180 * 40)
compress_images = True

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None

etopo.download(surface_resolution=resolution)
natural_earth.download()

if resolution == 60:
    with progress.progress('Removing oceans', 1) as pbar:
        natural_earth.remove_oceans_from_tif(etopo.surface_path, 'images/dem_no_oceans.tif', resize=image_resolution, scale=1)
        pbar.update(1)

    dem_app = 'images/dem_no_oceans.tif'#images/dem_app.tif'
    # clip.clip_uninhabitable_areas_tif('images/dem_no_oceans.tif', dem_app)

    offsets = compression.get_min_max([dem_app])
    print(offsets[0])
    compression.split_16_bits(dem_app, 'images/dem_lower.tif', 'images/dem_upper.tif', 0.05, -offsets[0])

    compression.minify_multiple(['images/dem_lower.tif', 'images/dem_upper.tif'], lambda x: x, -99999, 'dem', True, 100, True, grouping=2, a_override=1, b_override=0)


    os.rename('output/dem-1-2.webp', 'output/dem.webp')
else:
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

            image = natural_earth.remove_oceans_from_tif(file, 'images/dem_no_oceans.tif', scale=4, bbox=(longitude, end_latitude, end_longitude, latitude))

            # If all pixels are black, skip
            if np.all(image < 2) and np.all(image > -2):
                print(f'Skipping {region} as it contains no data')
                continue

            if compress_images:
                a, b = compression.minify('images/dem_no_oceans.tif', lambda x: x, -99999, f'output/dem/{region}.webp', 100, False, should_print=False)
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
                offset = compression.get_min_max(['images/dem_no_oceans.tif'])[0]
                compression_factors.append({
                    "filename": f'{region}.webp',
                    "a": 0.05,
                    "b": -offset,
                    "latitude_start": latitude,
                    "longitude_start": longitude,
                    "latitude_end": end_latitude,
                    "longitude_end": end_longitude,
                    "width": image.shape[1],
                    "height": image.shape[0]
                })
                compression.split_16_bits('images/dem_no_oceans.tif', 'images/dem_lower.tif', 'images/dem_upper.tif', 0.05, -offset)
                compression.minify_multiple(['images/dem_lower.tif', 'images/dem_upper.tif'], lambda x: x, None, f'dem-{region}', True, 100, True, should_print=False, a_override=1, b_override=0)
                os.rename(f'output/dem-{region}-1-3.webp', f'output/dem/{region}.webp')
            pbar.update(1)
    
    with open('output/dem/index.json', 'w') as f:
        json.dump({
            "resolution_arc_seconds": resolution,
            "files": compression_factors,
            "compression_method": "8-bit" if compress_images else "16-bit"
        }, f, indent=4)
    
    # Compress the contents of the dem directory to a zip file
    with zipfile.ZipFile('output/dem.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('output/dem'):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'output/dem'))