from .physical_dimension import PhysicalDimension


class PhaseNoise(PhysicalDimension):
    unit = "dBc/Hz"

    def __init__(self, scale="dB", **data):
        super().__init__(scale=scale, **data)


class IntegratedPhaseNoise(PhysicalDimension):
    unit = "rad"

    def __init__(self, scale="lin", **data):
        super().__init__(scale=scale, **data)
