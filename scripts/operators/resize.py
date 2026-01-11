from .interfaces import ImageOperator
from PIL import Image
import numpy as np


class Resize(ImageOperator):
    def __init__(self, max_size, resample=Image.NEAREST):
        self.max_size = max_size
        self.resample = resample

    def apply(self, images):
        output = []
        for image in images:
            img = Image.fromarray(image)
            img.thumbnail(self.max_size, resample=self.resample)
            output.append(np.array(img))
        return output, {}
