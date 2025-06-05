from .interfaces import ImageOperator
import numpy as np
from PIL import Image
import os

class ShiftX(ImageOperator):
    def __init__(self, shift, is_percent=False):
        self.shift = shift
        self.is_percent = is_percent

    def apply(self, image):
        if self.shift == 0:
            return image, {}
        shift = self.shift
        if self.is_percent:
            shift = int(np.floor(image.shape[1] * self.shift))
        return np.roll(image, shift, axis=1), {}

class ReplaceInvalid(ImageOperator):
    def __init__(self, replacement=0):
        self.replacement = replacement

    def apply(self, image):
        values_array = np.ma.masked_invalid(image)
        return np.where(values_array.mask, self.replacement, values_array), {}

class FlipY(ImageOperator):
    def apply(self, image):
        return np.flipud(image), {}

class Reshape(ImageOperator):
    def __init__(self, shape):
        self.shape = shape

    def apply(self, image):
        if self.shape is None:
            return image, {}
        img = Image.fromarray(image).resize(self.shape, Image.NEAREST)
        return np.array(img).reshape((self.shape[1], self.shape[0])), {}

class Float(ImageOperator):

    def __init__(self, bits=32):
        if bits not in [32, 64]:
            raise ValueError("Only 32 or 64 bits are supported for float conversion.")
        self.bits = bits

    def apply(self, image):
        return image.astype(np.float32 if self.bits == 32 else np.float64), {}

class Normalize(ImageOperator):
    def __init__(self, min_value=None, max_value=None, invalid_value=-999):
        self.min_value = min_value
        self.max_value = max_value
        self.invalid_value = invalid_value

    def apply(self, image):
        minimum = self.min_value
        maximum = self.max_value
        if minimum is None:
            minimum = np.min(image[image != self.invalid_value]) if self.invalid_value is not None else np.min(image)
        if maximum is None:
            maximum = np.max(image[image != self.invalid_value]) if self.invalid_value is not None else np.max(image)
        
        data = {
            'minimum': minimum,
            'maximum': maximum
        }

        if self.invalid_value is None:
            return (image - minimum) / (maximum - minimum), data
        normalized = (image[image != self.invalid_value] - minimum) / (maximum - minimum)
        normalized[normalized < 0] = 0
        result = image.copy()
        result[result != self.invalid_value] = normalized
        return result, data

class ReplaceLargeValues(ImageOperator):
    def __init__(self, threshold, replacement=0, invalid_value=-999):
        self.threshold = threshold
        self.replacement = replacement
        self.invalid_value = invalid_value

    def apply(self, image):
        large_values = []
        result = image.copy()
        large_value_indices = np.argwhere((image > self.threshold) & (image != self.invalid_value))
        for idx in large_value_indices:
            large_values.append((int(idx[0]), int(idx[1]), image[idx[0], idx[1]]))
            result[idx[0], idx[1]] = self.replacement
        return result, {'large_values': large_values}

class Save(ImageOperator):
    def __init__(self, path, mode='F'):
        self.path = path
        format_map = {
            'tif': 'TIFF',
            'webp': 'WEBP',
            'jpg': 'JPEG'
        }

        self.format = format_map.get(path.rsplit('.', 1)[-1].lower(), 'WEBP')
        self.mode = mode

    def apply(self, image):
        if self.mode == 'F':
            image_to_save = image.astype(np.float32)
        else:
            image_to_save = image
        img = Image.fromarray(image_to_save, mode=self.mode)
        if not os.path.exists(self.path.rsplit('/', 1)[0]):
            os.makedirs(self.path.rsplit('/', 1)[0])
        img.save(self.path, format=self.format)
        return image, {}