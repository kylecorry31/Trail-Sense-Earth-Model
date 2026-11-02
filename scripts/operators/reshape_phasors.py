from .interfaces import ImageOperator
import numpy as np


class ReshapePhasors(ImageOperator):
    """
    Reduces an [amplitude, phase (degrees)] pair to a smaller shape by averaging the phasors of every valid
    source pixel in each output pixel. Output pixels with no valid source pixels are set to the invalid value.
    """

    def __init__(self, shape, invalid_value=-999):
        self.shape = shape
        self.invalid_value = invalid_value

    def apply(self, images):
        amplitude, phase = images
        height, width = self.shape[1], self.shape[0]
        block_y = amplitude.shape[0] // height
        block_x = amplitude.shape[1] // width

        valid = (amplitude != self.invalid_value) & (phase != self.invalid_value)
        radians = np.radians(np.where(valid, phase, 0))
        real = np.where(valid, amplitude * np.cos(radians), 0)
        imaginary = np.where(valid, amplitude * np.sin(radians), 0)

        def block_sum(image):
            return image.reshape(height, block_y, width, block_x).sum(axis=(1, 3))

        count = block_sum(valid.astype(np.float64))
        has_data = count > 0
        real = block_sum(real) / np.maximum(count, 1)
        imaginary = block_sum(imaginary) / np.maximum(count, 1)

        new_amplitude = np.where(has_data, np.hypot(real, imaginary), self.invalid_value)
        new_phase = np.where(
            has_data, np.degrees(np.arctan2(imaginary, real)), self.invalid_value
        )
        return [new_amplitude, new_phase], {}
