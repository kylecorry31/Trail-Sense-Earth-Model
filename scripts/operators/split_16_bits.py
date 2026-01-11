from .interfaces import ImageOperator
import numpy as np


class Split16Bits(ImageOperator):
    def __init__(self, stack=True):
        self.stack = stack

    def apply(self, images):
        output = []
        for image in images:
            lower_bits = (image & 0xFF).astype(np.uint8)
            upper_bits = ((image >> 8) & 0xFF).astype(np.uint8)
            if self.stack:
                stacked = np.dstack([lower_bits, upper_bits])
                output.append(stacked)
            else:
                output.append(lower_bits)
                output.append(upper_bits)
        return output, {}
