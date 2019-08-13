# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import passive_auto_design.structure as st
from passive_auto_design.substrate import COPPER, D5880

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

def test_transformer():
    """
    unity test for tranformer object
    """
    geo = {'di':20,
           'n_turn':2,
           'width':1e-3,
           'gap':2e-3,
           'height':1e-6}
    transfo = st.Transformer(geo, geo)
    transfo.set_primary(geo)
    transfo.set_secondary(geo)
    assert transfo.generate_spice_model(0.99) == 'Transformer Model\n\n\
VIN\t\t3\t0\tDC\t0\tAC\t1\n\
RIN\t\t3\tIN\t50\n\
ROUT\tOUT\t0\t50\n\
RCPL\tCPL\t0\t50\n\
RISO\tISO\t0\t50\n\n\
L1\t\tIN\t1\t226079425.7p\n\
R1\t\t1\tOUT\t2256609.9m\n\
L2\t\tCPL\t2\t226079425.7p\n\
R2\t\t2\tISO\t2256609.9m\n\
K\t\tL1\tL2\t0.99\n\
CG1\t\tIN\t0\t0.0f\n\
CG2\t\tOUT\t0\t0.0f\n\
CG3\t\tISO\t0\t0.0f\n\
CG4\t\tCPL\t0\t0.0f\n\
CM1\t\tIN\tCPL\t500.4f\n\
CM2\t\tISO\tOUT\t500.4f\n\n'
