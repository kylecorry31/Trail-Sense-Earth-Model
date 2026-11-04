from .append_channel import AppendChannel
from .reshape import Reshape
from .interfaces import ImageOperator
import numpy as np

OCEAN = 255
INLAND_WATER = 127
LAND = 0


class AppendWaterChannel(ImageOperator):
    """
    Appends a water channel to each image (OCEAN = 255, INLAND_WATER = 127, LAND = 0), resized to the size of the image.

    land: a mask of the land and inland water (True where it is not ocean)
    dry_land: a mask of the land (True where it is not ocean or inland water)
    """

    def __init__(self, land, dry_land):
        self.channel = np.where(
            ~land, OCEAN, np.where(~dry_land, INLAND_WATER, LAND)
        ).astype(np.uint8)

    def apply(self, images):
        output = []
        for image in images:
            height, width = image.shape[:2]
            channel, _ = Reshape((width, height)).apply([self.channel])
            appended, _ = AppendChannel(channel[0]).apply([image])
            output.extend(appended)
        return output, {}
