from .interfaces import ImageOperator
import numpy as np


class RemoveLatitudeTrend(ImageOperator):
    """
    Subtracts a polynomial of the sine of the latitude (fit to the mean of each row, weighted by the area of the row)
    from the chosen images, which narrows their range so they can be stored more precisely. The images cover the
    latitudes from 90 to -90, with a row at each pole. The metadata has the coefficients of each polynomial (lowest
    power first) for the images that were changed, None for the others.
    """

    def __init__(self, degree, indices=(0,)):
        self.degree = degree
        self.indices = indices

    def apply(self, images):
        rows = images[0].shape[0]
        sine = np.sin(np.radians(90 - 180 * np.arange(rows) / (rows - 1)))
        weights = np.sqrt(np.maximum(np.sqrt(1 - sine**2), 0.05))
        output = []
        trends = []
        for i, image in enumerate(images):
            if i not in self.indices:
                output.append(image)
                trends.append(None)
                continue
            coefficients = np.polynomial.polynomial.polyfit(
                sine, image.mean(axis=1), self.degree, w=weights
            )
            trend = np.polynomial.polynomial.polyval(sine, coefficients)
            output.append(image - trend[:, None])
            trends.append([float(c) for c in coefficients])
        return output, {"trends": trends}
