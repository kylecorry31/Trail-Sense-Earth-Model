from .interfaces import ImageOperator


class Scale(ImageOperator):
    """Multiplies the values of each image by a factor."""

    def __init__(self, factor):
        self.factor = factor

    def apply(self, images):
        return [image * self.factor for image in images], {}
