from .interfaces import ImageOperator
import numpy as np


class SnapToNeighbors(ImageOperator):
    """
    Treats consecutive pairs of [magnitude, angle (degrees)] images as vectors, and makes the images easier to
    compress by copying a neighbor's value (left, then above) wherever it changes the vector by less than the
    tolerance times the size of all of the vectors at that pixel. Either the whole vector is copied or, if that is
    too different, just the angle. Pixels with a magnitude above ignore_above do not count towards the size.
    """

    def __init__(self, tolerance, invalid_value=-999, ignore_above=None):
        self.tolerance = tolerance
        self.invalid_value = invalid_value
        self.ignore_above = ignore_above

    def apply(self, images):
        shape = images[0].shape
        width = shape[1]
        magnitude = np.stack(images[0::2]).reshape(len(images) // 2, -1).astype(np.float64)
        angle = np.stack(images[1::2]).reshape(len(images) // 2, -1).astype(np.float64)
        valid = (magnitude != self.invalid_value) & (angle != self.invalid_value)
        radians = np.radians(np.where(valid, angle, 0))
        true_vector = np.where(valid, magnitude * np.exp(1j * radians), 0)

        counted = valid if self.ignore_above is None else valid & (magnitude <= self.ignore_above)
        tolerance = self.tolerance * np.sqrt((np.where(counted, magnitude, 0) ** 2).sum(axis=0))

        for i in range(magnitude.shape[1]):
            if not valid[:, i].any():
                continue
            neighbors = [j for j in (i - 1, i - width) if j >= 0]
            snapped = np.zeros(magnitude.shape[0], dtype=bool)
            for j in neighbors:
                vector = np.where(valid[:, j], magnitude[:, j] * np.exp(1j * np.radians(np.where(valid[:, j], angle[:, j], 0))), 0)
                close = valid[:, i] & valid[:, j] & ~snapped & (np.abs(vector - true_vector[:, i]) <= tolerance[i])
                magnitude[close, i] = magnitude[close, j]
                angle[close, i] = angle[close, j]
                snapped |= close
            for j in neighbors:
                vector = magnitude[:, i] * np.exp(1j * np.radians(np.where(valid[:, j], angle[:, j], 0)))
                close = valid[:, i] & valid[:, j] & ~snapped & (np.abs(vector - true_vector[:, i]) <= tolerance[i])
                angle[close, i] = angle[close, j]
                snapped |= close

        output = []
        for m, a in zip(magnitude, angle):
            output.append(m.reshape(shape))
            output.append(a.reshape(shape))
        return output, {}
