from .interfaces import ImageOperator


class Map(ImageOperator):
    def __init__(self, map_function):
        self.map_function = map_function

    def apply(self, images):
        output = [self.map_function(image) for image in images]
        return output, {}
