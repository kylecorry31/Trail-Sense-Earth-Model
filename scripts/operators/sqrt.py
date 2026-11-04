from .interfaces import ImageOperator
import numpy as np


class Sqrt(ImageOperator):
    """Takes the square root of the values of each image (which must not be negative, see Clip)."""

    def apply(self, images):
        return [np.sqrt(image) for image in images], {}
