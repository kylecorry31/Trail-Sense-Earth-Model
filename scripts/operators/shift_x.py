from .interfaces import ImageOperator
import numpy as np


class ShiftX(ImageOperator):
    def __init__(self, shift, is_percent=False):
        self.shift = shift
        self.is_percent = is_percent

    def apply(self, images):
        if self.shift == 0:
            return images, {}
        shift = self.shift
        output = []
        for image in images:
            if self.is_percent:
                shift = int(np.floor(image.shape[1] * self.shift))
            output.append(np.roll(image, shift, axis=1))
        return output, {}
