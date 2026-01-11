from .interfaces import ImageOperator
import numpy as np


class ReplaceLargeValues(ImageOperator):
    def __init__(self, threshold, replacement=0, invalid_value=-999):
        self.threshold = threshold
        self.replacement = replacement
        self.invalid_value = invalid_value

    def apply(self, images):
        all_large_values = []
        output = []
        for image in images:
            large_values = []
            result = image.copy()
            large_value_indices = np.argwhere(
                (image > self.threshold) & (image != self.invalid_value)
            )
            for idx in large_value_indices:
                large_values.append((int(idx[0]), int(idx[1]), image[idx[0], idx[1]]))
                result[idx[0], idx[1]] = self.replacement
            all_large_values.append(large_values)
            output.append(result)
        return output, {"large_values": all_large_values}
