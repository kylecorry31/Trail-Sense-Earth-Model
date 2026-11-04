from .compound import CompoundOperator
from .smooth_color import SmoothColor


class SmoothColors(CompoundOperator):
    """Smooths each color in order and then again in reverse order, so no color has the final say."""

    def __init__(self, colors, **smooth_color_args):
        self.colors = colors
        self.smooth_color_args = smooth_color_args

    def operators(self):
        return [
            SmoothColor(color, **self.smooth_color_args)
            for color in [*self.colors, *reversed(self.colors)]
        ]
