from .interfaces import ImageOperator
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

    def __create_image(self, images):
        if len(images) == 0:
            return None

        if len(images) == 1:
            return images[0].convert("L")

        if len(images) == 3:
            r, g, b = images
            return Image.merge("RGB", (r.convert("L"), g.convert("L"), b.convert("L")))

        if len(images) == 4:
            r, g, b, a = images
            return Image.merge(
                "RGBA",
                (r.convert("L"), g.convert("L"), b.convert("L"), a.convert("L")),
            )

        image_arrays = [np.array(im) for im in images]
        mapped = np.zeros((*image_arrays[0].shape, 4), dtype=np.uint8)
        mapped[..., 3] = 255
        for i in range(len(images)):
            mapped[..., i] = image_arrays[i]
        return Image.fromarray(mapped)

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
                else self.__create_image(pil_channels)
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
