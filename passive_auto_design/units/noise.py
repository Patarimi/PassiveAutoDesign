from .physical_dimension import PhysicalDimension


class PhaseNoise(PhysicalDimension):
    """
    Phase Noise PhysicalDimension, use for noise conversion (see ::converters).
    """

    unit: str = "dBc/Hz"

    def __init__(self, scale="dB", **data):
        super().__init__(scale=scale, **data)


class IntegratedPhaseNoise(PhysicalDimension):
    """
    Integrated Phase Noise PhysicalDimension, use for noise conversion (see ::converters).
    """

    unit: str = "rad"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)


class NoiseFigure(PhysicalDimension):
    """
    Noise Figure, use for RF-line Up and friis formula.
    """

    unit: str = ""

    def __init__(self, value, scale="dB", **data):
        super().__init__(value=value, scale=scale, **data)

    def to_temp(self, Tref=290):
        T = Tref * (self.lin() - 1)
        return NoiseTemperature(value=T.value)


class NoiseTemperature(PhysicalDimension):
    """
    Noise Temperature, use for RF-line Up.
    """

    unit: str = "K"

    def __init__(self, value, scale="lin", **data):
        super().__init__(value=value, scale=scale, **data)

    def to_figure(self, Tref=290):
        NF = (self / Tref + 1).dB()
        return NoiseFigure(NF.value)
