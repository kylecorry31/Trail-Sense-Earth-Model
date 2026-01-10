from .interfaces import ImageOperator
from ..natural_earth import remove_oceans, remove_inland_water

class RemoveOceans(ImageOperator):
    def __init__(self, dilation=5, replacement=0, scale=4):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale

    def apply(self, images):
        output = []
        for image in images:
            output.append(remove_oceans(image, dilation=self.dilation, replacement=self.replacement, scale=self.scale))
        return output, {}

class RemoveInlandWater(ImageOperator):
    def __init__(self, dilation=5, replacement=0, scale=4):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale

    def apply(self, images):
        output = []
        for image in images:
            output.append(remove_inland_water(image, dilation=self.dilation, replacement=self.replacement, scale=self.scale))
        return output, {}

class RemoveLand(ImageOperator):
    def __init__(self, dilation=5, replacement=0, scale=4):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale

    def apply(self, images):
        output = []
        for image in images:
            output.append(remove_oceans(image, inverted=True, dilation=self.dilation, replacement=self.replacement, scale=self.scale))
        return output, {}