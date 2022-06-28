from .physical_dimension import PhysicalDimension


class PhaseNoise(PhysicalDimension):
    """
    Phase Noise PhysicalDimension, use for noise conversion (see ::converters).
    """
    unit = "dBc/Hz"

    def __init__(self, scale="dB", **data):
        super().__init__(scale=scale, **data)


class IntegratedPhaseNoise(PhysicalDimension):
    """
    Integrated Phase Noise PhysicalDimension, use for noise conversion (see ::converters).
    """
    unit = "rad"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)
