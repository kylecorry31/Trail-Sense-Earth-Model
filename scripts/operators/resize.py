from .interfaces import ImageOperator
from PIL import Image
import numpy as np


class Resize(ImageOperator):
    def __init__(self, max_size, resample=Image.NEAREST, exact=False):
        self.max_size = max_size
        self.resample = resample
        self.exact = exact

    def apply(self, images):
        output = []
        for image in images:
            img = Image.fromarray(image)
            if self.exact:
                img = img.resize(self.max_size, self.resample)
            else:
                img.thumbnail(self.max_size, resample=self.resample)
            output.append(np.array(img))
        return output, {}
