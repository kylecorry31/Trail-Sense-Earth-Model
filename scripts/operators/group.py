from .interfaces import ImageOperator
import numpy as np


class Group(ImageOperator):
    def __init__(self, grouping=3):
        self.grouping = grouping

    def apply(self, images):
        output = []
        for i in range(0, len(images), self.grouping):
            output.append(np.dstack(images[i : i + self.grouping]))
        return output, {}
