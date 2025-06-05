from .interfaces import ImageOperator
import numpy as np
from PIL import Image
import os

class ShiftX(ImageOperator):
    def __init__(self, shift, is_percent=False):
        self.shift = shift
        self.is_percent = is_percent

    def apply(self, images):
        if self.shift == 0:
            return images, {}
        shift = self.shift
        output = []
        for image in images:
            if self.is_percent:
                shift = int(np.floor(image.shape[1] * self.shift))
            output.append(np.roll(image, shift, axis=1))
        return output, {}

class ReplaceInvalid(ImageOperator):
    def __init__(self, replacement=0):
        self.replacement = replacement

    def apply(self, images):
        output = []
        for image in images:
            values_array = np.ma.masked_invalid(image)
            output.append(np.where(values_array.mask, self.replacement, values_array))
        return output, {}

class FlipY(ImageOperator):
    def apply(self, images):
        output = []
        for image in images:
            output.append(np.flipud(image))
        return output, {}

class Reshape(ImageOperator):
    def __init__(self, shape):
        self.shape = shape

    def apply(self, images):
        if self.shape is None:
            return images, {}
        output = []
        for image in images:
            img = Image.fromarray(image).resize(self.shape, Image.NEAREST)
            output.append(np.array(img).reshape((self.shape[1], self.shape[0])))
        return output, {}

class Type(ImageOperator):

    def __init__(self, type):
        self.type = type

    def apply(self, images):
        output = []
        for image in images:
            output.append(image.astype(self.type))
        return output, {}

class Normalize(ImageOperator):
    def __init__(self, min_value=None, max_value=None, invalid_value=-999):
        self.min_value = min_value
        self.max_value = max_value
        self.invalid_value = invalid_value

    def apply(self, images):
        minimum = self.min_value
        maximum = self.max_value
        if minimum is None:
            for image in images:
                new_minimum = np.min(image[image != self.invalid_value]) if self.invalid_value is not None else np.min(image)
                if minimum is None or new_minimum < minimum:
                    minimum = new_minimum
        if maximum is None:
            for image in images:
                new_maximum = np.max(image[image != self.invalid_value]) if self.invalid_value is not None else np.max(image)
                if maximum is None or new_maximum > maximum:
                    maximum = new_maximum
        
        data = {
            'minimum': minimum,
            'maximum': maximum
        }

        output = []
        for image in images:
            if self.invalid_value is None:
                result = (image - minimum) / (maximum - minimum)
            else:
                normalized = (image[image != self.invalid_value] - minimum) / (maximum - minimum)
                normalized[normalized < 0] = 0
                result = image.copy()
                result[result != self.invalid_value] = normalized
            output.append(result)
        return output, data

class ReplaceLargeValues(ImageOperator):
    def __init__(self, threshold, replacement=0, invalid_value=-999):
        self.threshold = threshold
        self.replacement = replacement
        self.invalid_value = invalid_value

    def apply(self, images):
        all_large_values = []
        output = []
        for image in images:
            large_values = []
            result = image.copy()
            large_value_indices = np.argwhere((image > self.threshold) & (image != self.invalid_value))
            for idx in large_value_indices:
                large_values.append((int(idx[0]), int(idx[1]), image[idx[0], idx[1]]))
                result[idx[0], idx[1]] = self.replacement
            all_large_values.append(large_values)
            output.append(result)
        return output, {'large_values': all_large_values}

class Save(ImageOperator):
    def __init__(self, paths, mode='F'):
        self.paths = paths
        format_map = {
            'tif': 'TIFF',
            'webp': 'WEBP',
            'jpg': 'JPEG'
        }
        self.formats = []
        for path in paths:
            self.formats.append(format_map.get(path.rsplit('.', 1)[-1].lower(), 'WEBP'))
        self.mode = mode

    def apply(self, images):
        i = 0
        for image in images:
            path = self.paths[i]
            if self.mode == 'F':
                image_to_save = image.astype(np.float32)
            else:
                image_to_save = image
            img = Image.fromarray(image_to_save, mode=self.mode)
            if not os.path.exists(path.rsplit('/', 1)[0]):
                os.makedirs(path.rsplit('/', 1)[0])
            img.save(path, format=self.formats[i])
            i += 1
        return images, {}