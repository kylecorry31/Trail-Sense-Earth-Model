from uptide import tidal
import math
import datetime

deg2rad = math.pi / 180.0

constituents = [
    "Q1",
    "O1",
    "P1",
    "K1",
    "N2",
    "M2",
    "S2",
    "K2",
    "L2",
    "M1",
    "J1",
    "MM",
    "MF",
    "M3",
]

def get_corrections(year):
    time = datetime.datetime(year, 1, 1, 0, 0, 0)
    H, s, h, p, N, pp = tidal.astronomical_argument(time)
    f, u = tidal.nodal_corrections(constituents, N, pp)
    v = tidal.tidal_arguments(constituents, time)
    kotlin = "TideConstituentCorrections(\n"
    for f, u, v in zip(f, u, v):
        uv = ((u + v) / deg2rad) % 360
        kotlin += f"\tConstituentCorrection({f}f, {uv}f),\n"
    kotlin += ")"
    return kotlin
