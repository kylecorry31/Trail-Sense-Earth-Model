from .interfaces import ImageOperator
import numpy as np


class LabelIndices(ImageOperator):
    """
    Converts label images (1 to n, 0 is no label) to two images with the x (column) and y (row) position of each
    label, starting at 1, if the labels were laid out row by row in an image final_width wide (0 where there is no
    label).
    """

    def __init__(self, final_width):
        self.final_width = final_width

    def apply(self, images):
        output = []
        for labels in images:
            has_label = labels > 0
            output.append(np.where(has_label, (labels - 1) % self.final_width + 1, 0).astype(np.float64))
            output.append(np.where(has_label, (labels - 1) // self.final_width + 1, 0).astype(np.float64))
        return output, {}
