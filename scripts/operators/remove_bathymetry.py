from .compound import CompoundOperator
from .mask import Mask
from .remove_oceans import RemoveOceans
import numpy as np

# The lowest place on land (m), anything lower is not land
LOWEST_LAND = -430.5


class RemoveBathymetry(CompoundOperator):
    """
    Removes the ocean floor from ETOPO elevation tiles, using the source identifiers of the tile (source_ids, the same
    size as the tile) to tell land from bathymetry. The tile covers bbox (west, south, east, north).

    land_ids: the source identifiers which are land
    coastline_id: the source identifier of the US coastline, where elevations below 0 are set to 0
    """

    def __init__(self, source_ids, land_ids, bbox, coastline_id=13):
        self.source_ids = source_ids
        self.land_ids = land_ids
        self.bbox = bbox
        self.coastline_id = coastline_id

    def operators(self):
        return [
            RemoveOceans(
                scale=2,
                dilation=-20,
                only_replace_negative_pixels=True,
                bbox=self.bbox,
            ),
            Mask(~np.isin(self.source_ids, self.land_ids)),
            Mask(lambda image: (self.source_ids == self.coastline_id) & (image < 0)),
            Mask(lambda image: image < LOWEST_LAND),
        ]
