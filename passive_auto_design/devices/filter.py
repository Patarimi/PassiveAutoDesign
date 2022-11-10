"""
specify a filter mask from a given mask
"""
from numpy import sqrt
from math import ceil
from ..units.time import Frequency
from ..units.physical_dimension import PhysicalDimension


class Filter:
    Order: int

    def __init__(
        self,
        f_pass: Frequency,
        f_stop: Frequency,
        ripple: PhysicalDimension,
        atten: PhysicalDimension,
    ):
        """
        f_pass: pass-band edge frequency
        f_stop: stop-band edge frequency
        ripple: maximum ripple in the pass band in dB
        atten: minimum attenuation in the stop band in dB
        """
        epsilon = sqrt(ripple.lin() - 1)
        a_2 = atten.lin()
        k1 = PhysicalDimension(value=epsilon / sqrt(a_2 - 1))
        k = f_pass / f_stop
        self.Order = ceil(k1.dB() / k.dB())
