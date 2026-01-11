from .interfaces import ImageOperator
from .. import compression
import numpy as np


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

    def apply(self, images):
        output = []
        for image in images:
            min_hole_size = self.min_hole_size
            if self.min_hole_size_is_percent and self.min_hole_size is not None:
                image_area = np.prod(image.shape[:2])
                min_hole_size = image_area * self.min_hole_size

            result = compression.smooth_color(
                image,
                self.color,
                smoothing_structure=self.smoothing_structure,
                smoothing_iterations=self.smoothing_iterations,
                min_hole_size=min_hole_size,
            )
            output.append(result)
        return output, {}
