from .interfaces import ImageOperator
from ..natural_earth import remove_oceans

class RemoveOceans(ImageOperator):
    def __init__(self, dilation=5, replacement=0, scale=4):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale

    def apply(self, image):
        return remove_oceans(image, dilation=self.dilation, replacement=self.replacement, scale=self.scale), {}

class RemoveLand(ImageOperator):
    def __init__(self, dilation=5, replacement=0, scale=4):
        self.dilation = dilation
        self.replacement = replacement
        self.scale = scale

    def apply(self, image):
        return remove_oceans(image, inverted=True, dilation=self.dilation, replacement=self.replacement, scale=self.scale), {}