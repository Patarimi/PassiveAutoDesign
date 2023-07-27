from numpy import round
import passive_auto_design.units.converters as cv
from passive_auto_design.units.noise import PhaseNoise
from passive_auto_design.units.time import Frequency


def test_inp():
    f_0 = 2.3e9
    freq_pn = Frequency(value=[100, 1e3, 100e6])
    pn_dbc = PhaseNoise(value=[-7.5, -30, -131.7])

    ipn = cv.int_phase_noise(pn_dbc, freq_pn)
    assert round(ipn.value * 1e6) == 14393347
    f_min = Frequency(value=(1e6,))
    ipn1 = cv.int_phase_noise(pn_dbc, freq_pn, f_min=f_min)
    assert round(ipn1.value * 1e6) == 758
    ipn2 = cv.int_phase_noise(pn_dbc, freq_pn, f_max=f_min)
    assert round(ipn2.value * 1e3) == 15193

    assert round(cv.to_jitter(ipn1 + ipn2, f_0).value * 1e12) == 381
