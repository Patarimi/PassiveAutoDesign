from passive_auto_design.devices.filter import Filter
from passive_auto_design.units.time import Frequency
from passive_auto_design.units.physical_dimension import PhysicalDimension


def test_filter():
    f_pass = Frequency(1e3)
    f_stop = Frequency(5e3)
    ripple = PhysicalDimension(value=1, scale="dB")
    atten = PhysicalDimension(value=40, scale="dB")

    filter = Filter(f_pass=f_pass, f_stop=f_stop, ripple=ripple, atten=atten)
    assert filter.Order == 4
