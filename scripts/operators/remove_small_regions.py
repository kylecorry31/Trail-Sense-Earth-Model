from .interfaces import ImageOperator
from .. import compression


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
