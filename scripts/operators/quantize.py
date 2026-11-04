from .interfaces import ImageOperator
import numpy as np


class Quantize(ImageOperator):
    """Rounds each image to the nearest integer and converts it to the integer type."""

    def __init__(self, type=np.uint8):
        self.type = type

    def apply(self, images):
        return [np.rint(image).astype(self.type) for image in images], {}
