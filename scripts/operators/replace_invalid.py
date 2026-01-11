from .interfaces import ImageOperator
import numpy as np


class ReplaceInvalid(ImageOperator):
    def __init__(self, replacement=0):
        self.replacement = replacement

    def apply(self, images):
        output = []
        for image in images:
            values_array = np.ma.masked_invalid(image)
            output.append(np.where(values_array.mask, self.replacement, values_array))
        return output, {}
