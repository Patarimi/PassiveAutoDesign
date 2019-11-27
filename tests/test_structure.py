# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import passive_auto_design.structure.Waveguide as wg
import passive_auto_design.structure.Transformer as tf
from passive_auto_design.substrate import COPPER, D5880

def test_siw():
    """
    unity test for SIW object
    """
    wr1 = wg.SIW(COPPER, D5880, 2.4e-3)
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
        af1 = wg.AF_SIW(COPPER, D5880, 2.4e-3, 0)
    af1 = wg.AF_SIW(COPPER, D5880, 2.4e-3, 0.2e-3)
    af1.set_width(6.94e-3)
    assert round(af1.f_c*1e-9, 1) == 14.6
    af1.set_fc(17e9)
    assert round(1000*af1.width, 1) == 5.9
    assert af1.calc_a_d(15e9) == 0
    assert round(af1.calc_ksr(20e9), 6) == 1
    af1.f_c = 0
    af1.print_info()
    with pytest.raises(ValueError):
        af1.calc_fc(0, 1)

def test_transformer():
    """
    unity test for tranformer object
    """
    geo = {'di':20,
           'n_turn':2,
           'width':1e-3,
           'gap':2e-3,
           'height':1e-6}
    transfo = tf.Transformer(geo, geo)
    transfo.set_primary(geo)
    transfo.set_secondary(geo)
    assert transfo.generate_spice_model(0.99) == 'Transformer Model\n\n\
L0\tIN\t1\t127.14u\n\
R0\t1\tOUT\t2.26K\n\
L1\tCPL\t2\t127.14u\n\
R1\t2\tISO\t2.26K\n\
K0\tL0\tL1\t0.99\n\
C0\tIN\t0\t0\n\
C1\tOUT\t0\t0\n\
C2\tCPL\t0\t0\n\
C3\tISO\t0\t0\n\
C4\tIN\tCPL\t558.85f\n\
C5\tISO\tOUT\t558.85f\n'
