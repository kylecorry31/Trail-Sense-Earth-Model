from scripts import etopo, compression, natural_earth, clip, progress
from PIL import Image
import numpy as np
import os
import re

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

            # First letter is either N or S followed by 2 digits and E or W and then 3 digits
            regex = r'([NS]\d{2})([EW]\d{3})'
            match = re.search(regex, region)
            if not match:
                print(f'Invalid region format: {region}')
                continue
            latitude, longitude = match.groups()

            latitude = int(latitude[1:]) * (1 if latitude[0] == 'N' else -1)
            longitude = int(longitude[1:]) * (1 if longitude[0] == 'E' else -1)

            end_latitude = latitude - resolution
            end_longitude = longitude + resolution

            image = natural_earth.remove_oceans_from_tif(file, 'images/dem_no_oceans.tif', scale=2, bbox=(longitude, end_latitude, end_longitude, latitude))

            # If all pixels are black, skip
            if np.all(image == 0):
                print(f'Skipping {region} as it contains no data')
                continue

            if compress_images:
                a, b = compression.minify('images/dem_no_oceans.tif', lambda x: x, -99999, f'output/dem/{region}.webp', 100, False, should_print=False)
                compression_factors.append((region, a, b, latitude, longitude, end_latitude, end_longitude))
            else:
                compression.split_16_bits('images/dem_no_oceans.tif', 'images/dem_lower.tif', 'images/dem_upper.tif')
                compression.minify_multiple(['images/dem_lower.tif', 'images/dem_upper.tif'], None, None, f'dem-{region}', True, 100, True, should_print=False, a_override=1, b_override=0)
                os.rename(f'output/dem-{region}-1-3.webp', f'output/dem/{region}.webp')
            pbar.update(1)
    
    if compress_images:
        kotlin = "arrayOf(\n"
        for factor in compression_factors:
            kotlin += f'    arrayOf("{factor[0]}", {factor[1]}f, {factor[2]}f, {factor[3]}.0, {factor[4]}.0, {factor[5]}.0, {factor[6]}.0),\n'
        kotlin += ")"
        print(kotlin)

        with open('output/dem/compression_factors.kt', 'w') as f:
            f.write(kotlin)