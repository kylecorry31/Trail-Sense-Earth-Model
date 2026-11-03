from scripts import etopo, natural_earth, progress, load_pixels
from scripts.size_budget import fit_to_budget
from scripts.operators import process, Split16Bits, LinearCompression, Conditional, Map, Reshape, WebpQualityOptions, Save, Type, Mask, RemoveInlandWater, RemoveOceans
from PIL import Image
import numpy as np
import os
import re
import json
import math
import zipfile

version = "0.5.0"
preset_filter = None

presets = [
    {
        "id": "high",
        "scale": 1.0,
        "compress_images": False,
        "compression_quality": 100,
        "above_N60_quality": 100,
        "above_N60_scale": 1.0,
        "ignore_threshold": 2,
        "ocean_mask": True,
    },
    {
        "id": "medium",
        "scale": 1.0,
        "compress_images": True,
        "compression_quality": 100,
        "above_N60_quality": 100,
        "above_N60_scale": 1.0,
        "ignore_threshold": 2,
        "ocean_mask": False,
    },
    {
        "id": "low",
        "compress_images": True,
        "ignore_threshold": 8,
        "ocean_mask": False,
        "optimize": {
            "scales": [0.5, 0.65, 0.8, 1.0],
            "qualities": [60, 75, 90, 95],
            "size_budget_bytes": 20_000_000,
            "relief_scale": 1000,
            "latitude_importance": [(60, 0.3)],
            "detail_weight": 150,
        },
    },
    {
        "id": "mini",
        "compress_images": True,
        "ignore_threshold": 20,
        "ocean_mask": False,
        # Picks the resolution and quality of each tile to minimize the error within the size budget
        "optimize": {
            "scales": [0.1, 0.15, 0.2, 0.25, 0.3, 0.4],
            "qualities": [50, 65, 75, 85, 95],
            "size_budget_bytes": 2_250_000,
            # A tile's error counts for more the more relief it has (+1x per this many meters), as its peaks are lost first
            "relief_scale": 1000,
            # ...and for less where few people hike: (latitude from, importance)
            "latitude_importance": [(60, 0.3)],
            # Losing all of a tile's detail (the elevation changes that make up the gain of a route) counts as this many meters of error
            "detail_weight": 150,
        },
    },
]

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None
resolution = 15


def get_tile_options(region, full, latitude, longitude, optimize):
    """Every resolution and quality a tile could be saved as, with the cost of each for choosing between them."""
    # Tiles are narrower in the ground distance they cover towards the poles
    mid_latitude = latitude - resolution / 2
    width_factor = math.cos(math.radians(mid_latitude))

    # Errors count for more where there is more relief, as peaks are lost first, and for less where few people hike
    relief = float(full.max() - full.min())
    importance = (1 + relief / optimize["relief_scale"]) * min(
        [
            weight
            for from_latitude, weight in optimize["latitude_importance"]
            if abs(mid_latitude) >= from_latitude
        ],
        default=1,
    )

    options = []
    for option_scale in optimize["scales"]:
        height = int(full.shape[0] * option_scale)
        width = int(height * width_factor)
        images, results = process(
            [full],
            Reshape((width, height), Image.BOX),
            LinearCompression(),
            Map(lambda image: np.rint(image)),
            Type(np.uint8),
        )
        coefficients = results[1]["coefficients"]
        _, results = process(
            images,
            WebpQualityOptions(optimize["qualities"], [full], coefficients),
        )
        for option in results[0]["options"][0]:
            options.append(
                {
                    "filename": f"{region}.webp",
                    "a": float(coefficients[0]["a"]),
                    "b": float(coefficients[0]["b"]),
                    "latitude_start": float(latitude),
                    "longitude_start": float(longitude),
                    "latitude_end": float(latitude - resolution),
                    "longitude_end": float(longitude + resolution),
                    "width": width,
                    "height": height,
                    "data": option["data"],
                    "error": option["error"],
                    "detail_loss": option["detail_loss"],
                    # Errors are weighted by the ground area the tile covers
                    "weight": width_factor * importance,
                }
            )
    return options


