from .interfaces import ImageOperator
import numpy as np


def polar_rows(height, north, south):
    """The rows of an image (90 to -90 degrees of latitude) which are north of the north latitude or south of the south."""
    north_row = 0 if north is None else max(0, min(height, int((90 - north) / 180 * height)))
    south_row = height if south is None else max(0, min(height, int((90 - south) / 180 * height)))
    return slice(0, north_row), slice(south_row, height)


class FillPolarRegions(ImageOperator):
    """Fills the pixels north of the north latitude and south of the south latitude (either can be None) with a color."""

    def __init__(self, color, north=None, south=None):
        self.color = color
        self.north = north
        self.south = south

    def apply(self, images):
        output = []
        for image in images:
            filled = image.copy()
            for rows in polar_rows(image.shape[0], self.north, self.south):
                filled[rows] = self.color
            output.append(filled)
        return output, {}


class ReplaceColorInPolarRegions(ImageOperator):
    """Replaces a color with another north of the north latitude and south of the south latitude (either can be None)."""

    def __init__(self, color, replacement, north=None, south=None):
        self.color = color
        self.replacement = replacement
        self.north = north
        self.south = south

    def apply(self, images):
        output = []
        for image in images:
            replaced = image.copy()
            for rows in polar_rows(image.shape[0], self.north, self.south):
                region = replaced[rows]
                region[(region == self.color).all(axis=-1)] = self.replacement
            output.append(replaced)
        return output, {}
