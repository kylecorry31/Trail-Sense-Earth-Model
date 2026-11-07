"""
A compact file of points on the globe, each with a position and some values, that can be read a piece at a time (for
example the summits of a DEM or cell towers). See docs/geo-point-file-format.md for the specification.
"""

import json
import struct
import zlib
from dataclasses import dataclass, field

import numpy as np

MAGIC = b"TSGP"
FORMAT_VERSION = 1
HEADER_BYTES = 16
DIRECTORY_ENTRY_BYTES = 12
MAX_DECIMALS = 7


@dataclass(frozen=True)
class Field:
    """A value stored for every point, as an unsigned integer of `bytes` bytes (value = stored * step + offset)."""

    name: str
    bytes: int
    step: float = 1.0
    offset: float = 0.0

    def encode(self, values):
        steps = np.round((np.asarray(values, dtype=np.float64) - self.offset) / self.step)
        return np.clip(steps, 0, (1 << (8 * self.bytes)) - 1).astype(np.uint64)

    def decode(self, stored):
        return stored * self.step + self.offset


@dataclass(frozen=True)
class GeoPointFormat:
    # The size of a cell (a square of the globe whose points are stored together) in degrees
    cell_degrees: int = 5
    # Positions are stored to this many decimal places of a degree
    decimals: int = 4
    fields: tuple = ()
    # Cells are packed into compressed blocks of about this many points (a block is the smallest piece that is read)
    block_points: int = 2048
    # Anything the reader of a kind of file needs to know (ex. what the values mean)
    properties: dict = field(default_factory=dict)

    def __post_init__(self):
        if 180 % self.cell_degrees != 0 or 360 % self.cell_degrees != 0:
            raise ValueError("The cell size must divide 180 and 360")
        if not 0 <= self.decimals <= MAX_DECIMALS:
            raise ValueError(f"The decimals must be between 0 and {MAX_DECIMALS}")
        if any(not 1 <= f.bytes <= 4 for f in self.fields):
            raise ValueError("Fields must be 1 to 4 bytes")

    @property
    def rows(self):
        return 180 // self.cell_degrees

    @property
    def columns(self):
        return 360 // self.cell_degrees

    @property
    def steps(self):
        """The number of positions along each axis of a cell."""
        return self.cell_degrees * 10**self.decimals

    def pack(self, latitudes, longitudes, values=None):
        """
        The contents of a file of the points. Values is a dict of field name to an array of values, which are rounded to
        the step of the field and limited to what fits.
        """
        values = values or {}
        latitudes = np.asarray(latitudes, dtype=np.float64)
        longitudes = np.asarray(longitudes, dtype=np.float64)
        scale = 10**self.decimals
        # The north pole is moved to the last position of the last row, and 180 degrees east is -180
        latitude_steps = np.clip(np.round((latitudes + 90) * scale), 0, 180 * scale - 1).astype(np.int64)
        longitude_steps = np.mod(np.round((longitudes + 180) * scale), 360 * scale).astype(np.int64)
        rows, y = np.divmod(latitude_steps, self.steps)
        columns, x = np.divmod(longitude_steps, self.steps)
        cells = rows * self.columns + columns
        positions = y * self.steps + x
        stored = [f.encode(values[f.name]) for f in self.fields]

        order = np.lexsort((positions, cells))
        cells, positions = cells[order], positions[order]
        stored = [s[order] for s in stored]
        cell_ids, firsts, counts = np.unique(cells, return_index=True, return_counts=True)

        cell_ranges = []
        blocks = []
        i = 0
        while i < len(cell_ids):
            j, total = i, 0
            while j < len(cell_ids) and (total == 0 or total + counts[j] <= self.block_points):
                total += counts[j]
                j += 1
            start, end = firsts[i], firsts[j - 1] + counts[j - 1]
            cell_ranges.append((int(cell_ids[i]), int(cell_ids[j - 1])))
            blocks.append(
                self._pack_block(
                    cell_ids[i:j],
                    counts[i:j],
                    firsts[i:j] - start,
                    positions[start:end],
                    [s[start:end] for s in stored],
                )
            )
            i = j

        metadata = json.dumps(
            {
                "cell_degrees": self.cell_degrees,
                "decimals": self.decimals,
                "count": len(latitudes),
                "fields": [{"name": f.name, "bytes": f.bytes, "step": f.step, "offset": f.offset} for f in self.fields],
                "properties": self.properties,
            },
            separators=(",", ":"),
        ).encode("utf-8")

        offset = HEADER_BYTES + len(metadata) + (len(blocks) + 1) * DIRECTORY_ENTRY_BYTES
        directory = []
        for (first_cell, last_cell), block in zip(cell_ranges, blocks):
            directory.append(struct.pack("<III", first_cell, last_cell, offset))
            offset += len(block)
        cell_count = self.rows * self.columns
        directory.append(struct.pack("<III", cell_count, cell_count, offset))

        header = MAGIC + struct.pack("<B3xII", FORMAT_VERSION, len(metadata), len(blocks))
        return header + metadata + b"".join(directory) + b"".join(blocks)

    def _pack_block(self, cell_ids, counts, firsts, positions, stored):
        starts_cell = np.zeros(len(positions), dtype=bool)
        starts_cell[firsts] = True
        position_deltas = np.where(starts_cell, positions, positions - np.r_[0, positions[:-1]])
        cell_gaps = np.diff(np.r_[cell_ids[0] - 1, cell_ids]) - 1
        parts = [_varints([len(cell_ids)]), _varints(cell_gaps), _varints(counts), _varints(position_deltas)]
        for f, s in zip(self.fields, stored):
            # By byte (the first byte of every point, then the second, ...), since each compresses better on its own
            parts.append(s.astype("<u8").view(np.uint8).reshape(-1, 8)[:, : f.bytes].T.tobytes())
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        return compressor.compress(b"".join(parts)) + compressor.flush()

    def fit(self, latitudes, longitudes, values, budget_bytes):
        """
        The contents of a file of as many of the points as fit in the budget, taken in order (so the most important
        should be first), and how many that is.
        """
        def pack_first(n):
            return self.pack(latitudes[:n], longitudes[:n], {name: v[:n] for name, v in values.items()})

        best = pack_first(0)
        if len(best) > budget_bytes:
            raise ValueError("The budget is too small for an empty file")
        low, high = 0, len(latitudes)
        while low < high:
            middle = (low + high + 1) // 2
            data = pack_first(middle)
            if len(data) <= budget_bytes:
                low, best = middle, data
            else:
                high = middle - 1
        return best, low


