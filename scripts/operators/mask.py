from .interfaces import ImageOperator
import numpy as np


class Mask(ImageOperator):
    def __init__(self, mask_image, invert=False, replacement=0):
        self.mask_image = mask_image
        self.invert = invert
        self.replacement = replacement

    def apply(self, images):
        output = []
        for image in images:
            masked_image = np.copy(image)
            mask = self.mask_image if not callable(self.mask_image) else self.mask_image(image)
            if self.invert:
                mask = ~mask
            masked_image[mask] = self.replacement
            output.append(masked_image)
        return output, {}
