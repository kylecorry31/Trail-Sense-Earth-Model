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
    Encodes 8-bit images as lossy WebP at each quality and measures how well the decoded result matches the reference
    (it is resized to the reference's size). The images are not changed.

    Each option has the mean absolute error (in the units of the reference), and the detail loss, which is the fraction
    of the reference's detail (change in elevation between nearby points, which is what makes up the elevation gain
    of a route) that is missing from the decoded result.

    The images are encoded with cwebp (see encode_gray).

    reference: the images to compare against, at any resolution
    coefficients: the a and b used to compress each image (see LinearCompression), where value = pixel / a - b
    """

    def __init__(self, qualities, reference, coefficients):
        self.qualities = qualities
        self.reference = reference
        self.coefficients = coefficients

    def __get_option(self, image, quality, reference, reference_roughness, a, b):
        data = encode_gray(image, quality)
        decoded = np.array(Image.open(io.BytesIO(data)).convert("L"), dtype=np.float32)
        values = np.array(
            Image.fromarray(decoded / a - b).resize(
                (reference.shape[1], reference.shape[0]), Image.BILINEAR
            )
        )
        error = np.abs(values - reference).mean()
        lost = max(reference_roughness - roughness(values), 0)
        return {
            "quality": quality,
            "data": data,
            "error": float(error),
            "detail_loss": float(lost / max(reference_roughness, MIN_DETAIL)),
        }

    def apply(self, images):
        options = []
        with ThreadPoolExecutor() as executor:
            for image, reference, coefficient in zip(
                images, self.reference, self.coefficients
            ):
                a, b = coefficient["a"], coefficient["b"]
                reference_roughness = roughness(reference)
                options.append(
                    list(
                        executor.map(
                            lambda quality: self.__get_option(
                                image, quality, reference, reference_roughness, a, b
                            ),
                            self.qualities,
                        )
                    )
                )
        return images, {"options": options}
