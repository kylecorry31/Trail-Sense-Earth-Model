import numpy as np


def area_weights(rows, columns, minimum=0.01):
    """
    The ground area of each pixel of a grid with a row at each pole (90 to -90 degrees), relative to the equator. Rows
    are never weighted below the minimum, so the poles still count for something.
    """
    latitudes = 90 - 180 * np.arange(rows) / (rows - 1)
    return np.maximum(np.cos(np.radians(latitudes)), minimum)[:, None] * np.ones((1, columns))