def choose_options(tile_options, optimize):
    """Chooses an option for each tile which fits in the budget with the least total cost."""
    return fit_to_budget(
        tile_options,
        optimize["size_budget_bytes"],
        size=lambda option: len(option["data"]),
        cost=lambda option: option["weight"]
        * (option["error"] + optimize["detail_weight"] * option["detail_loss"]),
    )


etopo.download(surface_resolution=resolution)
natural_earth.download()

for preset in presets:
    if preset_filter is not None and preset["id"] != preset_filter:
        continue

    scale = preset.get("scale")
    compress_images = preset["compress_images"]
    compression_quality = preset.get("compression_quality")
    ignore_threshold = preset["ignore_threshold"]
    above_N60_quality = preset.get("above_N60_quality")
    above_N60_scale = preset.get("above_N60_scale")
    use_ocean_mask = preset.get("ocean_mask", False)
    optimize = preset.get("optimize")
    tile_options = []

    current_version = f'{version}-{preset["id"]}'

    true_resolution = int(resolution / scale) if scale else None

    files = etopo.get_file_paths(resolution, "surface")

    if os.path.exists("output/dem"):
        for file in os.listdir("output/dem"):
            os.remove(os.path.join("output/dem", file))

    if not os.path.exists("output/dem"):
        os.makedirs("output/dem")

    with progress.progress(
        f'Processing DEM files ({preset["id"]})', len(files)
    ) as pbar:
        compression_factors = []
        for file in files:
            region = file.split("_")[-2]

            if (
                region.startswith("S60")
                or region.startswith("S75")
                or region.startswith("N90")
            ):
                pbar.update(1)
                continue

            # N75 covers 60 - 75, 75-90 are already removed
            actual_quality = (
                above_N60_quality if region.startswith("N75") else compression_quality
            )
            actual_scale = above_N60_scale if region.startswith("N75") else scale

            # First letter is either N or S followed by 2 digits and E or W and then 3 digits
            regex = r"([NS]\d{2})([EW]\d{3})"
            match = re.search(regex, region)
            if not match:
                print(f"Invalid region format: {region}")
                pbar.update(1)
                continue
            latitude, longitude = match.groups()

            latitude = int(latitude[1:]) * (1 if latitude[0] == "N" else -1)
            longitude = int(longitude[1:]) * (1 if longitude[0] == "E" else -1)

            end_latitude = latitude - resolution
            end_longitude = longitude + resolution

            initial_size = 3600
            image_size = (
                (int(initial_size * actual_scale), int(initial_size * actual_scale))
                if actual_scale is not None
                else None
            )

            # While the source image removes most of the water, this will get ones missed in the US
            # Look into switching to https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod44w-061

            source_image = load_pixels(file.replace("surface", "surface_sid"))

            valid_sid_overrides = {
                'N45E030': [1, 9, 10, 11, 13],
                'N45E045': [1, 9, 10, 11, 13],
            }

            pre_mask, _ = process(
                [file],
                RemoveOceans(
                    scale=2,
                    dilation=-20,
                    only_replace_negative_pixels=True,
                    bbox=(longitude, end_latitude, end_longitude, latitude),
                ),
                # Remove bathymetry areas based on the sid image
                Mask(~np.isin(source_image, valid_sid_overrides.get(region, [9, 10, 11, 13]))),
                # If it is 13 and below 0, set it to 0 (13 is US coastline)
                Mask(lambda image: (source_image == 13) & (image < 0)),
                # Image is not allowed to be lower than the lowest place on land
                Mask(lambda image: image < -430.5),
            )
            pre_mask = pre_mask[0]

            if use_ocean_mask:
                ocean_mask, _ = process([pre_mask], Type(np.bool))
                ocean_mask = ocean_mask[0]

            mask, _ = process(
                [pre_mask],
                RemoveInlandWater(
                    scale=2,
                    dilation=-1,
                    only_replace_negative_pixels=True,
                    bbox=(longitude, end_latitude, end_longitude, latitude),
                ),
                # This image has inland water that is not properly masked
                Conditional(region == "S30W060", Mask(lambda image: image < 0)),
                Type(np.bool),
            )
            mask = mask[0]

            if optimize:
                full, _ = process([file], Mask(mask, invert=True))
                if not np.all(full[0] < ignore_threshold):
                    tile_options.append(
                        get_tile_options(region, full[0], latitude, longitude, optimize)
                    )
                pbar.update(1)
                continue

            # Reapply the mask
            image, _ = process([file], Mask(mask, invert=True), Reshape(image_size))
            image = image[0]

            # Water channel: 255 = ocean, 127 = inland water, 0 = land
            if use_ocean_mask:
                water_channel = np.where(~ocean_mask, 255, np.where(~mask, 127, 0)).astype(np.uint8)
                ocean_channel, _ = process([water_channel], Reshape(image_size))
                ocean_channel = ocean_channel[0]

            # Skip images with no valid land data
            if np.all(image < ignore_threshold):
                pbar.update(1)
                continue

            if compress_images:
                # 8-bit compression
                _, results = process(
                    [image],
                    LinearCompression(),
                    Map(lambda image: np.rint(image)),
                    Type(np.uint8),
                    Save(
                        [f"output/dem/{region}.webp"],
                        quality=actual_quality,
                        lossless=False,
                    ),
                )

                coefficients = results[0].get("coefficients", [{}])[0]
                a = coefficients.get("a", 1.0)
                b = coefficients.get("b", 0.0)
                compression_factors.append(
                    {
                        "filename": f"{region}.webp",
                        "a": float(a),
                        "b": float(b),
                        "latitude_start": float(latitude),
                        "longitude_start": float(longitude),
                        "latitude_end": float(end_latitude),
                        "longitude_end": float(end_longitude),
                        "width": int(image_size[0]),
                        "height": int(image_size[1]),
                    }
                )
            else:
                # 16-bit compression
                min_val = np.min(image)
                a = 0.25
                b = -min_val
                _ocean_channel = ocean_channel if use_ocean_mask else None
                _, results = process(
                    [image],
                    LinearCompression(a, b),
                    Map(lambda image: np.rint(image)),
                    Type(np.uint16),
                    Split16Bits(),
                    *([Map(lambda image: np.dstack([image, _ocean_channel]))] if use_ocean_mask else []),
                    Save(
                        lambda i: f"output/dem/{region}.webp",
                        quality=100,
                        lossless=True,
                    ),
                )
                compression_factors.append(
                    {
                        "filename": f"{region}.webp",
                        "a": float(a),
                        "b": float(b),
                        "latitude_start": float(latitude),
                        "longitude_start": float(longitude),
                        "latitude_end": float(end_latitude),
                        "longitude_end": float(end_longitude),
                        "width": int(image_size[0]),
                        "height": int(image_size[1]),
                    }
                )
            pbar.update(1)

    if optimize:
        chosen = choose_options(tile_options, optimize)
        heights = sorted(option["height"] for option in chosen)
        true_resolution = int(resolution * 3600 / heights[len(heights) // 2])
        total_size = sum(len(option["data"]) for option in chosen)
        print(f'Chose {total_size / 1000:.0f} KB of the {optimize["size_budget_bytes"] / 1000:.0f} KB budget')

        for option in chosen:
            with open(f'output/dem/{option["filename"]}', "wb") as f:
                f.write(option["data"])
            compression_factors.append(
                {
                    key: value
                    for key, value in option.items()
                    if key not in ("data", "error", "detail_loss", "weight")
                }
            )

    with open("output/dem/index.json", "w") as f:
        index = json.dumps(
            {
                "compression_method": "8-bit" if compress_images else "16-bit",
                "has_water_mask": use_ocean_mask,
                "version": current_version,
                "resolution_arc_seconds": true_resolution,
                "files": compression_factors,
            }
        )
        index = re.sub(r"\s", "", index)
        f.write(index)

    # Compress the contents of the dem directory to a zip file
    with zipfile.ZipFile(
        f"output/dem-{current_version}.zip", "w", zipfile.ZIP_DEFLATED
    ) as zipf:
        for root, dirs, files in os.walk("output/dem"):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), "output/dem"),
                )
