from scripts import etopo, natural_earth, progress, load_pixels
from scripts.webp import encode_gray
from scripts.size_budget import fit_to_budget
from scripts.operators import (
    process,
    Reshape,
    Mask,
    ToMask,
    Conditional,
    RemoveBathymetry,
    RemoveInlandWater,
    RemoveEmpty,
    Stretch,
    LinearCompression,
    Quantize,
    Split16Bits,
    AppendWaterChannel,
    WebpQualityOptions,
    Save,
)
from functools import partial
from PIL import Image
import numpy as np
import os
import re
import json
import math
import zipfile
import hashlib
import inspect
import pickle
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat

# INPUT
version = "0.5.0"
# Set to the id of a preset (ex. "mini") to only generate that one
preset_filter = None

# Each lossy preset picks the resolution and WebP quality of every tile to minimize the error within the size budget
low = {
    "scales": [0.5, 0.65, 0.8, 1.0],
    "qualities": [60, 75, 90, 95],
    "size_budget_bytes": 20_000_000,
    "relief_scale": 1000,
    "latitude_importance": [(60, 0.3)],
    "detail_weight": 150,
}
mini = {
    "scales": [0.1, 0.15, 0.2, 0.25, 0.3, 0.4],
    "qualities": [50, 65, 75, 85, 95],
    "size_budget_bytes": 2_250_000,
    # A tile's error counts for more the more relief it has (+1x per this many meters), as its peaks are lost first
    "relief_scale": 1000,
    # ...and for less where few people hike: (latitude from, importance)
    "latitude_importance": [(60, 0.3)],
    # Losing all of a tile's detail (the elevation changes that make up the gain of a route) counts as this many meters of error
    "detail_weight": 150,
}

######## Program, don't modify ########
# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None
resolution = 15
tile_pixels = 3600
# The number of tiles processed at once
max_workers = 4
# Slow steps are saved here so that changing how the options are chosen (ex. the budget) is quick (delete it to start over)
cache_directory = "output/cache/dem"

# The source identifiers of ETOPO which are land (the others are bathymetry), by region if it differs from the default
default_land_ids = [9, 10, 11, 13]
land_ids_overrides = {
    "N45E030": [1, 9, 10, 11, 13],
    "N45E045": [1, 9, 10, 11, 13],
}


def get_tile_options(region, full, latitude, longitude, settings):
    """Every resolution and quality a tile could be saved as, with what is needed to cost each for choosing between them."""
    # Tiles are narrower in the ground distance they cover towards the poles
    mid_latitude = latitude - resolution / 2
    width_factor = math.cos(math.radians(mid_latitude))
    relief = float(full.max() - full.min())

    options = []
    for option_scale in settings["scales"]:
        height = int(full.shape[0] * option_scale)
        width = int(height * width_factor)
        _, results = process(
            [full],
            Reshape((width, height), Image.BOX),
            WebpQualityOptions(settings["qualities"], Stretch(), reference=[full]),
        )
        coefficients = results.of(WebpQualityOptions)["coefficients"]
        for option in results.of(WebpQualityOptions)["options"][0]:
            options.append(
                {
                    **index_entry(
                        region,
                        latitude,
                        longitude,
                        width,
                        height,
                        coefficients[0]["a"],
                        coefficients[0]["b"],
                    ),
                    "data": option["data"],
                    "error": option["error"],
                    "detail_loss": option["detail_loss"],
                    "area": width_factor,
                    "relief": relief,
                    "mid_latitude": mid_latitude,
                }
            )
    return options


def get_weight(option, settings):
    """
    How much the error of a tile counts: for the ground area it covers, for more where there is more relief (as peaks
    are lost first), and for less where few people hike.
    """
    latitude_importance = min(
        [
            weight
            for from_latitude, weight in settings["latitude_importance"]
            if abs(option["mid_latitude"]) >= from_latitude
        ],
        default=1,
    )
    return option["area"] * (1 + option["relief"] / settings["relief_scale"]) * latitude_importance


def choose_options(tile_options, settings):
    """Chooses an option for each tile which fits in the budget with the least total cost."""
    return fit_to_budget(
        tile_options,
        settings["size_budget_bytes"],
        size=lambda option: len(option["data"]),
        cost=lambda option: get_weight(option, settings)
        * (option["error"] + settings["detail_weight"] * option["detail_loss"]),
    )


