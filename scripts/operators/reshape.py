from .interfaces import ImageOperator
from PIL import Image
import numpy as np


class Reshape(ImageOperator):
    def __init__(self, shape):
        self.shape = shape

    def apply(self, images):
        if self.shape is None:
            return images, {}
        output = []
        for image in images:
            img = Image.fromarray(image).resize(self.shape, Image.NEAREST)
            output.append(np.array(img).reshape((self.shape[1], self.shape[0])))
        return output, {}
