# Geo point file format (`.tsgeo`)

A geo point file is a compact list of points on the globe. Each point has a position and the same set of numeric
fields. The points are grouped into square cells, and the cells are packed into small blocks, each compressed on its
own. A reader only needs the header, metadata, and directory, plus the blocks around a location, so the file can be read
without decompressing or loading the rest of it.

## Layout

```
+-------------------+  offset 0
| Header            |  16 bytes
+-------------------+  offset 16
| Metadata          |  UTF-8 JSON, metadata_length bytes
+-------------------+
| Block directory   |  (block_count + 1) x 12 bytes
+-------------------+
| Block 0           |  raw deflate
| Block 1           |
| ...               |
+-------------------+  end of file
```

All integers are unsigned and little endian.

## Header

| Offset | Type | Field | Notes |
| --- | --- | --- | --- |
| 0 | 4 bytes | `magic` | `TSGP` (`54 53 47 50`) |
| 4 | u8 | `version` | Format version, currently `1`. Readers must reject versions they do not know. |
| 5 | 3 bytes | reserved | Zero |
| 8 | u32 | `metadata_length` | Bytes of metadata |
| 12 | u32 | `block_count` | Number of blocks |

## Metadata

A UTF-8 JSON object:

| Key | Type | Meaning |
| --- | --- | --- |
| `cell_degrees` | int | The size of a cell in degrees. Must divide both 180 and 360 (ex. 1, 5, 10, 15). |
| `decimals` | int | Positions are stored to this many decimal places of a degree, 0 to 7, the same for every point |
| `count` | int | The number of points |
| `fields` | array | The fields every point has, in the order they are stored (see below). Can be empty. |
| `properties` | object | Anything the reader of this kind of file needs, such as what it is and what its fields mean. The format does not interpret it. |

Each field:

| Key | Type | Meaning |
| --- | --- | --- |
| `name` | string | Unique within the file |
| `bytes` | int | 1 to 4. The field is stored as an unsigned integer of this many bytes. |
| `step` | number | The size of one unit of the stored integer |
| `offset` | number | `value = stored * step + offset` |

Writers round each value to the nearest step and clamp it to what fits (`0` to `2^(8 * bytes) - 1`).

## Cells and positions

```
rows    = 180 / cell_degrees
columns = 360 / cell_degrees
cells   = rows * columns
scale   = 10^decimals          (positions per degree)
steps   = cell_degrees * scale (positions along each side of a cell)
```

Cells are numbered in rows from the south pole to the north pole, and each row from the antimeridian (-180) east:
`cell = row * columns + column`.

A writer turns a coordinate into whole positions:

```
latitude_position  = clamp(round((latitude + 90) * scale), 0, 180 * scale - 1)
longitude_position = round((longitude + 180) * scale) mod (360 * scale)
row, y    = divmod(latitude_position, steps)
column, x = divmod(longitude_position, steps)
position  = y * steps + x      (the position within the cell)
```

So 180 east is stored as -180, and the north pole as one position south of it (`90 - 10^-decimals`).

A reader turns it back with:

```
latitude  = (row * steps + y - 90 * scale) / scale
longitude = (column * steps + x - 180 * scale) / scale
```

Subtracting in whole positions before dividing gives the closest double to the stored decimal (ex. 44.27, not
44.27000000000001).

## Block directory

`block_count + 1` entries of 12 bytes:

| Offset | Type | Field |
| --- | --- | --- |
| 0 | u32 | `first_cell`: the first cell with points in the block |
| 4 | u32 | `last_cell`: the last cell with points in the block |
| 8 | u32 | `offset`: where the block starts in the file |

The last entry only marks the end: both of its cells are `cells`, and its offset is the end of the last block (the file
size). Block `i` is the bytes from `offset[i]` up to `offset[i + 1]`.

Blocks are in cell order and do not overlap (`first_cell <= last_cell < next first_cell`), and all of a cell's points
are in one block. A cell that is not between the first and last cell of any block has no points, so the reader skips
it without reading anything. A cell inside a block's range may still have no points.

## Blocks

Each block is compressed with raw deflate (RFC 1951, no zlib or gzip header). Decompressed, it is:

1. `cell_count` (varint): the number of cells with points in the block
2. `cell_count` varints: the gap before each cell, `cell - previous_cell - 1`, where the previous cell of the first one
   is `first_cell - 1` (so the first gap is always 0)
3. `cell_count` varints: the number of points in each cell
4. For every point, cell by cell: its position within the cell (see above) as a varint. The points of a cell are sorted
   by position (so by latitude, then longitude), and each is stored as the difference from the one before it in the
   cell. The first point of a cell is stored as is.
5. For each field, in order: byte 0 of the field for every point in the block, then byte 1 for every point, and so
   on (`bytes * points in the block` bytes), with the points in the same order as the positions

Varints are unsigned LEB128: 7 bits per byte, least significant group first, with the high bit set on every byte but
the last.

Storing each byte of a field separately (byte planes) keeps similar numbers together, which compresses much better than
storing each point's bytes together. Delta coding the sorted positions turns them into small numbers.

Writers group consecutive cells into a block until adding the next cell would take it over a target number of points
(2048 by default). A cell with more points than that is a block on its own. A block must be at most 1 MB decompressed
(readers can reject larger blocks).

## Compatibility

- A change to the layout (header, directory, or blocks) needs a new `version`. Older readers ignore the file.
- New metadata keys and properties can be added without a new version, since readers ignore keys they do not know.
- What a file is and what its fields mean is up to its `properties`. Readers should check a type property (ex.
  `properties.type`) before using a file, so a change to how a kind of file is used should use a new type.
