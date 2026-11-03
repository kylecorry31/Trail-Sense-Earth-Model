from .interfaces import ImageOperator
from scipy import ndimage
import numpy as np


class HilbertOrder(ImageOperator):
    """
    Renumbers the labels (1 to n, 0 is no label) of label images so they follow a Hilbert curve through the
    centers of the labels, which puts labels that are near each other next to each other in the numbering.
    """

    @staticmethod
    def __hilbert_distance(x, y, order):
        distance = 0
        step = 1 << (order - 1)
        while step > 0:
            rx = 1 if x & step else 0
            ry = 1 if y & step else 0
            distance += step * step * ((3 * rx) ^ ry)
            if ry == 0:
                if rx == 1:
                    x, y = step - 1 - x, step - 1 - y
                x, y = y, x
            step //= 2
        return distance

    def apply(self, images):
        output = []
        for labels in images:
            order = max(1, int(np.ceil(np.log2(max(labels.shape)))))
            distances = []
            for rows, columns in ndimage.find_objects(labels):
                center_row = rows.start + (rows.stop - rows.start) // 2
                center_column = columns.start + (columns.stop - columns.start) // 2
                distances.append(self.__hilbert_distance(center_column, center_row, order))

            # The new label of each old label (index 0 is no label) is its rank along the curve
            ranks = np.empty(len(distances), dtype=labels.dtype)
            ranks[np.argsort(distances, kind="stable")] = np.arange(1, len(distances) + 1)
            new_labels = np.concatenate([[0], ranks]).astype(labels.dtype)
            output.append(new_labels[labels])
        return output, {}
