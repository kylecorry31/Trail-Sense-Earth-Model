from . import get_min_max, compress_to_webp
from .progress import progress

def minify_multiple(files, map_point, invalid_value, data_point, use_rgb, quality, lossless):
    offset = get_min_max(files, map_point, invalid_value)

    print(f'Offset ({data_point}): {-offset[0]} for {data_point} (Min: {offset[0]}, Max: {offset[1]})')

    grouping = 3 if use_rgb else 1
    
    with progress('Compressing', len(files) // grouping) as pbar:
        for i in range(0, len(files), grouping):
            compress_to_webp(files[i:i+grouping], f'output/{data_point}-{i + 1}-{i + grouping}.webp', map_point, offset[0], invalid_value, quality, lossless)
            pbar.update(grouping)

def minify(path, map_point, invalid_value, output_filename, quality, lossless):
    offset = get_min_max([path], map_point, invalid_value)

    print(f'Offset: {-offset[0]} (Min: {offset[0]}, Max: {offset[1]})')
    
    with progress('Compressing', 1) as pbar:
        compress_to_webp([path], output_filename, map_point, offset[0], invalid_value, quality, lossless)
        pbar.update(1)