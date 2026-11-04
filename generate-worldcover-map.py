from scripts import natural_earth, worldcover
import numpy as np

from scripts.operators import (
    process,
    ClassifyColors,
    FillPolarRegions,
    ReplaceColorInPolarRegions,
    SmoothColors,
    RemoveWater,
    Resize,
    Save,
)

# INPUT
# https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Maps/Conventions/Topographic_maps
DESERT = (232, 225, 182)
FOREST = (146, 181, 126)
ROCK = (202, 195, 184)
GRASS = (184, 201, 166)
ICE = (245, 244, 242)
WATER = (0, 0, 0)
INLAND_WATER = (127, 127, 127)


# Ordered from the color that should win the most to the least
colors = [
    ICE,
    FOREST,
    GRASS,
    ROCK,
    DESERT,
]

min_hole_size_percent = 0.00005
smoothing_iterations = 1

######## Program, don't modify ########
worldcover.download()
worldcover.process_map()
natural_earth.download()

process(
    ["images/worldcover-map.tif"],
    # WorldCover classes:
    # 10 tree, 20 shrub, 30 grass, 40 crop, 50 built-up, 60 bare,
    # 70 snow/ice, 80 water, 90 wetland, 95 mangrove, 100 moss/lichen.
    ClassifyColors(
        ROCK,
        [
            (GRASS, lambda image: np.isin(image, [20, 30, 40, 90])),
            (FOREST, lambda image: np.isin(image, [10, 95])),
            (DESERT, lambda image: image == 60),
            (ICE, lambda image: image == 70),
        ],
    ),
    # Antarctica
    FillPolarRegions(ICE, south=-60),
    ReplaceColorInPolarRegions(DESERT, ROCK, north=55, south=-55),
    RemoveWater(dilation=0, scale=2, inland_replacement=INLAND_WATER[0]),
    SmoothColors(
        colors,
        smoothing_iterations=smoothing_iterations,
        min_hole_size=min_hole_size_percent,
        min_hole_size_is_percent=True,
    ),
    # Remove water features again to clean up edges
    RemoveWater(dilation=0, scale=2, inland_replacement=INLAND_WATER[0]),
    Resize((3800, 3800)),
    Save(["output/worldcover-map.webp"], quality=100, lossless=True),
    show_progress=True,
)
