import passive_auto_design.units.time as t
from passive_auto_design.units.physical_dimension import PhysicalDimension, NDArray


def test_frequency():
    freq = t.Frequency(value=[1e9, 10e9])
    period = freq.to_time()
    assert period == t.Time(value=[1e-9, 0.1e-9])
    wl = round(freq.to_wavelength(eps_r=4), 8)
    assert wl == PhysicalDimension(value=[0.59958492, 0.05995849], unit="m")


def test_frac_bw():
    freq = t.Frequency(value=[1e9, 6e9])
    assert round(freq.fractionnal_bandwidth()) == 204


def test_time():
    period = t.Time(value=[1e-9, 10e-6])
    freq = period.dB().to_freq()

    assert freq == t.Frequency(value=[1e9, 1e5]).dB()
