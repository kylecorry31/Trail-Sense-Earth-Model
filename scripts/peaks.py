import io

import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter, uniform_filter

from .geo_points import Field, GeoPointFormat

FILENAME = "peaks.tsgeo"
RADIUS_METERS = 4000
# The type tells the app how to use the file, so a change to the formula needs a new type
FILE_FORMAT = GeoPointFormat(
    cell_degrees=5,
    # About 110 m, finer than the 15 arc second pixels the summits are found in
    decimals=3,
    fields=(Field("scale", bytes=1, step=1 / 64), Field("base", bytes=2, step=16)),
    properties={"type": "peaks", "radius_meters": RADIUS_METERS},
)
METERS_PER_DEGREE = 111_000

# A summit is the highest pixel within SUMMIT_WINDOW pixels that stands at least PROMINENCE_METERS above the average of
# the valid pixels within SURROUNDINGS_WINDOW pixels (zero is treated as having no data)
PROMINENCE_METERS = 300
SURROUNDINGS_WINDOW = 121
SUMMIT_WINDOW = 21
# Summits which the model is less than this far below are not worth storing (raising them makes the model worse
# around them about as often as it makes it better)
MIN_SHORTFALL_METERS = 110
# Relief can only be scaled up if the model already rises toward the summit, so a summit is skipped when the model is
# less than this fraction of its shortfall above the model around it (RADIUS_METERS away), which also limits the scale
# to 1 / MIN_MODEL_RELIEF_RATIO
MIN_MODEL_RELIEF_RATIO = 0.5
RING_SAMPLES = 12

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
    The summits in the source elevation of a square tile that the decoded model is well under, as arrays of their
    latitude, longitude, shortfall (how far below them the model is), scale, and base. The model is sampled the way the
    app does.
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
        return empty_summits()

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
    ring_latitudes = latitudes[:, None] + RADIUS_METERS / METERS_PER_DEGREE * np.sin(angles)
    ring_longitudes = longitudes[:, None] + RADIUS_METERS / (
        METERS_PER_DEGREE * np.cos(np.radians(latitudes))[:, None]
    ) * np.cos(angles)
    ring = sample(ring_latitudes.ravel(), ring_longitudes.ravel()).reshape(-1, RING_SAMPLES).mean(axis=1)
    relief = sampled - ring
    keep = (shortfall >= MIN_SHORTFALL_METERS) & (relief >= MIN_MODEL_RELIEF_RATIO * shortfall)
    scale = shortfall[keep] / relief[keep]
    return {
        "latitude": latitudes[keep],
        "longitude": longitudes[keep],
        "shortfall": shortfall[keep],
        "scale": scale,
        "base": ring[keep],
    }


def empty_summits():
    return {key: np.zeros(0) for key in ("latitude", "longitude", "shortfall", "scale", "base")}
