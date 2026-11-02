from .interfaces import ImageOperator


class Crop(ImageOperator):
    def __init__(self, top=0, bottom=0, left=0, right=0):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def apply(self, images):
        output = []
        for image in images:
            height, width = image.shape[:2]
            output.append(
                image[self.top : height - self.bottom, self.left : width - self.right]
            )
        return output, {}
