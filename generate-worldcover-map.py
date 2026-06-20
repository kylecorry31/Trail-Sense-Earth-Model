from scripts import natural_earth, worldcover
import numpy as np

from scripts.operators import (
    process,
    Map,
    SmoothColor,
    Resize,
    Save,
    RemoveOceans,
    RemoveInlandWater,
)

worldcover.download()
worldcover.process_map()
natural_earth.download()

# https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Maps/Conventions/Topographic_maps
DESERT = (232, 225, 182)
FOREST = (146, 181, 126)
ROCK = (202, 195, 184)
GRASS = (184, 201, 166)
ICE = (245, 244, 242)
WATER = (0, 0, 0)
INLAND_WATER = (127, 127, 127)


# Define color mapping function
def map_colors(image):
    height = image.shape[0]
    new_image = np.full((*image.shape, 3), ROCK, dtype=np.uint8)

    # WorldCover classes:
    # 10 tree, 20 shrub, 30 grass, 40 crop, 50 built-up, 60 bare,
    # 70 snow/ice, 80 water, 90 wetland, 95 mangrove, 100 moss/lichen.
    new_image[np.isin(image, [20, 30, 40, 90])] = GRASS
    new_image[np.isin(image, [10, 95])] = FOREST
    new_image[image == 60] = DESERT
    new_image[image == 70] = ICE

    # Fill all pixels in antarctica with ice
    south = -60
    south_pixel = max(0, min(height, int((90 - south) / 180 * height)))
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
    FOREST,
    GRASS,
    ROCK,
    DESERT,
]

min_hole_size_percent = 0.00005
smoothing_iterations = 1

operators = [
    # Map the land colors
    Map(map_colors),
    # Remove water features
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

operators.extend(
    [
        # Remove water features again to clean up edges
        RemoveOceans(dilation=0, scale=2),
        RemoveInlandWater(dilation=0, replacement=127, scale=2),
        Resize((3800, 3800)),
        Save(["output/worldcover-map.webp"], quality=100, lossless=True),
    ]
)

process(
    ["images/worldcover-map.tif"],
    *operators,
    show_progress=True,
)
