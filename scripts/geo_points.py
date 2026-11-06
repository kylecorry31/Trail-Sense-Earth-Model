"""
A compact file of points on the globe, each with a coordinate and a value, that can be read a piece at a time (for
example the summits of a DEM or the cell towers of an area).

The points are grouped into square cells of the globe, so a reader only needs the header, the cell table, and the cells
around the location it is interested in.

Format (little endian):
    header (12 bytes): format version (u8), cell size in degrees (u8), bytes per value (u8), bits per axis of the
        position (u8), number of points (u32), size of one step of the value (f32)
    cell table: for every cell, the number of points in the cells before it (u32), plus one more entry for the total.
        Cells are in rows from the south (-90) to the north, each row from the west (-180) to the east.
    records, grouped by cell in the order of the table, sorted by latitude within a cell: the position within the cell
        as x | y << bits_per_axis (x and y are in 1/2^bits_per_axis of the cell from its south west corner), in the
        fewest bytes that fit it, followed by the value in steps. The y of a record is the difference from the y of the
        record before it in the cell (the first is from the south edge), which is small since they are sorted.
    The records are stored by byte: first the first byte of every record, then the second byte of every record, and so
        on. Each of these is mostly similar numbers, which compress far better than the records mixed together.

What a value means is up to whoever reads the file.
"""

import io
import struct
from dataclasses import dataclass

import numpy as np
from PIL import Image

FORMAT_VERSION = 1
HEADER_BYTES = 12
# The width of the image when a file is saved as one (see to_webp)
WEBP_WIDTH = 64


@dataclass(frozen=True)
class GeoPointFormat:
    cell_degrees: int = 5
    bits_per_axis: int = 12
    value_bytes: int = 1
    value_step: float = 1.0

    @property
    def rows(self):
        return 180 // self.cell_degrees

    @property
    def columns(self):
        return 360 // self.cell_degrees

    @property
    def table_bytes(self):
        return (self.rows * self.columns + 1) * 4

    @property
    def position_bytes(self):
        return (2 * self.bits_per_axis + 7) // 8

    @property
    def record_bytes(self):
        return self.position_bytes + self.value_bytes

    def max_points(self, budget_bytes):
        """How many points fit in a file of this size."""
        return max((budget_bytes - HEADER_BYTES - self.table_bytes) // self.record_bytes, 0)

    def pack(self, points):
        """
        The contents of the file for points, an array of (latitude, longitude, value). Values are rounded to the step
        and limited to what fits.
        """
        steps_per_axis = 1 << self.bits_per_axis
        rows = np.clip(np.floor((points[:, 0] + 90) / self.cell_degrees).astype(np.int64), 0, self.rows - 1)
        columns = np.clip(np.floor((points[:, 1] + 180) / self.cell_degrees).astype(np.int64), 0, self.columns - 1)
        south = rows * self.cell_degrees - 90
        west = columns * self.cell_degrees - 180
        y = np.clip(np.floor((points[:, 0] - south) / self.cell_degrees * steps_per_axis), 0, steps_per_axis - 1)
        x = np.clip(np.floor((points[:, 1] - west) / self.cell_degrees * steps_per_axis), 0, steps_per_axis - 1)
        x, y = x.astype(np.int64), y.astype(np.int64)
        value = np.clip(np.round(points[:, 2] / self.value_step), 0, (1 << (8 * self.value_bytes)) - 1)

        cells = rows * self.columns + columns
        order = np.lexsort((x, y, cells))
        x, y, cells_sorted, value = x[order], y[order], cells[order], value[order]
        starts_cell = np.r_[True, cells_sorted[1:] != cells_sorted[:-1]]
        y_step = np.where(starts_cell, y, y - np.r_[0, y[:-1]])
        record = x.astype(np.uint64) | (y_step.astype(np.uint64) << self.bits_per_axis)
        record = record | (value.astype(np.uint64) << (8 * self.position_bytes))
        record_bytes = record.astype("<u8").view(np.uint8).reshape(-1, 8)[:, : self.record_bytes]

        counts = np.bincount(cells, minlength=self.rows * self.columns)
        table = np.concatenate([[0], np.cumsum(counts)]).astype("<u4")
        header = struct.pack(
            "<BBBBIf", FORMAT_VERSION, self.cell_degrees, self.value_bytes, self.bits_per_axis, len(points), self.value_step
        )
        return header + table.tobytes() + record_bytes.T.tobytes()


def to_webp(data):
    """
    The contents of a file as a lossless grayscale WebP, which compresses it. Every byte is a pixel, in rows of
    WEBP_WIDTH pixels. The end is padded with zeros.
    """
    padded = data + bytes(-len(data) % WEBP_WIDTH)
    pixels = np.frombuffer(padded, dtype=np.uint8).reshape(-1, WEBP_WIDTH)
    output = io.BytesIO()
    Image.fromarray(pixels, "L").save(output, "WEBP", lossless=True, quality=100, method=6)
    return output.getvalue()
