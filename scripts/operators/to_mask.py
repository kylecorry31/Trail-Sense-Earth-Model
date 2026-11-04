from .interfaces import ImageOperator


class ToMask(ImageOperator):
    """Converts each image to a boolean mask, which is True wherever the pixel is not 0."""

    def apply(self, images):
        return [image.astype(bool) for image in images], {}