def read(data):
    """The metadata, latitudes, longitudes, and field values (a dict) of a file, for checking what was written."""
    if data[:4] != MAGIC:
        raise ValueError("Not a geo point file")
    version, metadata_length, block_count = struct.unpack("<B3xII", data[4:HEADER_BYTES])
    if version != FORMAT_VERSION:
        raise ValueError(f"Unsupported version {version}")
    metadata = json.loads(data[HEADER_BYTES : HEADER_BYTES + metadata_length])
    fields = [Field(**f) for f in metadata["fields"]]
    decimals = metadata["decimals"]
    columns = 360 // metadata["cell_degrees"]
    steps = metadata["cell_degrees"] * 10**decimals
    directory_start = HEADER_BYTES + metadata_length
    directory = [
        struct.unpack_from("<III", data, directory_start + i * DIRECTORY_ENTRY_BYTES) for i in range(block_count + 1)
    ]

    latitudes, longitudes = [], []
    values = {f.name: [] for f in fields}
    for (first_cell, _, start), (_, _, end) in zip(directory[:-1], directory[1:]):
        block = zlib.decompress(data[start:end], -15)
        reader = _VarintReader(block)
        cell_count = reader.next()
        cell_ids, cell = [], first_cell - 1
        for _ in range(cell_count):
            cell += reader.next() + 1
            cell_ids.append(cell)
        counts = [reader.next() for _ in range(cell_count)]
        for cell, count in zip(cell_ids, counts):
            row, column = divmod(cell, columns)
            position = 0
            for _ in range(count):
                position += reader.next()
                y, x = divmod(position, steps)
                latitudes.append((row * steps + y - 90 * 10**decimals) / 10**decimals)
                longitudes.append((column * steps + x - 180 * 10**decimals) / 10**decimals)
        total = sum(counts)
        offset = reader.offset
        for f in fields:
            planes = np.frombuffer(block, np.uint8, f.bytes * total, offset).reshape(f.bytes, total)
            offset += f.bytes * total
            stored = sum(planes[i].astype(np.uint64) << np.uint64(8 * i) for i in range(f.bytes))
            values[f.name].extend(f.decode(np.asarray(stored, dtype=np.float64)).tolist())
    return metadata, np.array(latitudes), np.array(longitudes), {k: np.array(v) for k, v in values.items()}


def _varints(values):
    """Unsigned LEB128: 7 bits per byte, least significant first, with the high bit set on every byte but the last."""
    values = np.asarray(values, dtype=np.uint64)
    if len(values) == 0:
        return b""
    lengths = np.ones(len(values), dtype=np.int64)
    for k in range(1, 10):
        lengths += (values >> np.uint64(7 * k)) > 0
    starts = np.r_[0, np.cumsum(lengths)[:-1]]
    output = np.zeros(lengths.sum(), dtype=np.uint8)
    for k in range(lengths.max()):
        has = lengths > k
        group = (values[has] >> np.uint64(7 * k)) & np.uint64(0x7F)
        more = (lengths[has] > k + 1).astype(np.uint64) << np.uint64(7)
        output[starts[has] + k] = (group | more).astype(np.uint8)
    return output.tobytes()


class _VarintReader:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def next(self):
        value, shift = 0, 0
        while True:
            byte = self.data[self.offset]
            self.offset += 1
            value |= (byte & 0x7F) << shift
            if byte < 0x80:
                return value
            shift += 7
