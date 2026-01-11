from .interfaces import ImageOperator
from .. import compression
import numpy as np


class GrowColor(ImageOperator):
    def __init__(self, color, structure=None, iterations=1):
        self.color = color
        self.iterations = iterations
        self.structure = structure if structure is not None else np.ones((3, 3))

    def apply(self, images):
        output = []
        for image in images:
            result = compression.grow_color(
                image, self.color, structure=self.structure, iterations=self.iterations
            )
            output.append(result)
        return output, {}
