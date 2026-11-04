from .interfaces import ImageOperator


class Offset(ImageOperator):
    """Adds an amount to the values of each image."""

    def __init__(self, amount):
        self.amount = amount

    def apply(self, images):
        return [image + self.amount for image in images], {}
