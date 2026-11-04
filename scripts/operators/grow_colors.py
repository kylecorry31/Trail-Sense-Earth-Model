from .compound import CompoundOperator
from .grow_color import GrowColor


class GrowColors(CompoundOperator):
    """Grows each color in order (see GrowColor)."""

    def __init__(self, colors, **grow_color_args):
        self.colors = colors
        self.grow_color_args = grow_color_args

    def operators(self):
        return [GrowColor(color, **self.grow_color_args) for color in self.colors]
