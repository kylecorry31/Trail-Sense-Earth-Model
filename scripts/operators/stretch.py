from .compound import CompoundOperator
from .linear_compression import LinearCompression
from .quantize import Quantize
import numpy as np


class Stretch(CompoundOperator):
    """
    Linearly stretches images to the range of an integer type (value = pixel / a - b). The metadata has the
    coefficients and a decoder (pixels back to values) for each image. Takes the same arguments as LinearCompression.
    """

    def __init__(self, type=np.uint8, **linear_compression_args):
        self.type = type
        self.linear_compression_args = linear_compression_args

    def apply(self, images):
        images, data = super().apply(images)
        # The coefficients and decoders of the stretch
        return images, data["metadata"][0]

    def operators(self):
        return [LinearCompression(**self.linear_compression_args), Quantize(self.type)]

