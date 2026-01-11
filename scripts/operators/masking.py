from .interfaces import ImageOperator
from ..natural_earth import remove_oceans, remove_inland_water
import numpy as np


class RemoveOceans(ImageOperator):
    def __init__(
        self,
        dilation=5,
        replacement=0,
        scale=4,
        bbox=None,
        only_replace_negative_pixels=False,
    ):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale
        self.bbox = bbox
        self.only_replace_negative_pixels = only_replace_negative_pixels

    def apply(self, images):
        output = []
        for image in images:
            output.append(
                remove_oceans(
                    image,
                    dilation=self.dilation,
                    replacement=self.replacement,
                    scale=self.scale,
                    bbox=self.bbox,
                    only_replace_negative_pixels=self.only_replace_negative_pixels,
                )
            )
        return output, {}


class RemoveInlandWater(ImageOperator):
    def __init__(
        self,
        dilation=5,
        replacement=0,
        scale=4,
        bbox=None,
        only_replace_negative_pixels=False,
        remove_rivers=False,
    ):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale
        self.bbox = bbox
        self.only_replace_negative_pixels = only_replace_negative_pixels
        self.remove_rivers = remove_rivers

    def apply(self, images):
        output = []
        for image in images:
            output.append(
                remove_inland_water(
                    image,
                    dilation=self.dilation,
                    replacement=self.replacement,
                    scale=self.scale,
                    bbox=self.bbox,
                    only_replace_negative_pixels=self.only_replace_negative_pixels,
                    remove_rivers=self.remove_rivers,
                )
            )
        return output, {}


class RemoveLand(ImageOperator):
    def __init__(
        self,
        dilation=5,
        replacement=0,
        scale=4,
        bbox=None,
        only_replace_negative_pixels=False,
    ):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale
        self.bbox = bbox
        self.only_replace_negative_pixels = only_replace_negative_pixels

    def apply(self, images):
        output = []
        for image in images:
            output.append(
                remove_oceans(
                    image,
                    inverted=True,
                    dilation=self.dilation,
                    replacement=self.replacement,
                    scale=self.scale,
                    bbox=self.bbox,
                    only_replace_negative_pixels=self.only_replace_negative_pixels,
                )
            )
        return output, {}


class Mask(ImageOperator):
    def __init__(self, mask_image, invert=False, replacement=0):
        self.mask_image = mask_image
        self.invert = invert
        self.replacement = replacement

    def apply(self, images):
        output = []
        for image in images:
            masked_image = np.copy(image)
            mask = self.mask_image if not callable(self.mask_image) else self.mask_image(image)
            if self.invert:
                mask = ~mask
            masked_image[mask] = self.replacement
            output.append(masked_image)
        return output, {}
