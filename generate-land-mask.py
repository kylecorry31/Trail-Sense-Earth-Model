from scripts import natural_earth
from scripts.operators import process, RemoveWater, Save
import numpy as np

natural_earth.download()

# A white image of 360x180 degrees, with the water removed
process(
    [np.full((2100, 4200), 255, dtype=np.uint8)],
    RemoveWater(dilation=0, scale=2),
    Save(["output/land.webp"], quality=100, lossless=True),
)
