from .interfaces import ImageOperator
import numpy as np


class PolarToCartesian(ImageOperator):
    """
    Converts consecutive pairs of [magnitude, angle (degrees)] images to [x, y] images. Pixels where either image
    is the invalid value are set to the invalid value.
    """

    def __init__(self, invalid_value=-999):
        self.invalid_value = invalid_value

    def apply(self, images):
        output = []
        for magnitude, angle in zip(images[0::2], images[1::2]):
            valid = (magnitude != self.invalid_value) & (angle != self.invalid_value)
            radians = np.radians(np.where(valid, angle, 0))
            output.append(np.where(valid, magnitude * np.cos(radians), self.invalid_value))
            output.append(np.where(valid, magnitude * np.sin(radians), self.invalid_value))
        return output, {}
