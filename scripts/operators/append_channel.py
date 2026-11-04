from .interfaces import ImageOperator
import numpy as np


class AppendChannel(ImageOperator):
    """Appends a channel (an image of the same size) to each image."""

    def __init__(self, channel):
        self.channel = channel

    def apply(self, images):
        return [np.dstack([image, self.channel]) for image in images], {}
