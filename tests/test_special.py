from numpy import Inf, array, round
import passive_auto_design.special as sp


def test_std_dev():
    z1 = array([25, 50])
    z2 = array([50, 50])
    assert sp.std_dev(z1, z2) == 1/3


def test_quality_factor():
    assert sp.quality_f(100 - 1j * 300) == -3.0


def test_dB():
    assert sp.dB(10) == 20
    assert sp.ihsr(3+0*1j, 3*1j) == Inf


def test_sp_calculation():
    assert sp.gamma(1j*25, 1j*50) == 1/3
    z_profile = array([50, 75, 100], dtype=complex)
    assert round(sp.reflexion_coef(z_profile, 10), 3) == -0.006 - 0.286*1j
    assert round(sp.transmission_coef(z_profile, 10), 3) == 1.04 - 0.002*1j
