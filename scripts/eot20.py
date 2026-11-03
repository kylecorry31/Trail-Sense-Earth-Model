import netCDF4
import numpy as np
import os
from scripts import progress
import shutil
import requests
from .operators import process
from .operators import FlipY, ReplaceInvalid, PolarToCartesian, CartesianToPolar, Quadtree, Crop, ShiftX, Normalize, ReplaceLargeValues, Save, SplitProcessing, RemoveOceans

# Load the data
source_directory = 'source/eot20'
output_directory = 'images/eot20'

# This needs to be less than 255
final_width = 128
invalid_value = 100000
large_amplitude_threshold = 500
# The smallest phasor magnitude (cm) to measure the change in tide between cells against
error_floor = 10

shapefile_path = "source/natural-earth/ne_10m_land.shp"
island_shapefile_path = "source/natural-earth/ne_10m_minor_islands.shp"

def download():
    os.makedirs(source_directory, exist_ok=True)
    with progress.progress("Downloading EOT20 data", 1) as pbar:
        if not os.path.exists(f'{source_directory}/ocean_tides/2N2_ocean_eot20.nc'):
            url = 'https://www.seanoe.org/data/00683/79489/data/85762.zip'
            r = requests.get(url, allow_redirects=True)
            with open(f'{source_directory}/85762.zip', 'wb') as f:
                f.write(r.content)
            shutil.unpack_archive(f'{source_directory}/85762.zip', f'{source_directory}')
            os.remove(f'{source_directory}/85762.zip')
            os.remove(f'{source_directory}/load_tides.zip')
            shutil.unpack_archive(f'{source_directory}/ocean_tides.zip', f'{source_directory}')
            os.remove(f'{source_directory}/ocean_tides.zip')
            shutil.rmtree(f'{source_directory}/__MACOSX')
        pbar.update(1)

def process_ocean_tides(leaf_budget, base_degrees, min_degrees):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(source_directory, exist_ok=True)

    constituents = ['2N2', 'J1', 'K1', 'K2', 'M2', 'M4', 'MF', 'MM', 'N2', 'O1', 'P1', 'Q1', 'S1', 'S2', 'SA', 'SSA', 'T2']

    # Load the source data (as x, y phasors so they can be averaged), which is needed for all of the constituents at
    # once to decide where the model needs more detail
    phasors = []
    with progress.progress(f'Loading ocean tides', len(constituents)) as pbar:
        for constituent in constituents:
            file_path = f'{source_directory}/ocean_tides/{constituent}_ocean_eot20.nc'
            with netCDF4.Dataset(file_path, 'r') as file:
                # The source grid includes the -90 degree row and a duplicate 360 degree column
                images, _ = process(
                    [file.variables['amplitude'][:], file.variables['phase'][:]],
                    ReplaceInvalid(invalid_value),
                    Crop(top=1, right=1),
                    ShiftX(0.5, True),
                    FlipY(),
                    RemoveOceans(dilation=5, replacement=invalid_value),
                    PolarToCartesian(invalid_value),
                )
                phasors.extend(image.astype(np.float32) for image in images)
                pbar.update(1)

    # Cells are base_degrees where the tide varies slowly and are split in half, down to min_degrees, where it varies
    # more. Phasor values are in cm.
    degrees_per_pixel = 360 / phasors[0].shape[1]
    images, results = process(
        phasors,
        Quadtree(
            round(base_degrees / degrees_per_pixel),
            round(min_degrees / degrees_per_pixel),
            leaf_budget,
            final_width,
            invalid_value,
            reference_floor=error_floor,
        ),
        CartesianToPolar(invalid_value),
    )
    del phasors

    process([results[0]['indices_x']], Save([f'{output_directory}/indices-x.tif']))
    process([results[0]['indices_y']], Save([f'{output_directory}/indices-y.tif']))

    with progress.progress(f'Processing ocean tides', len(constituents)) as pbar:
        amplitudes = {}
        large_amplitudes = []
        for i, constituent in enumerate(constituents):
            # AMPLITUDE
            _, amplitude_results = process(
                [images[2 * i]],
                ReplaceLargeValues(large_amplitude_threshold, invalid_value=invalid_value),
                SplitProcessing(Normalize(0.0, invalid_value=invalid_value)),
                Save([f'{output_directory}/{constituent}-amplitude.tif'])
            )

            replace_large_values_idx = 0
            normalize_index = 1

            # Extract results
            for value in amplitude_results[replace_large_values_idx]['large_values'][0]:
                large_amplitudes.append((constituent, value[0], value[1], int(value[2])))

            amplitudes[constituent] = float(amplitude_results[normalize_index]['data'][0][0]['maximum'])

            # PHASE
            process(
                [images[2 * i + 1]],
                Normalize(-180.0, 180.0, invalid_value),
                Save([f'{output_directory}/{constituent}-phase.tif'])
            )

            pbar.update(1)

    return amplitudes, large_amplitudes
