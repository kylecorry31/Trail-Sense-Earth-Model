from .compound import CompoundOperator
from .remove_small_regions import RemoveSmallRegions


class RemoveSmallRegionsOfColors(CompoundOperator):
    """Removes the small regions of each color in order (see RemoveSmallRegions)."""

    def __init__(self, colors, max_size, **remove_small_regions_args):
        self.colors = colors
        self.max_size = max_size
        self.remove_small_regions_args = remove_small_regions_args

    def operators(self):
        return [
            RemoveSmallRegions(color, self.max_size, **self.remove_small_regions_args)
            for color in self.colors
        ]
