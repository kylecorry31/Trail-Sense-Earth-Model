from .interfaces import ImageOperator
import numpy as np


class CondenseLabels(ImageOperator):
    """
    Condenses each image into one value per label, the average of the valid pixels (not the invalid value) with that
    label, laid out row by row in an image final_width wide. The label image can be smaller than the images (each of
    its pixels covers a square of image pixels). Labels with no valid pixels, and the unused end of the last row,
    are set to the invalid value.
    """

    def __init__(self, labels, final_width, invalid_value=-999):
        self.labels = labels
        self.final_width = final_width
        self.invalid_value = invalid_value

    def apply(self, images):
        scale = images[0].shape[0] // self.labels.shape[0]
        labels = np.repeat(np.repeat(self.labels, scale, axis=0), scale, axis=1).ravel()
        label_count = int(self.labels.max())
        rows = -(-label_count // self.final_width)
        assert rows < 255, f"Too many cells to index: {label_count}"

        total_count = rows * self.final_width
        output = []
        for image in images:
            values = image.ravel()
            valid = values != self.invalid_value
            counts = np.bincount(labels[valid], minlength=label_count + 1)[1:]
            sums = np.bincount(labels[valid], weights=values[valid], minlength=label_count + 1)[1:]
            condensed = np.full(total_count, self.invalid_value, dtype=np.float64)
            condensed[:label_count] = np.where(counts > 0, sums / np.maximum(counts, 1), self.invalid_value)
            output.append(condensed.reshape(rows, self.final_width))
        return output, {}
