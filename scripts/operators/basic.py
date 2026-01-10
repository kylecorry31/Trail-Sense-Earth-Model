from .. import create_image, compression
from .interfaces import ImageOperator
import numpy as np
from PIL import Image
import os


class SplitProcessing(ImageOperator):
    def __init__(self, *operators):
        self.operators = operators

    def apply(self, images):
        output = []
        data = {"data": []}
        for image in images:
            image_data = []
            for operator in self.operators:
                image, operator_data = operator.apply([image])
                image_data.append(operator_data)
            for i in image:
                output.append(i)
            data["data"].append(image_data)
        return output, data


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


class Replace(ImageOperator):
    def __init__(self, target_value, replacement=0):
        self.target_value = target_value
        self.replacement = replacement

    def apply(self, images):
        output = []
        for image in images:
            output.append(np.where(image == self.target_value, self.replacement, image))
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


class Resize(ImageOperator):
    def __init__(self, max_size, resample=Image.NEAREST):
        self.max_size = max_size
        self.resample = resample

    def apply(self, images):
        output = []
        for image in images:
            img = Image.fromarray(image)
            img.thumbnail(self.max_size, resample=self.resample)
            output.append(np.array(img))
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
                new_minimum = (
                    np.min(image[image != self.invalid_value])
                    if self.invalid_value is not None
                    else np.min(image)
                )
                if minimum is None or new_minimum < minimum:
                    minimum = new_minimum
        if maximum is None:
            for image in images:
                new_maximum = (
                    np.max(image[image != self.invalid_value])
                    if self.invalid_value is not None
                    else np.max(image)
                )
                if maximum is None or new_maximum > maximum:
                    maximum = new_maximum

        data = {"minimum": minimum, "maximum": maximum}

        output = []
        for image in images:
            if self.invalid_value is None:
                result = (image - minimum) / (maximum - minimum)
            else:
                normalized = (image[image != self.invalid_value] - minimum) / (
                    maximum - minimum
                )
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
            large_value_indices = np.argwhere(
                (image > self.threshold) & (image != self.invalid_value)
            )
            for idx in large_value_indices:
                large_values.append((int(idx[0]), int(idx[1]), image[idx[0], idx[1]]))
                result[idx[0], idx[1]] = self.replacement
            all_large_values.append(large_values)
            output.append(result)
        return output, {"large_values": all_large_values}


class BitwiseOr(ImageOperator):
    def apply(self, images):
        if len(images) == 0:
            return images, {}
        output_image = images[0].copy()
        for image in images[1:]:
            output_image = np.bitwise_or(output_image, image)
        return [output_image], {}


class Tile(ImageOperator):
    def __init__(self, tile_size):
        self.tile_size = tile_size

    def apply(self, images):
        output = []
        for image in images:
            tiles_x = int(np.ceil(image.shape[1] / self.tile_size[1]))
            tiles_y = int(np.ceil(image.shape[0] / self.tile_size[0]))
            for ty in range(tiles_y):
                for tx in range(tiles_x):
                    x_start = tx * self.tile_size[1]
                    y_start = ty * self.tile_size[0]
                    x_end = min(x_start + self.tile_size[1], image.shape[1])
                    y_end = min(y_start + self.tile_size[0], image.shape[0])
                    tile = image[y_start:y_end, x_start:x_end]
                    output.append(tile)
        return output, {}


class Group(ImageOperator):
    def __init__(self, grouping=3):
        self.grouping = grouping

    def apply(self, images):
        output = []
        for i in range(0, len(images), self.grouping):
            output.append(np.dstack(images[i : i + self.grouping]))
        return output, {}


class Save(ImageOperator):
    def __init__(self, paths, mode=None, quality=100, lossless=True):
        self.paths = paths
        self.mode = mode
        self.quality = quality
        self.lossless = lossless

    def __get_format(self, path):
        format_map = {
            "tif": "TIFF",
            "webp": "WEBP",
            "jpg": "JPEG",
            "png": "PNG",
        }
        return format_map.get(path.rsplit(".", 1)[-1].lower(), "WEBP")

    def apply(self, images):
        i = 0

        for image in images:
            path = self.paths(i) if callable(self.paths) else self.paths[i]

            if not os.path.exists(path.rsplit("/", 1)[0]):
                os.makedirs(path.rsplit("/", 1)[0])

            if isinstance(image, np.ndarray) and image.ndim == 3:
                channels = [image[:, :, k] for k in range(image.shape[2])]
            else:
                channels = image if isinstance(image, (list, tuple)) else [image]

            format = self.__get_format(path)
            if self.mode is not None:
                mode = self.mode
            elif format == "TIFF":
                mode = "F"
            else:
                mode = "L"

            pil_channels = [
                Image.fromarray(
                    c.astype(np.float32) if mode == "F" else c.astype(np.uint8),
                    mode=mode,
                )
                for c in channels
            ]
            img = (
                pil_channels[0]
                if len(pil_channels) == 1
                else create_image(pil_channels)
            )

            if format != "TIFF":
                img.save(
                    path,
                    quality=self.quality,
                    lossless=self.lossless,
                    format=format,
                    method=6,
                    alpha_quality=0 if len(channels) < 3 else self.quality,
                    optimize=True,
                    compress_level=9,
                )
            else:
                img.save(path, format=format)

            i += 1
        return images, {}


class Map(ImageOperator):
    def __init__(self, map_function):
        self.map_function = map_function

    def apply(self, images):
        output = [self.map_function(image) for image in images]
        return output, {}


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


class RemoveSmallRegions(ImageOperator):
    def __init__(
        self, color, max_size=10, invalid_colors=None, default_fill=None, search_space=2
    ):
        self.color = color
        self.max_size = max_size
        self.invalid_colors = invalid_colors or []
        self.default_fill = default_fill
        self.search_space = search_space

    def apply(self, images):
        output = []
        for image in images:
            result = compression.remove_small_regions(
                image,
                self.color,
                self.max_size,
                invalid_colors=self.invalid_colors,
                default_fill=self.default_fill,
                search_space=self.search_space,
            )
            output.append(result)
        return output, {}


class GrowColor(ImageOperator):
    def __init__(self, color, structure=None, iterations=1):
        self.color = color
        self.iterations = iterations
        self.structure = structure if structure is not None else np.ones((3, 3))

    def apply(self, images):
        from .. import compression

        output = []
        for image in images:
            result = compression.grow_color(
                image, self.color, structure=self.structure, iterations=self.iterations
            )
            output.append(result)
        return output, {}


class Resize(ImageOperator):
    def __init__(self, size):
        self.size = size

    def apply(self, images):
        output = []
        for image in images:
            img = Image.fromarray(image)
            img.thumbnail(self.size, resample=Image.NEAREST)
            output.append(np.array(img))
        return output, {}


class Min(ImageOperator):
    def apply(self, images):
        combined = np.min(np.array(images), axis=0)
        return [combined], {}
