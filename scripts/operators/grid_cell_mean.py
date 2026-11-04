from .interfaces import ImageOperator
import numpy as np


class GridCellMean(ImageOperator):
    """
    The mean of the area each point of a grid stands for. The grid has a point at each pole and wraps around the
    antimeridian, and each point is centered in a cell of 180 / (height - 1) degrees by 360 / width degrees. Reducing a
    value that is the mean of its whole cell (like a reanalysis temperature) with the mean elevation of the cell is more
    accurate than using the elevation at the point, which can be thousands of meters different in the mountains.
    """

    def __init__(self, shape):
        self.shape = shape

    def __mean(self, image):
        height, width = self.shape
        rows, columns = image.shape
        image = image.astype(np.float64)
        cell_height = 180 / (height - 1)
        cell_width = 360 / width
        means = np.zeros((height, width))
        for y in range(height):
            latitude = 90 - y * cell_height
            top = int(np.floor((90 - min(latitude + cell_height / 2, 90)) / 180 * rows))
            bottom = max(int(np.ceil((90 - max(latitude - cell_height / 2, -90)) / 180 * rows)), top + 1)
            row = image[top:bottom].mean(axis=0)
            # Cumulative sums around the antimeridian
            padded = np.concatenate([[0], np.cumsum(np.concatenate([row, row]))])
            for x in range(width):
                longitude = -180 + x * cell_width
                first = int(np.floor((longitude - cell_width / 2 + 180) / 360 * columns))
                last = int(np.ceil((longitude + cell_width / 2 + 180) / 360 * columns))
                count = max(last - first, 1)
                start = first % columns
                means[y, x] = (padded[start + count] - padded[start]) / count
        return means

    def apply(self, images):
        return [self.__mean(image) for image in images], {}
