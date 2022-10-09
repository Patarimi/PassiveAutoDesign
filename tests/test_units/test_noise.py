import passive_auto_design.units.noise as ns


def test_INP():
    ns.IntegratedPhaseNoise(value=[-40, -80, -120])


def test_NF():
    NF = ns.NoiseFigure(value=[0.1, 1, 3])
    assert round(NF.to_temp(), 1) == ns.NoiseTemperature(value=[6.8, 75.1, 288.6])


def test_Temp():
    Temp = ns.NoiseTemperature(290)
    assert round(Temp.to_figure(), 1) == ns.NoiseFigure(3)
