"""

"""
from numpy import sqrt
from .physical_dimension import PhysicalDimension
from .constants import c0


class Frequency(PhysicalDimension):
    unit = "Hz"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)

    def to_time(self):
        if self.scale == "lin":
            return Time(value=1 / self.value, scale=self.scale)
        return Time(value=-self.value, scale=self.scale)

    def to_wavelength(self, eps_r: float = 1):
        f_lin = self.lin()
        return PhysicalDimension(
            value=sqrt(eps_r) * c0 / f_lin.value, scale="lin", unit="m"
        )


class Time(PhysicalDimension):
    unit = "s"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)

    def to_freq(self):
        if self.scale == "lin":
            return Frequency(value=1 / self.value, scale=self.scale)
        return Frequency(value=-self.value, scale=self.scale)
