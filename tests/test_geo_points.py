import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import geo_points
from scripts.geo_points import Field, GeoPointFormat


def test_round_trips_positions_and_values():
    rng = np.random.default_rng(1)
    latitudes = rng.uniform(-90, 90, 5000)
    longitudes = rng.uniform(-180, 180, 5000)
    values = rng.uniform(0, 1000, 5000)
    file_format = GeoPointFormat(
        decimals=4, fields=(Field("value", bytes=2, step=0.5, offset=-10),), block_points=256, properties={"a": 1}
    )

    metadata, read_latitudes, read_longitudes, read_values = geo_points.read(
        file_format.pack(latitudes, longitudes, {"value": values})
    )

    # Sorted by the stored position, since points can round to the same latitude
    order = np.lexsort((longitudes.round(4), latitudes.round(4)))
    read_order = np.lexsort((read_longitudes.round(4), read_latitudes.round(4)))
    assert metadata["count"] == 5000 and metadata["properties"] == {"a": 1}
    np.testing.assert_allclose(read_latitudes[read_order], latitudes[order], atol=0.5e-4 + 1e-9)
    np.testing.assert_allclose(read_longitudes[read_order], longitudes[order], atol=0.5e-4 + 1e-9)
    np.testing.assert_allclose(read_values["value"][read_order], values[order], atol=0.25 + 1e-9)


def test_keeps_exact_decimals_and_wraps_the_edges():
    file_format = GeoPointFormat(decimals=7)
    _, latitudes, longitudes, _ = geo_points.read(
        file_format.pack([44.2705803, -90, 90, 10], [-71.3033311, -180, 179.9999999, 180])
    )

    assert sorted(zip(latitudes.round(7), longitudes.round(7))) == [
        (-90.0, -180.0),
        (10.0, -180.0),
        (44.2705803, -71.3033311),
        (89.9999999, 179.9999999),
    ]


def test_limits_values_to_what_fits():
    file_format = GeoPointFormat(fields=(Field("value", bytes=1),))
    _, _, _, values = geo_points.read(file_format.pack([0, 1], [0, 1], {"value": [-5, 300]}))
    assert sorted(values["value"]) == [0, 255]


def test_fits_as_many_points_as_the_budget_allows():
    rng = np.random.default_rng(2)
    latitudes, longitudes = rng.uniform(-60, 60, 2000), rng.uniform(-180, 180, 2000)
    file_format = GeoPointFormat()

    data, count = file_format.fit(latitudes, longitudes, {}, 4000)

    assert len(data) <= 4000 < len(file_format.pack(latitudes[: count + 1], longitudes[: count + 1]))
    assert geo_points.read(data)[0]["count"] == count


def test_an_empty_file_has_no_blocks():
    data = GeoPointFormat().pack([], [])
    assert geo_points.read(data)[1].size == 0
    metadata_length = struct.unpack_from("<I", data, 8)[0]
    assert len(data) == geo_points.HEADER_BYTES + metadata_length + geo_points.DIRECTORY_ENTRY_BYTES


def test_rejects_unsupported_shapes():
    for arguments in ({"cell_degrees": 7}, {"decimals": 8}, {"fields": (Field("value", bytes=5),)}):
        try:
            GeoPointFormat(**arguments)
        except ValueError:
            continue
        raise AssertionError(f"{arguments} was accepted")


if __name__ == "__main__":
    # Runs without pytest: python tests/test_geo_points.py
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"passed {name}")
