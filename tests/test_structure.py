# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import design.structure as st
from design.substrate import COPPER, D5880

def test_siw():
    """
    unity test for SIW object
    """
    wr1 = st.SIW(COPPER, D5880, 2.4e-3)
#width not set, pphc should return an error
    with pytest.raises(ValueError):
        wr1.calc_pphc(29e9, 35e5)
    wr1.set_width(7.1e-3)
    assert round(wr1.f_c) == 14233805208
    wr1.set_fc(17e9)
    assert round(1000*wr1.width, 2) == 5.94
    assert round(wr1.calc_a_d(20e9), 4) == 0.0461
    assert round(wr1.calc_a_c(20e9), 6) == 0.004997
    assert round(wr1.calc_ksr(20e9), 6) == 1
    wr1.diel.rougthness = 0
    with pytest.raises(ValueError):
        wr1.calc_ksr(20e9)
    wr1.diel.rougthness = 0.0009
    assert round(wr1.calc_pphc(29e9, 35e5)) == 139370
    wr1.print_info()
    assert round(wr1.get_sparam(20e9, 10e-3), 2) == (-0.99+0.13j)

def test_af_siw():
    """
    unity test for AF-SIW object
    """
    with pytest.raises(ValueError):
        af1 = st.AF_SIW(COPPER, D5880, 2.4e-3, 0)
    af1 = st.AF_SIW(COPPER, D5880, 2.4e-3, 0.2e-3)
    af1.set_fc(17e9)
    assert round(1000*af1.width) == 6.0
    assert af1.calc_a_d(15e9) == 0
    assert round(af1.calc_ksr(20e9), 6) == 1
    af1.print_info()
