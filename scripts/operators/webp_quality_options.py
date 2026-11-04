from .interfaces import ImageOperator
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from ..webp import encode_gray
import numpy as np
import io

# Detail is the change in elevation between points this many pixels of the reference apart
DETAIL_STEP = 2
# Detail below this (in the units of the reference) counts as noise when measuring how much of it is lost
MIN_DETAIL = 10


def roughness(values):
    horizontal = np.abs(values[:, DETAIL_STEP:] - values[:, :-DETAIL_STEP]).mean()
    vertical = np.abs(values[DETAIL_STEP:] - values[:-DETAIL_STEP]).mean()
    return float((horizontal + vertical) / 2)


class WebpQualityOptions(ImageOperator):
    """
    Encodes each image as lossy WebP at each quality and measures how well the decoded result matches the reference (it
    is resized to the reference's size). The images are not changed.

    Each option has the mean absolute error (in the units of the reference), and the detail loss, which is the fraction
    of the reference's detail (change in elevation between nearby points, which is what makes up the elevation gain
    of a route) that is missing from the decoded result.

    The images are encoded with cwebp (see encode_gray).

    Each option also has the mean squared error, weighted by weights (an image the size of the reference, like the area
    of each pixel) if they are given.

    to_pixels: the operator which converts the images to the 8-bit pixels to encode (like Stretch). Its metadata has a
        decoder for each image, a function that converts decoded pixels back to values (in the units of the reference)
    reference: the images to compare against, at any resolution (by default, the images)

    The metadata has the options of each image, and the metadata of to_pixels.
    """

    def __init__(self, qualities, to_pixels, reference=None, weights=None):
        self.qualities = qualities
        self.to_pixels = to_pixels
        self.reference = reference
        self.weights = weights

    def __get_option(self, pixels, to_values, quality, reference, reference_roughness):
        data = encode_gray(pixels, quality)
        decoded = np.array(Image.open(io.BytesIO(data)).convert("L"), dtype=np.float32)
        values = np.array(
            Image.fromarray(to_values(decoded)).resize(
                (reference.shape[1], reference.shape[0]), Image.BILINEAR
            )
        )
        error = np.abs(values - reference).mean()
        lost = max(reference_roughness - roughness(values), 0)
        return {
            "quality": quality,
            "data": data,
            "error": float(error),
            "squared_error": float(np.average((values - reference) ** 2, weights=self.weights)),
            "detail_loss": float(lost / max(reference_roughness, MIN_DETAIL)),
        }

    def apply(self, images):
        pixels, pixels_metadata = self.to_pixels.apply(images)
        references = self.reference if self.reference is not None else images
        options = []
        with ThreadPoolExecutor() as executor:
            for image_pixels, to_values, reference in zip(
                pixels, pixels_metadata["decoders"], references
            ):
                reference_roughness = roughness(reference)
                options.append(
                    list(
                        executor.map(
                            lambda quality: self.__get_option(
                                image_pixels, to_values, quality, reference, reference_roughness
                            ),
                            self.qualities,
                        )
                    )
                )
        return images, {**pixels_metadata, "options": options}
