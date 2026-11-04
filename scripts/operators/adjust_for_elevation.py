from .interfaces import ImageOperator
import numpy as np


class AdjustForElevation(ImageOperator):
    """
    Adds rate * elevation to the values of each image, where the elevations (any size, covering the same area) are
    resampled to the size of the image. A positive rate (the lapse rate) brings a value at elevation to sea level.
    """

    def __init__(self, elevations, rate):
        self.elevations = elevations
        self.rate = rate

    def apply(self, images):
        output = []
        rows, columns = self.elevations.shape
        for image in images:
            height, width = image.shape
            ys = np.arange(height) * rows // height
            xs = np.arange(width) * columns // width
            output.append(image + self.rate * self.elevations[np.ix_(ys, xs)])
        return output, {}