def index_entry(region, latitude, longitude, width, height, a, b):
    """The details the app needs to read a tile (value = pixel / a - b)."""
    return {
        "filename": f"{region}.webp",
        "a": float(a),
        "b": float(b),
        "latitude_start": float(latitude),
        "longitude_start": float(longitude),
        "latitude_end": float(latitude - resolution),
        "longitude_end": float(longitude + resolution),
        "width": int(width),
        "height": int(height),
    }


def parse_region(region):
    """The latitude and longitude of the top left corner of a region, like N75W180."""
    match = re.search(r"([NS])(\d{2})([EW])(\d{3})", region)
    if not match:
        return None
    north_south, latitude, east_west, longitude = match.groups()
    return (
        int(latitude) * (1 if north_south == "N" else -1),
        int(longitude) * (1 if east_west == "E" else -1),
    )


def get_land_masks(file, region, latitude, longitude):
    """
    The land of a tile as two masks (True where it is land): one without the ocean and one without the ocean or inland
    water (the ocean is kept apart from inland water so that it can be stored as a water channel).
    """
    bounds = (longitude, latitude - resolution, longitude + resolution, latitude)

    # While the source image removes most of the water, this will get ones missed in the US
    # Look into switching to https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod44w-061
    source_ids = load_pixels(file.replace("surface", "surface_sid"))
    elevation, _ = process(
        [file],
        RemoveBathymetry(source_ids, land_ids_overrides.get(region, default_land_ids), bounds),
    )
    land, _ = process(elevation, ToMask())
    dry_land, _ = process(
        elevation,
        RemoveInlandWater(
            scale=2,
            dilation=-1,
            only_replace_negative_pixels=True,
            bbox=bounds,
        ),
        # This image has inland water that is not properly masked
        Conditional(region == "S30W060", Mask(lambda image: image < 0)),
        ToMask(),
    )
    return land[0], dry_land[0]


def save_high_tile(file, region, latitude, longitude):
    """16-bit lossless, split across two channels, with a water channel (ocean, inland water, or land)."""
    land, dry_land = get_land_masks(file, region, latitude, longitude)
    tiles, _ = process([file], Mask(dry_land, invert=True), RemoveEmpty(2))
    if not tiles:
        return None

    # Each step is 4 meters above the lowest point of the tile
    a = 0.25
    b = -np.min(tiles[0])
    process(
        tiles,
        LinearCompression(a, b),
        Quantize(np.uint16),
        Split16Bits(),
        AppendWaterChannel(land, dry_land),
        Save([f"output/dem/{region}.webp"], quality=100, lossless=True),
    )
    return index_entry(region, latitude, longitude, tile_pixels, tile_pixels, a, b)


def save_medium_tile(file, region, latitude, longitude):
    """Stretched to 8 bits, at the source resolution."""
    _, dry_land = get_land_masks(file, region, latitude, longitude)
    tiles, results = process(
        [file],
        Mask(dry_land, invert=True),
        RemoveEmpty(2),
        Stretch(),
        Save([f"output/dem/{region}.webp"], quality=100, lossless=False),
    )
    if not tiles:
        return None

    coefficients = results.of(LinearCompression)["coefficients"][0]
    return index_entry(region, latitude, longitude, tile_pixels, tile_pixels, coefficients["a"], coefficients["b"])


def get_dry_land_tile(file, region, latitude, longitude):
    """The elevation of a tile with the water removed (cached, since finding the water is slow)."""
    path = f"{cache_directory}/land/{region}.npy"
    if os.path.exists(path):
        return np.load(path)
    _, dry_land = get_land_masks(file, region, latitude, longitude)
    tiles, _ = process([file], Mask(dry_land, invert=True))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.save(path, tiles[0])
    return tiles[0]


def get_options_cache_path(settings, ignore_threshold, region):
    """
    Where the options of a tile are saved. They change with the settings which affect the images and with the code that
    makes them, but not with the settings that only affect the choice between them (the budget and the cost of each option).
    """
    image_settings = {key: settings[key] for key in ("scales", "qualities")}
    code = inspect.getsource(get_tile_options) + inspect.getsource(WebpQualityOptions) + inspect.getsource(encode_gray)
    key = hashlib.sha1(json.dumps([image_settings, ignore_threshold, code]).encode()).hexdigest()[:12]
    return f"{cache_directory}/options/{key}/{region}.pkl"


