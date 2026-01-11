from .interfaces import ImageOperator
import numpy as np


class Replace(ImageOperator):
    def __init__(self, target_values, replacement=0, inverse=False):
        self.target_values = (
            target_values
            if isinstance(target_values, (list, tuple))
            else [target_values]
        )
        self.replacement = replacement
        self.inverse = inverse

    def apply(self, images):
        output = []
        for image in images:
            mask = np.isin(image, self.target_values)
            if self.inverse:
                mask = ~mask
            output.append(np.where(mask, self.replacement, image))
        return output, {}
