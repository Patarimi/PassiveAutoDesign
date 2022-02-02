from passive_auto_design import unit


def test_freq():
    assert unit.Frequency(9e9) == "9 GHz"


def test_impedance():
    assert unit.Impedance(50 + 0.1 * 1j) == r"50 + j100 m $\Omega$"
    assert unit.Impedance(50 - 0.1 * 1j) == r"50 - j100 m $\Omega$"
