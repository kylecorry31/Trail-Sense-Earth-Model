from .interfaces import ImageOperator
import numpy as np


class Clip(ImageOperator):
    """Limits the values of each image to the range (either end can be left open with None)."""

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def apply(self, images):
        return [np.clip(image, self.min, self.max) for image in images], {}
