from .interfaces import ImageOperator
import numpy as np


class ClassifyColors(ImageOperator):
    """
    Converts each image to a color image, where each pixel is the color of the last rule it matches (or the default
    color if it matches none). The rules are (color, condition) pairs, where the condition is a function of the image
    which returns a mask.
    """

    def __init__(self, default, rules):
        self.default = default
        self.rules = rules

    def apply(self, images):
        output = []
        for image in images:
            colors = np.full((*image.shape[:2], 3), self.default, dtype=np.uint8)
            for color, condition in self.rules:
                colors[condition(image)] = color
            output.append(colors)
        return output, {}
