"""
A compact index of cell tower locations.

The world is split into tiles of 512x512 cells (about 2.7 degrees at the default resolution of 1/192 degree). The
cells of a tile are sorted along a Z-order (Morton) curve, which keeps the cells of a cluster close together, and
the gaps between consecutive cells are stored with Elias-gamma style codes: a Huffman code for the bit length of the
gap followed by the remaining bits of the gap.

The bytes are stored as the pixels of a lossless WebP image (see to_image), so the app can read a tile by decoding only
the rows of the image that hold it.

File layout:
    1 byte:     the number of cells per tile edge, as a power of two
    1 byte:     the number of bit length codes (n)
    n bytes:    the Huffman code length of each bit length
    varint:     the number of tiles
    per tile:   varint tile id gap, varint cell count, varint size in bytes
    per tile:   the gap codes, padded to a whole byte
"""

import heapq
import math

import numpy as np

tile_bits = 9
image_width = 1024
# Cells in latitude/longitude, offset to start at 0 (the poles and the antimeridian)
resolution_per_degree = 192


def to_cells(latitudes, longitudes, per_degree=resolution_per_degree):
    """The unique (row, column) cells of the points, where the center of a cell is a multiple of the resolution"""
    rows = np.round((np.asarray(latitudes) + 90) * per_degree).astype(np.int64)
    columns = np.round((np.asarray(longitudes) + 180) * per_degree).astype(np.int64)
    packed = np.unique(rows * (360 * per_degree + 1) + columns)
    width = 360 * per_degree + 1
    return packed // width, packed % width


def __interleave(x):
    result = np.zeros_like(x)
    for bit in range(tile_bits):
        result |= ((x >> bit) & 1) << (2 * bit)
    return result


def morton(rows, columns):
    return __interleave(rows) | (__interleave(columns) << 1)


def __varint(value):
    out = bytearray()
    while value >= 128:
        out.append(value & 127 | 128)
        value >>= 7
    out.append(value)
    return out


def __code_lengths(counts):
    """Huffman code lengths for the symbols, every symbol gets a code"""
    heap = [(count + 1, i, [i]) for i, count in enumerate(counts)]
    heapq.heapify(heap)
    lengths = [0] * len(counts)
    tie = len(counts)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        for symbol in a[2] + b[2]:
            lengths[symbol] += 1
        heapq.heappush(heap, (a[0] + b[0], tie, a[2] + b[2]))
        tie += 1
    return lengths


def canonical_codes(lengths):
    """Codes assigned in order of length, then symbol"""
    order = sorted(range(len(lengths)), key=lambda s: (lengths[s], s))
    codes = [0] * len(lengths)
    code = 0
    previous = lengths[order[0]]
    for symbol in order:
        code <<= lengths[symbol] - previous
        previous = lengths[symbol]
        codes[symbol] = code
        code += 1
    return codes


def encode(rows, columns, per_degree=resolution_per_degree):
    """Encodes the cells (rows and columns from to_cells)"""
    edge = 1 << tile_bits
    tile_columns = (360 * per_degree) // edge + 1
    tile_ids = (rows >> tile_bits) * tile_columns + (columns >> tile_bits)
    codes = morton(rows & (edge - 1), columns & (edge - 1))

    order = np.lexsort((codes, tile_ids))
    tile_ids = tile_ids[order]
    codes = codes[order]

    unique_tiles, starts, counts = np.unique(tile_ids, return_index=True, return_counts=True)

    gaps = []
    for start, count in zip(starts, counts):
        tile_codes = codes[start:start + count]
        gaps.append(np.diff(tile_codes, prepend=-1))

    max_symbol = 2 * tile_bits
    histogram = [0] * (max_symbol + 1)
    for tile_gaps in gaps:
        for symbol, count in zip(*np.unique(np.floor(np.log2(tile_gaps)).astype(int), return_counts=True)):
            histogram[symbol] += count
    lengths = __code_lengths(histogram)
    huffman = canonical_codes(lengths)

    payloads = []
    for tile_gaps in gaps:
        bits = []
        for gap in tile_gaps.tolist():
            symbol = gap.bit_length() - 1
            bits.append((huffman[symbol], lengths[symbol]))
            if symbol:
                bits.append((gap & ((1 << symbol) - 1), symbol))
        value = 0
        total = 0
        for code, length in bits:
            value = (value << length) | code
            total += length
        padding = -total % 8
        payloads.append((value << padding).to_bytes((total + padding) // 8, "big"))

    out = bytearray([tile_bits, len(lengths)])
    out += bytes(lengths)
    out += __varint(len(unique_tiles))
    previous = 0
    for tile, count, payload in zip(unique_tiles.tolist(), counts.tolist(), payloads):
        out += __varint(tile - previous)
        out += __varint(count)
        out += __varint(len(payload))
        previous = tile
    for payload in payloads:
        out += payload
    return bytes(out)


def to_image(data, width=image_width):
    """The index as a grayscale image (a pixel per byte, read left to right, top to bottom), so it can be stored as lossless WebP"""
    height = -(-len(data) // width)
    pixels = np.zeros(height * width, dtype=np.uint8)
    pixels[:len(data)] = np.frombuffer(data, dtype=np.uint8)
    return pixels.reshape(height, width)


def decode(data, per_degree=resolution_per_degree):
    """Decodes to the sorted unique (row, column) cells, used to check the encoding"""
    position = 0

    def varint():
        nonlocal position
        value = 0
        shift = 0
        while True:
            byte = data[position]
            position += 1
            value |= (byte & 127) << shift
            if byte < 128:
                return value
            shift += 7

    edge_bits = data[0]
    symbols = data[1]
    lengths = list(data[2:2 + symbols])
    position = 2 + symbols
    codes = canonical_codes(lengths)
    lookup = {(lengths[s], codes[s]): s for s in range(symbols)}
    tile_count = varint()
    tiles = []
    previous = 0
    for _ in range(tile_count):
        previous += varint()
        tiles.append((previous, varint(), varint()))
    tile_columns = (360 * per_degree) // (1 << edge_bits) + 1
    rows = []
    columns = []
    for tile, count, size in tiles:
        bits = int.from_bytes(data[position:position + size], "big")
        remaining = size * 8
        position += size
        code = -1
        for _ in range(count):
            length = 0
            value = 0
            while (length, value) not in lookup:
                remaining -= 1
                value = (value << 1) | ((bits >> remaining) & 1)
                length += 1
            symbol = lookup[(length, value)]
            gap = 1 << symbol
            if symbol:
                remaining -= symbol
                gap |= (bits >> remaining) & ((1 << symbol) - 1)
            code += gap
            x = y = 0
            for bit in range(edge_bits):
                x |= ((code >> (2 * bit)) & 1) << bit
                y |= ((code >> (2 * bit + 1)) & 1) << bit
            rows.append((tile // tile_columns << edge_bits) | x)
            columns.append((tile % tile_columns << edge_bits) | y)
    return np.array(rows), np.array(columns)
