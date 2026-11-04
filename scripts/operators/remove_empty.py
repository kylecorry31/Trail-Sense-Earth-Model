from .interfaces import ImageOperator
import numpy as np


class RemoveEmpty(ImageOperator):
    """Removes the images where every pixel is below the threshold (ex. a tile of only ocean)."""

    def __init__(self, threshold):
        self.threshold = threshold

    def apply(self, images):
        return [image for image in images if not np.all(image < self.threshold)], {}
