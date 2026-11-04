from .interfaces import ImageOperator
import numpy as np


class LinearCompression(ImageOperator):
    """
    Linearly stretches the images (pixel = (value + b) * a). The metadata has the coefficients of each image and a
    decoder, a function that converts its pixels back to values (value = pixel / a - b).
    """

    def __init__(self, a=None, b=None, calculate_per_image=False, target_max=255):
        self.a = a
        self.b = b
        self.calculate_per_image = calculate_per_image
        self.target_max = target_max

    def apply(self, images):
        a = self.a
        b = self.b
        coefficients = []
        decoders = []

        if not self.calculate_per_image and (a is None or b is None):
            min_value = np.inf
            max_value = -np.inf
            for image in images:
                min_value = min(min_value, np.min(image))
                max_value = max(max_value, np.max(image))

            if np.isinf(min_value):
                b = 0
                a = 1
            else:
                b = -min_value
                denom = max_value + b
                a = self.target_max / denom if denom != 0 else 1
        else:
            a = self.a if self.a is not None else 1.0
            b = self.b if self.b is not None else 0.0

        output = []
        for image in images:
            current_a = a
            current_b = b

            if self.calculate_per_image:
                local_min = np.min(image)
                local_max = np.max(image)
                current_b = -local_min
                denom = local_max + current_b
                current_a = self.target_max / denom if denom != 0 else 1
            coefficients.append({"a": float(current_a), "b": float(current_b)})
            decoders.append(lambda pixels, a=current_a, b=current_b: pixels / a - b)

            compressed = (image + current_b) * current_a
            output.append(compressed)

        metadata = {"coefficients": coefficients, "decoders": decoders}

        return output, metadata
