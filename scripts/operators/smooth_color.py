from .interfaces import ImageOperator
import numpy as np
from skimage.morphology import dilation, erosion, remove_small_holes


class SmoothColor(ImageOperator):
    def __init__(
        self,
        color,
        smoothing_iterations=5,
        min_hole_size=None,
        smoothing_structure=None,
        min_hole_size_is_percent=False,
    ):
        self.color = color
        self.smoothing_iterations = smoothing_iterations
        self.min_hole_size = min_hole_size
        self.smoothing_structure = smoothing_structure
        self.min_hole_size_is_percent = min_hole_size_is_percent

    def __smooth_color(
        self,
        image,
        color,
        smoothing_structure=None,
        smoothing_iterations=2,
        min_hole_size=None,
    ):
        distances = np.linalg.norm(
            image.astype(np.int16) - np.array(color).astype(np.int16), axis=-1
        )
        mask = distances <= 4
        for _ in range(smoothing_iterations):
            mask = dilation(mask, footprint=smoothing_structure)
        for _ in range(smoothing_iterations):
            mask = erosion(mask, footprint=smoothing_structure)
        if min_hole_size is not None:
            mask = remove_small_holes(mask, max_size=min_hole_size)
        image[mask] = color
        return image

    def apply(self, images):
        output = []
        for image in images:
            min_hole_size = self.min_hole_size
            if self.min_hole_size_is_percent and self.min_hole_size is not None:
                image_area = np.prod(image.shape[:2])
                min_hole_size = image_area * self.min_hole_size

            result = self.__smooth_color(
                image,
                self.color,
                smoothing_structure=self.smoothing_structure,
                smoothing_iterations=self.smoothing_iterations,
                min_hole_size=min_hole_size,
            )
            output.append(result)
        return output, {}
