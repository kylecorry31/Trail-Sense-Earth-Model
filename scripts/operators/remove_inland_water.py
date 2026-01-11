from .interfaces import ImageOperator
from ..natural_earth import remove_inland_water


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
