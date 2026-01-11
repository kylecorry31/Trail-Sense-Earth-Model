from scripts import etopo, natural_earth, progress, load_pixels
from scripts.operators import process
from scripts.operators.compression import Split16Bits, LinearCompression
from scripts.operators.basic import Conditional, Group, Map, Reshape, Save, Type
from PIL import Image
import numpy as np
import os
import re
import json
import zipfile

from scripts.operators.masking import Mask, RemoveInlandWater, RemoveOceans

version = "0.3.0"
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
    },
    {
        "id": "medium",
        "scale": 1.0,
        "compress_images": True,
        "compression_quality": 100,
        "above_N60_quality": 100,
        "above_N60_scale": 1.0,
        "ignore_threshold": 2,
    },
    {
        "id": "low",
        "scale": 0.75,
        "compress_images": True,
        "compression_quality": 90,
        "above_N60_quality": 60,
        "above_N60_scale": 0.75,
        "ignore_threshold": 8,
    },
    {
        "id": "mini",
        "scale": 0.25,
        "compress_images": True,
        "compression_quality": 75,
        "above_N60_quality": 10,
        "above_N60_scale": 0.1,
        "ignore_threshold": 20,
    },
]

# Increase the maximum image pixel limit to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = None
resolution = 15

etopo.download(surface_resolution=resolution)
natural_earth.download()

for preset in presets:
    if preset_filter is not None and preset["id"] != preset_filter:
        continue

    scale = preset["scale"]
    compress_images = preset["compress_images"]
    compression_quality = preset["compression_quality"]
    ignore_threshold = preset["ignore_threshold"]
    above_N60_quality = preset["above_N60_quality"]
    above_N60_scale = preset["above_N60_scale"]

    current_version = f'{version}-{preset["id"]}'

    true_resolution = int(resolution / scale)

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

            mask, _ = process(
                [file],
                RemoveOceans(
                    scale=2,
                    dilation=-20,
                    only_replace_negative_pixels=True,
                    bbox=(longitude, end_latitude, end_longitude, latitude),
                ),
                RemoveInlandWater(
                    scale=2,
                    dilation=-1,
                    only_replace_negative_pixels=True,
                    bbox=(longitude, end_latitude, end_longitude, latitude),
                ),
                # Remove bathymetry areas based on the sid image
                Mask(~np.isin(source_image, [9, 10, 11, 13])),
                # If it is 13 and below 0, set it to 0 (13 is US coastline)
                Mask(lambda image: (source_image == 13) & (image < 0)),
                # Image is not allowed to be lower than the lowest place on land
                Mask(lambda image: image < -430.5),
                # This image has inland water that is not properly masked
                Conditional(region == "S30W060", Mask(lambda image: image < 0)),
                Type(np.bool),
            )
            mask = mask[0]

            # Reapply the mask
            image, _ = process([file], Mask(mask, invert=True), Reshape(image_size))
            image = image[0]

            # Skip images with no valid land data
            if np.all(image < ignore_threshold):
                pbar.update(1)
                continue

            if compress_images:
                # 8-bit compression
                _, results = process(
                    [image],
                    LinearCompression(),
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
                _, results = process(
                    [image],
                    LinearCompression(a, b),
                    Map(lambda image: np.rint(image)),
                    Type(np.uint16),
                    Split16Bits(),
                    Save(
                        lambda: f"output/dem/{region}.webp",
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

    with open("output/dem/index.json", "w") as f:
        index = json.dumps(
            {
                "compression_method": "8-bit" if compress_images else "16-bit",
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
