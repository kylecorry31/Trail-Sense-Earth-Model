from scripts import progress
from .. import load_pixels
from .interfaces import ImageOperator
import PIL.Image as Image

# Import all operators
from .split_processing import SplitProcessing
from .shift_x import ShiftX
from .replace_invalid import ReplaceInvalid
from .replace import Replace
from .flip_y import FlipY
from .reshape import Reshape
from .quadtree import Quadtree
from .hilbert_order import HilbertOrder
from .fourier_series import FourierSeries
from .remove_latitude_trend import RemoveLatitudeTrend
from .condense_labels import CondenseLabels
from .label_indices import LabelIndices
from .polar_to_cartesian import PolarToCartesian
from .cartesian_to_polar import CartesianToPolar
from .snap_to_neighbors import SnapToNeighbors
from .crop import Crop
from .resize import Resize
from .type import Type
from .normalize import Normalize
from .replace_large_values import ReplaceLargeValues
from .bitwise_or import BitwiseOr
from .tile import Tile
from .group import Group
from .save import Save
from .map import Map
from .smooth_color import SmoothColor
from .remove_small_regions import RemoveSmallRegions
from .grow_color import GrowColor
from .min import Min
from .conditional import Conditional
from .index import Index
from .linear_compression import LinearCompression
from .webp_quality_options import WebpQualityOptions
from .fit_to_budget import FitToBudget
from .classify_colors import ClassifyColors
from .polar_regions import FillPolarRegions, ReplaceColorInPolarRegions
from .split_16_bits import Split16Bits
from .remove_oceans import RemoveOceans
from .remove_inland_water import RemoveInlandWater
from .remove_land import RemoveLand
from .mask import Mask
from .quantize import Quantize
from .clip import Clip
from .scale import Scale
from .sqrt import Sqrt
from .append_channel import AppendChannel
from .compound import CompoundOperator
from .remove_water import RemoveWater
from .to_mask import ToMask
from .remove_empty import RemoveEmpty
from .remove_bathymetry import RemoveBathymetry
from .append_water_channel import AppendWaterChannel
from .smooth_colors import SmoothColors
from .remove_small_regions_of_colors import RemoveSmallRegionsOfColors
from .grow_colors import GrowColors
from .climate_harmonics import ClimateHarmonics
from .offset import Offset
from .climate_normal import ClimateNormal
from .adjust_for_elevation import AdjustForElevation
from .grid_cell_mean import GridCellMean
from .stretch import Stretch

# Export all operators
__all__ = [
    "SplitProcessing",
    "ShiftX",
    "ReplaceInvalid",
    "Replace",
    "FlipY",
    "Reshape",
    "Quadtree",
    "HilbertOrder",
    "FourierSeries",
    "RemoveLatitudeTrend",
    "CondenseLabels",
    "LabelIndices",
    "PolarToCartesian",
    "CartesianToPolar",
    "SnapToNeighbors",
    "Crop",
    "Resize",
    "Type",
    "Normalize",
    "ReplaceLargeValues",
    "BitwiseOr",
    "Tile",
    "Group",
    "Save",
    "Map",
    "SmoothColor",
    "RemoveSmallRegions",
    "GrowColor",
    "Min",
    "Conditional",
    "Index",
    "LinearCompression",
    "WebpQualityOptions",
    "FitToBudget",
    "ClassifyColors",
    "FillPolarRegions",
    "ReplaceColorInPolarRegions",
    "Split16Bits",
    "RemoveOceans",
    "RemoveInlandWater",
    "RemoveLand",
    "Mask",
    "Quantize",
    "Clip",
    "Scale",
    "Sqrt",
    "AppendChannel",
    "CompoundOperator",
    "RemoveWater",
    "ToMask",
    "RemoveEmpty",
    "RemoveBathymetry",
    "AppendWaterChannel",
    "SmoothColors",
    "RemoveSmallRegionsOfColors",
    "GrowColors",
    "ClimateHarmonics",
    "Offset",
    "ClimateNormal",
    "AdjustForElevation",
    "GridCellMean",
    "Stretch",
    "process",
]

class Results(list):
    """The data returned by each operator, which can also be looked up by the type of operator."""

    def __init__(self, operators):
        super().__init__()
        self.__operators = operators

    def of(self, operator_type, occurrence=0):
        matches = [
            data
            for operator, data in zip(self.__operators, self)
            if isinstance(operator, operator_type)
        ]
        return matches[occurrence]


def _flatten(operators):
    """
    Operators can be nested in lists (to build up repeated steps with a comprehension) or skipped with None (for
    optional steps).
    """
    flat = []
    for operator in operators:
        if operator is None:
            continue
        if isinstance(operator, (list, tuple)):
            flat.extend(_flatten(operator))
        elif isinstance(operator, CompoundOperator):
            flat.extend(_flatten(operator.operators()))
        elif isinstance(operator, ImageOperator):
            flat.append(operator)
        else:
            raise TypeError(f"Not an operator: {operator!r}")
    return flat


def process(images, *operators, show_progress=False):
    Image.MAX_IMAGE_PIXELS = None
    operators = _flatten(operators)
    if images and isinstance(images[0], str):
        with progress.progress("Loading", total=len(images), disable=not show_progress) as pbar:
            new_images = []
            for path in images:
                new_images.append(load_pixels(path))
                pbar.update(1)
        images = new_images

    results = Results(operators)
    with progress.progress("Processing", total=len(operators), disable=not show_progress) as pbar:
        for operator in operators:
            pbar.set_description(f"Processing [{operator.__class__.__name__}]")
            images, data = operator.apply(images)
            results.append(data)
            pbar.update(1)
    return images, results
