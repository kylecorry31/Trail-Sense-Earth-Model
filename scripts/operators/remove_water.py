from .compound import CompoundOperator
from .remove_oceans import RemoveOceans
from .remove_inland_water import RemoveInlandWater


class RemoveWater(CompoundOperator):
    """Removes the oceans (replaced with 0) and then inland water (replaced with inland_replacement)."""

    def __init__(self, dilation=5, scale=4, inland_replacement=0):
        self.dilation = dilation
        self.scale = scale
        self.inland_replacement = inland_replacement

    def operators(self):
        return [
            RemoveOceans(dilation=self.dilation, scale=self.scale),
            RemoveInlandWater(
                dilation=self.dilation,
                scale=self.scale,
                replacement=self.inland_replacement,
            ),
        ]
