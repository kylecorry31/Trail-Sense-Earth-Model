from .interfaces import ImageOperator
from PIL import Image
import numpy as np


class Reshape(ImageOperator):
    def __init__(self, shape, resample=Image.NEAREST):
        self.shape = shape
        self.resample = resample

    def apply(self, images):
        if self.shape is None:
            return images, {}
        output = []
        for image in images:
            if self.resample != Image.NEAREST:
                image = image.astype(np.float32)
            img = Image.fromarray(image).resize(self.shape, self.resample)
            output.append(np.array(img).reshape((self.shape[1], self.shape[0])))
        return output, {}