def get_lossy_tile_options(settings, ignore_threshold, file, region, latitude, longitude):
    """Every resolution and quality a tile could be saved as (the best is chosen once all of the tiles have options)."""
    path = get_options_cache_path(settings, ignore_threshold, region)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)

    tiles, _ = process([get_dry_land_tile(file, region, latitude, longitude)], RemoveEmpty(ignore_threshold))
    options = get_tile_options(region, tiles[0], latitude, longitude, settings) if tiles else None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(options, f)
    return options


presets = [
    {
        "id": "high",
        "compression_method": "16-bit",
        "has_water_mask": True,
        "resolution_arc_seconds": resolution,
        "tile": save_high_tile,
    },
    {
        "id": "medium",
        "compression_method": "8-bit",
        "has_water_mask": False,
        "resolution_arc_seconds": resolution,
        "tile": save_medium_tile,
    },
    {
        "id": "low",
        "compression_method": "8-bit",
        "has_water_mask": False,
        "budget": low,
        "tile": partial(get_lossy_tile_options, low, 8),
    },
    {
        "id": "mini",
        "compression_method": "8-bit",
        "has_water_mask": False,
        "budget": mini,
        "tile": partial(get_lossy_tile_options, mini, 20),
    },
]


def process_tile(file, preset):
    """Saves a tile (or finds its options) for a preset, or returns None if the tile is skipped."""
    region = file.split("_")[-2]

    if region.startswith(("S60", "S75", "N90")):
        return None

    position = parse_region(region)
    if position is None:
        print(f"Invalid region format: {region}")
        return None

    return preset["tile"](file, region, *position)


etopo.download(surface_resolution=resolution)
natural_earth.download()

for preset in presets:
    if preset_filter is not None and preset["id"] != preset_filter:
        continue

    budget = preset.get("budget")
    current_version = f'{version}-{preset["id"]}'
    true_resolution = preset.get("resolution_arc_seconds")

    os.makedirs("output/dem", exist_ok=True)
    for file in os.listdir("output/dem"):
        os.remove(os.path.join("output/dem", file))

    files = etopo.get_file_paths(resolution, "surface")
    tiles = []
    with progress.progress(f'Processing DEM files ({preset["id"]})', len(files)) as pbar:
        # The tiles are independent (the lossy ones are slow to find the water of and to encode). A few low priority
        # workers keep the computer usable while this runs.
        with ProcessPoolExecutor(max_workers=max_workers, initializer=os.nice, initargs=(19,)) as executor:
            for tile in executor.map(process_tile, files, repeat(preset)):
                if tile is not None:
                    tiles.append(tile)
                pbar.update(1)

    if budget:
        chosen = choose_options(tiles, budget)
        heights = sorted(option["height"] for option in chosen)
        true_resolution = int(resolution * tile_pixels / heights[len(heights) // 2])
        total_size = sum(len(option["data"]) for option in chosen)
        print(f'Chose {total_size / 1000:.0f} KB of the {budget["size_budget_bytes"] / 1000:.0f} KB budget')

        for option in chosen:
            with open(f'output/dem/{option["filename"]}', "wb") as f:
                f.write(option["data"])
        tiles = [
            {
                key: value
                for key, value in option.items()
                if key not in ("data", "error", "detail_loss", "area", "relief", "mid_latitude")
            }
            for option in chosen
        ]

    with open("output/dem/index.json", "w") as f:
        index = json.dumps(
            {
                "compression_method": preset["compression_method"],
                "has_water_mask": preset["has_water_mask"],
                "version": current_version,
                "resolution_arc_seconds": true_resolution,
                "files": tiles,
            }
        )
        index = re.sub(r"\s", "", index)
        f.write(index)

    # Compress the contents of the dem directory to a zip file
    with zipfile.ZipFile(f"output/dem-{current_version}.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, names in os.walk("output/dem"):
            for name in names:
                path = os.path.join(root, name)
                zipf.write(path, os.path.relpath(path, "output/dem"))
