from .interfaces import ImageOperator
import numpy as np


class ClimateNormal(ImageOperator):
    """
    Averages the images of each month over the years. The images are in order by year and then month, so the result
    has one image per month.
    """

    def __init__(self, months=12):
        self.months = months

    def apply(self, images):
        return [
            np.mean(images[month :: self.months], axis=0) for month in range(self.months)
        ], {}
