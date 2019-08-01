# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import design.structure as st
from design.substrate import COPPER, AIR

def test_structure():
    WR = st.SIW(COPPER, AIR, 2.4e-3)
    with pytest.raises(ValueError):
        WR.calc_pphc(29e9, 35e5)
    WR.set_width(7.1e-3)
    assert round(WR.calc_pphc(29e9, 35e5)) == 94966
