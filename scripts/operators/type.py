from .interfaces import ImageOperator


class Type(ImageOperator):

    def __init__(self, type):
        self.type = type

    def apply(self, images):
        output = []
        for image in images:
            output.append(image.astype(self.type))
        return output, {}
