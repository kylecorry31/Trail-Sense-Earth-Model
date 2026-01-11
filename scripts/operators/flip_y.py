from .interfaces import ImageOperator
import numpy as np


class FlipY(ImageOperator):
    def apply(self, images):
        output = []
        for image in images:
            output.append(np.flipud(image))
        return output, {}
