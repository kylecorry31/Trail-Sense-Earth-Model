from .interfaces import ImageOperator
import numpy as np


class BitwiseOr(ImageOperator):
    def apply(self, images):
        if len(images) == 0:
            return images, {}
        output_image = images[0].copy()
        for image in images[1:]:
            output_image = np.bitwise_or(output_image, image)
        return [output_image], {}
