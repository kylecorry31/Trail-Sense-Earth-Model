from .interfaces import ImageOperator
import numpy as np


class FourierSeries(ImageOperator):
    """
    Replaces the 12 monthly images with the coefficients of their annual cycle, as a mean followed by the cosine and
    sine of each harmonic (1 + 2 * harmonics images). The value in month m (0 to 11) is
    mean + sum(cos_h * cos(2 pi h m / 12) + sin_h * sin(2 pi h m / 12)).
    """

    def __init__(self, harmonics):
        self.harmonics = harmonics

    def apply(self, images):
        angles = 2 * np.pi * np.arange(len(images)) / len(images)
        columns = [np.ones(len(images))]
        for harmonic in range(1, self.harmonics + 1):
            columns += [np.cos(harmonic * angles), np.sin(harmonic * angles)]
        basis = np.stack(columns, axis=1)
        shape = images[0].shape
        values = np.stack(images).reshape(len(images), -1).astype(np.float64)
        coefficients = np.linalg.lstsq(basis, values, rcond=None)[0]
        return [c.reshape(shape) for c in coefficients], {"harmonics": self.harmonics}
