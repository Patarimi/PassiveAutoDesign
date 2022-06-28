from numpy import sqrt, min, max, abs
from .physical_dimension import PhysicalDimension
from .constants import c0


class Frequency(PhysicalDimension):
    """
    Frequency class inherited from Physical Dimension.
    """
    unit = "Hz"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)

    def to_time(self):
        """
        Convert the frequency to equivalent period.
        """
        if self.scale == "lin":
            return Time(value=1 / self.value, scale=self.scale)
        return Time(value=-self.value, scale=self.scale)

    def to_wavelength(self, eps_r: float = 1):
        """
        Convert the frequency to the equivalent wavelength.
        eps_r : relative permittivity of the medium used.
        """
        f_lin = self.lin()
        return PhysicalDimension(
            value=sqrt(eps_r) * c0 / f_lin.value, scale="lin", unit="m"
        )

    def fractionnal_bandwidth(self):
        """
        Return the fractionnal BandWidth in percent.
        """
        f_min = min(self.lin().value)
        f_max = max(self.lin().value)
        return 100 * abs(f_max - f_min) / sqrt(f_max * f_min)


class Time(PhysicalDimension):
    """
    Time class inherited from Physical Dimension.
    """
    unit = "s"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)

    def to_freq(self):
        """
        Convert the period to equivalent frequency.
        """
        if self.scale == "lin":
            return Frequency(value=1 / self.value, scale=self.scale)
        return Frequency(value=-self.value, scale=self.scale)
