from .interfaces import ImageOperator
import numpy as np


class CartesianToPolar(ImageOperator):
    """
    Converts consecutive pairs of [x, y] images to [magnitude, angle (degrees, -180 to 180)] images. Pixels where
    either image is the invalid value are set to the invalid value.
    """

    def __init__(self, invalid_value=-999):
        self.invalid_value = invalid_value

    def apply(self, images):
        output = []
        for x, y in zip(images[0::2], images[1::2]):
            valid = (x != self.invalid_value) & (y != self.invalid_value)
            output.append(np.where(valid, np.hypot(x, y), self.invalid_value))
            output.append(np.where(valid, np.degrees(np.arctan2(y, x)), self.invalid_value))
        return output, {}
