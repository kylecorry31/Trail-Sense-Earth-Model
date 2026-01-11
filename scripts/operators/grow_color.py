from .interfaces import ImageOperator
import numpy as np
from skimage.morphology import dilation


class GrowColor(ImageOperator):
    def __init__(self, color, structure=None, iterations=1):
        self.color = color
        self.iterations = iterations
        self.structure = structure if structure is not None else np.ones((3, 3))

    def __grow_color(self, image, color, structure=None, iterations=1):
        distances = np.linalg.norm(
            image.astype(np.int16) - np.array(color).astype(np.int16), axis=-1
        )
        mask = distances <= 4
        for _ in range(iterations):
            mask = dilation(mask, footprint=structure)
        image[mask] = color
        return image

    def apply(self, images):
        output = []
        for image in images:
            result = self.__grow_color(
                image, self.color, structure=self.structure, iterations=self.iterations
            )
            output.append(result)
        return output, {}
