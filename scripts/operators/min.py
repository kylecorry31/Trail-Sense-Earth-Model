from .interfaces import ImageOperator
import numpy as np


class Min(ImageOperator):
    def apply(self, images):
        combined = np.min(np.array(images), axis=0)
        return [combined], {}
