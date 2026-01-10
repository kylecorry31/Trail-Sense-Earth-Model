from scripts import load_pixels, visible_earth, natural_earth, compression, progress
import PIL.Image as Image
import numpy as np

from scripts.operators import process
from scripts.operators.basic import (
    Map,
    SmoothColor,
    RemoveSmallRegions,
    GrowColor,
    Resize,
    Save,
    Min,
    Type,
)
from scripts.operators.masking import RemoveOceans, RemoveInlandWater

visible_earth.download()
visible_earth.process_maps()

# https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Maps/Conventions/Topographic_maps
DESERT = (232, 225, 182)
# RAINFOREST = (168, 198, 143)
ROCK = (202, 195, 184)
GRASS = (189, 204, 150)
ICE = (245, 244, 242)
WATER = (0, 0, 0)
INLAND_WATER = (127, 127, 127)


# Define color mapping function
def map_colors(image):
    mean = np.mean(image, axis=-1)

    # Desert
    new_image = np.full_like(image, DESERT)

    # Grass
    mask = (mean < 100) & (image[..., 1] > image[..., 0])
    new_image[mask] = GRASS

    # Rainforests
    # mask = (np.mean(image, axis=-1) < 100) & (image[..., 1] > image[..., 0] * 1.05) & (image[..., 1] < 40) & (image[..., 2] < 10) & (image[..., 0] < 30)
    # new_image[mask] = RAINFOREST
    # pbar.update(1)

    # Ice (r, g, b above threshold)
    threshold = 150
    mask = np.all(image >= threshold, axis=-1)
    new_image[mask] = ICE

    # Fill all pixels near the poles with white
    north = 75
    south = -60
    height = image.shape[0]
    north_pixel = max(0, min(height, int((90 - north) / 180 * height)))
    south_pixel = max(0, min(height, int((90 - south) / 180 * height)))
    new_image[:north_pixel, :] = ICE
    new_image[south_pixel:, :] = ICE

    # Replace all desert color near the poles with rock
    north = 55
    south = -55
    north_pixel = max(0, min(height, int((90 - north) / 180 * height)))
    south_pixel = max(0, min(height, int((90 - south) / 180 * height)))
    mask = (new_image[:north_pixel, :] == DESERT).all(axis=-1)
    new_image[:north_pixel, :][mask] = ROCK
    mask = (new_image[south_pixel:, :] == DESERT).all(axis=-1)
    new_image[south_pixel:, :][mask] = ROCK

    return new_image


smoothing_order = [
    ICE,
    # RAINFOREST,
    GRASS,
    ROCK,
    DESERT,
]

min_hole_size_percent = 0.007
smoothing_iterations = 5

operators = [
    # Consolidate the satellite images into one
    Min(),
    Type(np.uint8),
    # Remove water features
    RemoveOceans(dilation=0, scale=2),
    RemoveInlandWater(dilation=0, replacement=127, scale=2),
    # Map the land colors
    Map(map_colors),
    # Remove water features again to clean up edges
    RemoveOceans(dilation=0, scale=2),
    RemoveInlandWater(dilation=0, replacement=127, scale=2),
]

# Add smoothing operators
for color in smoothing_order:
    operators.append(
        SmoothColor(
            color,
            smoothing_iterations=smoothing_iterations,
            min_hole_size=min_hole_size_percent,
            min_hole_size_is_percent=True,
        )
    )

for color in reversed(smoothing_order):
    operators.append(
        SmoothColor(
            color,
            smoothing_iterations=smoothing_iterations,
            min_hole_size=min_hole_size_percent,
            min_hole_size_is_percent=True,
        )
    )

# Fill noise
for color in smoothing_order:
    operators.append(
        RemoveSmallRegions(
            color, 100, invalid_colors=[WATER, INLAND_WATER], search_space=30
        )
    )

# Grow all colors for extra noise reduction
for color in smoothing_order:
    operators.append(GrowColor(color, structure=np.ones((3, 3)), iterations=8))

# Fill noise again
for color in smoothing_order:
    operators.append(
        RemoveSmallRegions(
            color, 60, invalid_colors=[WATER, INLAND_WATER], search_space=30
        )
    )

operators.extend(
    [
        # Remove water features again to clean up edges
        RemoveOceans(dilation=0, scale=2),
        RemoveInlandWater(dilation=0, replacement=127, scale=2),
        Resize((3800, 3800)),
        Save(["output/world-map.webp"], quality=100, lossless=True),
    ]
)

process(
    [f"images/world-map-{month}.tif" for month in range(1, 13)],
    *operators,
    show_progress=True,
)
