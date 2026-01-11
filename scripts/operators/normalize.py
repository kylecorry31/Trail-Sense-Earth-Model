from .interfaces import ImageOperator
import numpy as np


class Normalize(ImageOperator):
    def __init__(self, min_value=None, max_value=None, invalid_value=-999):
        self.min_value = min_value
        self.max_value = max_value
        self.invalid_value = invalid_value

    def apply(self, images):
        minimum = self.min_value
        maximum = self.max_value
        if minimum is None:
            for image in images:
                new_minimum = (
                    np.min(image[image != self.invalid_value])
                    if self.invalid_value is not None
                    else np.min(image)
                )
                if minimum is None or new_minimum < minimum:
                    minimum = new_minimum
        if maximum is None:
            for image in images:
                new_maximum = (
                    np.max(image[image != self.invalid_value])
                    if self.invalid_value is not None
                    else np.max(image)
                )
                if maximum is None or new_maximum > maximum:
                    maximum = new_maximum

        data = {"minimum": minimum, "maximum": maximum}

        output = []
        for image in images:
            if self.invalid_value is None:
                result = (image - minimum) / (maximum - minimum)
            else:
                normalized = (image[image != self.invalid_value] - minimum) / (
                    maximum - minimum
                )
                normalized[normalized < 0] = 0
                result = image.copy()
                result[result != self.invalid_value] = normalized
            output.append(result)
        return output, data
