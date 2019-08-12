# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import design.structure as st
from design.substrate import COPPER, D5880

def test_SIW():
    WR = st.SIW(COPPER, D5880, 2.4e-3)
#width not set, pphc should return an error
    with pytest.raises(ValueError):
        WR.calc_pphc(29e9, 35e5)
    WR.set_width(7.1e-3)
    assert round(WR.f_c) == 14233805208
    WR.set_fc(17e9)
    assert round(1000*WR.width,2) == 5.94
    assert round(WR.calc_a_d(20e9),4) == 0.0461
    assert round(WR.calc_a_c(20e9),6) == 0.004997
    assert round(WR.calc_ksr(20e9),6) == 1
    WR.diel.rougthness = 0
    with pytest.raises(ValueError):
        WR.calc_ksr(20e9)
    WR.diel.rougthness = 0.0009
    assert round(WR.calc_pphc(29e9, 35e5)) == 139370
    WR.print_info()
    assert round(WR.get_sparam(20e9, 10e-3), 2) == (-0.99+0.13j)
