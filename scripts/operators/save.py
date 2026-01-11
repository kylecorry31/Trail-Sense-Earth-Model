from .interfaces import ImageOperator
from .. import create_image
from PIL import Image
import numpy as np
import os


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
