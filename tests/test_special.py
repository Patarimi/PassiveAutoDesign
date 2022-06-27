from pytest import raises
from numpy import inf, array, round
import passive_auto_design.special as sp
from passive_auto_design.units.physical_dimension import PhysicalDimension


def test_std_dev():
    z1 = array([25, 50])
    z2 = array([50, 50])
    assert sp.std_dev(z1, z2) == 1 / 3


def test_quality_factor():
    assert sp.quality_f(100 - 1j * 300) == -3.0


def test_ihsr():
    assert sp.ihsr(3 + 0 * 1j, 3 * 1j) == inf
    assert sp.ihsr(3, 3) == 0
    assert round(10 ** (-3 / 10), 1) == 0.5


def test_sp_calculation():
    assert sp.gamma(1j * 25, 1j * 50) == 1 / 3
    z_profile = array([50, 75, 100], dtype=complex)
    assert round(sp.reflexion_coef(z_profile, 10), 3) == -0.006 - 0.286 * 1j
    assert round(sp.transmission_coef(z_profile, 10), 3) == 1.04 - 0.002 * 1j


def test_frac_bw():
    assert round(sp.frac_bandwidth(1e9, 6e9)) == 204


def test_friis():
    noise_factor = PhysicalDimension(value=[3, 6], scale="dB")
    gain = PhysicalDimension(value=15, scale="dB")
    f_out = sp.friis(noise_factor, gain)
    assert round(f_out.value, 2) == 3.2
    gain = PhysicalDimension(value=[15, 18], scale="dB")
    with raises(ValueError):
        sp.friis(noise_factor, gain)
