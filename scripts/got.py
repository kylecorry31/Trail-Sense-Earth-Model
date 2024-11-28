import netCDF4
import os
import rasterio.mask
import rasterio.transform
from scripts import progress, to_tif
import numpy as np
import geopandas as gpd
import rasterio
from scipy.ndimage import binary_dilation
from rasterio.features import rasterize
from PIL import Image

# Load the data
source_directory = 'source/got5.5'
output_directory = 'images/got'
x_scale = 0.125
y_scale = 0.125
width = 2880
height = 1441
invalid_value = 0

# This needs to be less than 255
final_width = 250

shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"

def download():
    pass
    # os.makedirs(source_directory, exist_ok=True)
    # with progress.progress("Downloading EOT20 data", 1) as pbar:
    #     if not os.path.exists(f'{source_directory}/ocean_tides/2N2_ocean_eot20.nc'):
    #         url = 'https://www.seanoe.org/data/00683/79489/data/85762.zip'
    #         r = requests.get(url, allow_redirects=True)
    #         with open(f'{source_directory}/85762.zip', 'wb') as f:
    #             f.write(r.content)
    #         shutil.unpack_archive(f'{source_directory}/85762.zip', f'{source_directory}')
    #         os.remove(f'{source_directory}/85762.zip')
    #         os.remove(f'{source_directory}/load_tides.zip')
    #         shutil.unpack_archive(f'{source_directory}/ocean_tides.zip', f'{source_directory}')
    #         os.remove(f'{source_directory}/ocean_tides.zip')
    #         shutil.rmtree(f'{source_directory}/__MACOSX')
    #     pbar.update(1)
    

def process_ocean_tides(final_shape):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(source_directory, exist_ok=True)

    constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'MS4', 'MU2', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA']
    # Lowercase constituents
    constituents = [constituent.lower() for constituent in constituents]

    with progress.progress("Loading land masks", 2) as pbar:
        gdf = gpd.read_file(shapefile_path)
        pbar.update(1)
        gdf_islands = gpd.read_file(island_shapefile_path)
        pbar.update(1)

    # Render the shapefiles to an image of 2881x1441
    with progress.progress("Rendering land masks", 3) as pbar:
        scale = 4
        mask = rasterize(gdf.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(-180, 90, x_scale / scale, y_scale / scale), dtype=np.float32)
        mask[mask > 0] = 255
        pbar.update(1)

        img_islands = rasterize(gdf_islands.geometry, out_shape=(height * scale, width * scale), transform=rasterio.transform.from_origin(-180, 90, x_scale / scale, y_scale / scale), dtype=np.float32)
        img_islands[img_islands > 0] = 255
        pbar.update(1)

        mask = np.maximum(mask, img_islands)

        # Dilate the image
        mask = mask > 0
        mask = binary_dilation(mask, iterations=5 * scale)
        mask = mask.astype(np.float32)
        
        # Downsample the image
        mask = mask[::scale, ::scale]

        pbar.update(1)

    with progress.progress(f'Processing ocean tides', len(constituents) * 2) as pbar:
        amplitudes = {}
        large_amplitudes = []
        indices_images_created = False
        non_zero_bool_array = None
        for constituent in constituents:
            file_path = f'{source_directory}/ocean_tides/{constituent}.nc'
            with netCDF4.Dataset(file_path, 'r') as file:
                phase = file.variables['phase'][:]
                amplitude = file.variables['amplitude'][:]

                min_phase = 0.0
                max_phase = 360.0
                phase = (phase - min_phase) / (max_phase - min_phase)
   
                x_shift = amplitude.shape[1] // 2

                # AMPLITUDE
                updated = to_tif(amplitude, f'{output_directory}/{constituent.upper()}-amplitude.tif', True, x_shift, invalid_value, (width, height))
                # Mask the image
                updated = updated * mask
                updated[mask == 0] = invalid_value

                # Resize to the final shape (before normalization)
                if final_shape is not None:
                    img = Image.fromarray(updated).resize(final_shape, Image.NEAREST)
                    updated = np.array(img).reshape((final_shape[1], final_shape[0]))

                min_amplitude = 0.0

                has_large_amplitudes = (np.sum(updated > 500) - np.sum(updated == invalid_value)) > 0
                if has_large_amplitudes:
                    large_amplitude_indices = np.argwhere((updated > 500) & (updated != invalid_value))
                    for idx in large_amplitude_indices:
                        large_amplitudes.append((constituent, int(idx[0]), int(idx[1]), int(updated[idx[0], idx[1]])))
                        updated[idx[0], idx[1]] = 0
                
                max_amplitude = np.max(updated[updated != invalid_value])

                normalized = (updated[updated != invalid_value] - min_amplitude) / (max_amplitude - min_amplitude)
                normalized[normalized < 0] = 0
                updated[updated != invalid_value] = normalized

                if non_zero_bool_array is None:
                    non_zero_bool_array = (updated != invalid_value)

                # Create the indices images
                if not indices_images_created:
                    indices_images_created = True
                    indices_x = np.zeros(updated.shape)
                    indices_y = np.zeros(updated.shape)
                    non_zero_indices = np.argwhere(non_zero_bool_array)
                    for i in range(len(non_zero_indices)):
                        source_x = non_zero_indices[i][1]
                        source_y = non_zero_indices[i][0]
                        destination_x = i % final_width + 1
                        destination_y = i // final_width + 1
                        indices_x[source_y, source_x] = destination_x
                        indices_y[source_y, source_x] = destination_y
                    # Save the images
                    to_tif(indices_x, f'{output_directory}/indices-x.tif')
                    to_tif(indices_y, f'{output_directory}/indices-y.tif')

                # Create a condensed image
                updated = updated[non_zero_bool_array]
                total_values = len(updated)
                updated = np.append(updated, np.zeros(final_width - (total_values % final_width)))
                updated = updated.reshape((-1, final_width))
                amplitudes[constituent.upper()] = float(max_amplitude)
                to_tif(updated, f'{output_directory}/{constituent.upper()}-amplitude.tif')
                pbar.update(1)
                
                # PHASE
                updated = to_tif(phase, f'{output_directory}/{constituent.upper()}-phase.tif', True, x_shift, invalid_value, (width, height))
                # Mask the image
                updated = updated * mask
                updated[mask == 0] = invalid_value

                # Resize to the final shape
                if final_shape is not None:
                    img = Image.fromarray(updated).resize(final_shape, Image.NEAREST)
                    updated = np.array(img).reshape((final_shape[1], final_shape[0]))
                
                updated = updated[non_zero_bool_array]
                total_values = len(updated)
                updated = np.append(updated, np.zeros(final_width - (total_values % final_width)))
                updated = updated.reshape((-1, final_width))

                to_tif(updated, f'{output_directory}/{constituent.upper()}-phase.tif')


                pbar.update(1)
    return amplitudes, large_amplitudes
    

