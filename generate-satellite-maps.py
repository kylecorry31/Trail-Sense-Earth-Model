from scripts import visible_earth, natural_earth
import numpy as np

from scripts.operators import (
    process,
    ClassifyColors,
    FillPolarRegions,
    ReplaceColorInPolarRegions,
    SmoothColors,
    RemoveSmallRegionsOfColors,
    GrowColors,
    RemoveWater,
    Resize,
    Save,
    Min,
    Type,
)

# INPUT
# https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Maps/Conventions/Topographic_maps
DESERT = (232, 225, 182)
# RAINFOREST = (168, 198, 143)
ROCK = (202, 195, 184)
GRASS = (184, 201, 166)
ICE = (245, 244, 242)
WATER = (0, 0, 0)
INLAND_WATER = (127, 127, 127)


# Ordered from the color that should win the most to the least
colors = [
    ICE,
    # RAINFOREST,
    GRASS,
    ROCK,
    DESERT,
]

min_hole_size_percent = 0.007
smoothing_iterations = 5
water = [WATER, INLAND_WATER]

######## Program, don't modify ########
visible_earth.download()
visible_earth.process_maps()
natural_earth.download()

process(
    [f"images/world-map-{month}.tif" for month in range(1, 13)],
    # Consolidate the satellite images into one
    Min(),
    Type(np.uint8),
    RemoveWater(dilation=0, scale=2, inland_replacement=INLAND_WATER[0]),
    ClassifyColors(
        DESERT,
        [
            (GRASS, lambda image: (np.mean(image, axis=-1) < 100) & (image[..., 1] > image[..., 0])),
            # r, g, and b above a threshold
            (ICE, lambda image: np.all(image >= 150, axis=-1)),
        ],
    ),
    FillPolarRegions(ICE, north=75, south=-60),
    ReplaceColorInPolarRegions(DESERT, ROCK, north=55, south=-55),
    # Remove water features again to clean up edges
    RemoveWater(dilation=0, scale=2, inland_replacement=INLAND_WATER[0]),
    SmoothColors(
        colors,
        smoothing_iterations=smoothing_iterations,
        min_hole_size=min_hole_size_percent,
        min_hole_size_is_percent=True,
    ),
    # Fill noise
    RemoveSmallRegionsOfColors(colors, 100, invalid_colors=water, search_space=30),
    # Grow all colors for extra noise reduction
    GrowColors(colors, structure=np.ones((3, 3)), iterations=8),
    # Fill noise again
    RemoveSmallRegionsOfColors(colors, 60, invalid_colors=water, search_space=30),
    RemoveWater(dilation=0, scale=2, inland_replacement=INLAND_WATER[0]),
    Resize((3800, 3800)),
    Save(["output/world-map.webp"], quality=100, lossless=True),
    show_progress=True,
)
