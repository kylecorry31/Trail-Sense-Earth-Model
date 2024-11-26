import pyTMD
import pyTMD.astro
from pyTMD.time import timescale
import math

deg2rad = math.pi / 180.0
constituents = [
    'M2',
    'S2',
    'N2',
    'K1',
    'M4',
    'O1',
    'M6',
    'MK3',
    'S4',
    'MN4',
    'NU2',
    'S6',
    'MU2',
    '2N2',
    'OO1',
    'S1',
    'M1',
    'J1',
    'MM',
    'SSA',
    'SA',
    'MSF',
    'MF',
    'Q1',
    'T2',
    'R2',
    '2Q1',
    'P1',
    '2SM2',
    'M3',
    'L2',
    '2MK3',
    'K2',
    'M8',
    'MS4'
]


def get_corrections(year):
    t = timescale().from_calendar(year, 1, 1, 0, 0,
                                  0).to_deltatime((1992, 1, 1, 0, 0, 0))
    lower_constituents = [constituent.lower() for constituent in constituents]
    pu, pf, g = pyTMD.arguments.arguments(
        t + 48622,
        lower_constituents
    )

    corrections = {}
    for i in range(len(constituents)):
        uv = (g[0][i] + pu[0][i] / deg2rad) % 360
        corrections[constituents[i].upper()] = {
            'f': float(pf[0][i]), 'uv': float(uv)}

    # Add RHO and LAM2
    corrections['RHO'] = {'f': corrections['M2']['f'] * corrections['K1']
                          ['f'], 'uv': corrections['M2']['uv'] - corrections['K1']['uv']}
    corrections['LAM2'] = corrections['M2']

    return corrections
