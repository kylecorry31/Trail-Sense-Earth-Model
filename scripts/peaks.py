"""
Summits for a lossy DEM. Downsampling flattens narrow summits (Mount Washington ends up about 400 m low), so the summits
the model is well under are stored in a separate file, peaks.webp, which the app uses to sharpen the model around them.
It is ignored by versions of the app that do not know about it.

The file is a geo point file (see geo_points.py) where the value of a point is a scale and a base elevation (see
pack_value). The elevation added at a distance d from a summit, where the model is at an elevation e, is
scale * max(e - base, 0) * (1 - (d / RADIUS_METERS)^2)^2 when d is less than the radius (the amounts added by summits near
each other add up). The scale makes the summit reach its true elevation, and since it multiplies the height of the model
above its surroundings, the added relief follows the shape of the model (ridges stay ridges) instead of being a dome.
The app uses the same radius and value encoding (see PeakOverlay).
"""

import io

import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter, uniform_filter

from .geo_points import GeoPointFormat

FILE_FORMAT = GeoPointFormat(cell_degrees=5, bits_per_axis=12, value_bytes=2, value_step=1)
FILENAME = "peaks.webp"
RADIUS_METERS = 4000
METERS_PER_DEGREE = 111_000

# A summit is the highest pixel within SUMMIT_WINDOW pixels that stands at least PROMINENCE_METERS above the average of
# the valid pixels within SURROUNDINGS_WINDOW pixels (zero is treated as having no data)
PROMINENCE_METERS = 300
SURROUNDINGS_WINDOW = 121
SUMMIT_WINDOW = 21
# Summits which the model is less than this far below are not worth storing
MIN_SHORTFALL_METERS = 100
# Relief can only be scaled up if the model already rises toward the summit, so a summit is skipped when the model is
# less than this fraction of its shortfall above the model around it (RING_METERS away), which also limits the scale to
# 1 / MIN_MODEL_RELIEF_RATIO
MIN_MODEL_RELIEF_RATIO = 0.5
RING_METERS = 4000
RING_SAMPLES = 12

SCALE_BITS = 7
SCALE_STEPS_PER_UNIT = 63
BASE_BITS = 9
BASE_STEP_METERS = 16


def pack_value(scale, base):
    """The value of a summit: the scale in steps of 1/63 (7 bits), then the base elevation in steps of 16 m (9 bits)."""
    scale_steps = np.clip(np.round(scale * SCALE_STEPS_PER_UNIT), 0, (1 << SCALE_BITS) - 1).astype(np.int64)
    base_steps = np.clip(np.round(base / BASE_STEP_METERS), 0, (1 << BASE_BITS) - 1).astype(np.int64)
    return scale_steps | (base_steps << SCALE_BITS)


def cubic_weight(distance):
    """The weight of a pixel at a distance (in pixels) when sampling with a Catmull-Rom spline."""
    d = np.abs(distance)
    return np.where(d <= 1, 1 - 2.5 * d**2 + 1.5 * d**3, np.where(d <= 2, 2 - 4 * d + 2.5 * d**2 - 0.5 * d**3, 0.0))


def sample_bicubic(image, y, x):
    """The image at (y, x) in pixels (a pixel's center is at its integer coordinates), sampled the way the app does."""
    height, width = image.shape
    y0 = np.floor(y).astype(np.int64)
    x0 = np.floor(x).astype(np.int64)
    result = np.zeros(y.shape)
    for i in range(-1, 3):
        row = np.clip(y0 + i, 0, height - 1)
        row_weight = cubic_weight(y - (y0 + i))
        for j in range(-1, 3):
            column = np.clip(x0 + j, 0, width - 1)
            result += image[row, column] * row_weight * cubic_weight(x - (x0 + j))
    return result


def decode_tile(webp_data, a, b):
    """The elevation of every pixel of a stretched 8-bit tile (value = pixel / a - b)."""
    pixels = np.asarray(Image.open(io.BytesIO(webp_data)).convert("L"), dtype=np.float32)
    return pixels / a - b


def find_summits(source, model, north, west, degrees):
    """
    The summits in the source elevation of a square tile that the decoded model is well under, as an array of
    (latitude, longitude, how far below the model is, scale, base elevation). The model is sampled the way the app does.
    """
    source = source.astype(np.float32)
    height, width = source.shape
    valid = (source != 0).astype(np.float32)
    surroundings = uniform_filter(source * valid, SURROUNDINGS_WINDOW, mode="nearest") / np.maximum(
        uniform_filter(valid, SURROUNDINGS_WINDOW, mode="nearest"), 1e-6
    )
    is_summit = (
        (source == maximum_filter(source, size=SUMMIT_WINDOW))
        & (source - surroundings >= PROMINENCE_METERS)
        & (valid > 0)
    )
    rows, columns = np.nonzero(is_summit)
    if len(rows) == 0:
        return np.zeros((0, 5))

    latitudes = north - (rows + 0.5) / height * degrees
    longitudes = west + (columns + 0.5) / width * degrees
    model_height, model_width = model.shape

    def sample(sample_latitudes, sample_longitudes):
        return sample_bicubic(
            model,
            (north - sample_latitudes) / degrees * model_height - 0.5,
            (sample_longitudes - west) / degrees * model_width - 0.5,
        )

    sampled = sample(latitudes, longitudes)
    shortfall = source[rows, columns] - sampled
    angles = np.linspace(0, 2 * np.pi, RING_SAMPLES, endpoint=False)
    ring_latitudes = latitudes[:, None] + RING_METERS / METERS_PER_DEGREE * np.sin(angles)
    ring_longitudes = longitudes[:, None] + RING_METERS / (
        METERS_PER_DEGREE * np.cos(np.radians(latitudes))[:, None]
    ) * np.cos(angles)
    ring = sample(ring_latitudes.ravel(), ring_longitudes.ravel()).reshape(-1, RING_SAMPLES).mean(axis=1)
    relief = sampled - ring
    keep = (shortfall >= MIN_SHORTFALL_METERS) & (relief >= MIN_MODEL_RELIEF_RATIO * shortfall)
    scale = shortfall[keep] / relief[keep]
    return np.stack([latitudes[keep], longitudes[keep], shortfall[keep], scale, ring[keep]], axis=1)
