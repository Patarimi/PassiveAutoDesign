import pytest
from numpy import round
import passive_auto_design.components.waveguide as wg
from passive_auto_design.substrate import COPPER, D5880


def test_waveguide():
    """
    unity test for SIW object
    """
    wr1 = wg.Waveguide(COPPER, D5880, 2.4e-3)
# width not set, pphc should return an error
    with pytest.raises(ValueError):
        wr1.calc_pphc(29e9, 35e5)
    wr1.width = 7.1e-3
    assert round(wr1.first_cut_off) == 14233805208
    wr1.first_cut_off = 17e9
    assert round(1000*wr1.width, 2) == 5.94
    assert round(wr1.calc_a_d(20e9), 4) == 0.0461
    assert round(wr1.calc_a_c(20e9), 6) == 0.004997
    assert round(wr1.calc_ksr(20e9), 6) == 1
    assert round(wr1.calc_lambda(20e9), 6) == 0.028455
    wr1.diel.roughness = 0
    with pytest.raises(ValueError):
        wr1.calc_ksr(20e9)
    wr1.diel.roughness = 0.0009
    assert round(wr1.calc_pphc(29e9, 35e5)) == 139370
    assert round(wr1.calc_aphc(29e9, 533.15)) == 131
    wr1.print_info()
    assert round(wr1.get_sparam(20e9, 10e-3), 2) == (-0.99+0.13j)


def test_af_siw():
    """
    unity test for AF-SIW object
    """
    with pytest.raises(ValueError):
        wg.AF_SIW(COPPER, D5880, 2.4e-3, 0)
    af1 = wg.AF_SIW(COPPER, D5880, 2.4e-3, 0.2e-3)
    af1.width = 6.94e-3
    assert round(af1.first_cut_off*1e-9, 1) == 14.6
    af1.first_cut_off = 17e9
    assert round(1000*af1.width, 1) == 5.9
    assert af1.calc_a_d(15e9) == 0
    assert round(af1.calc_ksr(20e9), 6) == 1
    assert round(af1.calc_pphc(29e9, 35e5)) == 139389
    assert round(af1.calc_aphc(29e9, 533.15)) == 1936
    af1.first_cut_off = 0
    af1.print_info()
    with pytest.raises(ValueError):
        af1.f_cut_off(0, 1)
