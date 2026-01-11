from scripts import progress
from .. import load_pixels
import PIL.Image as Image

# Import all operators
from .split_processing import SplitProcessing
from .shift_x import ShiftX
from .replace_invalid import ReplaceInvalid
from .replace import Replace
from .flip_y import FlipY
from .reshape import Reshape
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
from .split_16_bits import Split16Bits
from .remove_oceans import RemoveOceans
from .remove_inland_water import RemoveInlandWater
from .remove_land import RemoveLand
from .mask import Mask

# Export all operators
__all__ = [
    "SplitProcessing",
    "ShiftX",
    "ReplaceInvalid",
    "Replace",
    "FlipY",
    "Reshape",
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
    "Split16Bits",
    "RemoveOceans",
    "RemoveInlandWater",
    "RemoveLand",
    "Mask",
    "process",
]

def process(images, *operators, show_progress=False):
    Image.MAX_IMAGE_PIXELS = None
    if images and isinstance(images[0], str):
        with progress.progress("Loading", total=len(images), disable=not show_progress) as pbar:
            new_images = []
            for path in images:
                new_images.append(load_pixels(path))
                pbar.update(1)
        images = new_images
    
    results = []
    with progress.progress("Processing", total=len(operators), disable=not show_progress) as pbar:
        for operator in operators:
            try:
                op_name = operator.__class__.__name__
                pbar.set_description(f"Processing [{op_name}]")
            except Exception:
                pass
            images, data = operator.apply(images)
            results.append(data)
            pbar.update(1)
    return images, results