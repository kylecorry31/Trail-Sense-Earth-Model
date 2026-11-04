from .compound import CompoundOperator
from .fourier_series import FourierSeries
from .remove_latitude_trend import RemoveLatitudeTrend


class ClimateHarmonics(CompoundOperator):
    """
    Replaces the 12 monthly images with the annual cycle of every cell (see FourierSeries), and removes the latitude
    trend from the mean (see RemoveLatitudeTrend), which is the first image.
    """

    MEAN_INDEX = 0

    def __init__(self, harmonics, trend_degree):
        self.harmonics = harmonics
        self.trend_degree = trend_degree

    def operators(self):
        return [
            FourierSeries(self.harmonics),
            RemoveLatitudeTrend(self.trend_degree, [self.MEAN_INDEX]),
        ]
