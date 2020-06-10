# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import passive_auto_design.structure.Waveguide as wg
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
    assert round(wr1.calc_lambda(20e9), 6) == 0.028455
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

import passive_auto_design.structure.Transformer as tf
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
L0\tIN\t1\t127.14389u\n\
R0\t1\tOUT\t2.25661K\n\
L1\tCPL\t2\t127.14389u\n\
R1\t2\tISO\t2.25661K\n\
K0\tL0\tL1\t0.99\n\
C0\tIN\t0\t0\n\
C1\tOUT\t0\t0\n\
C2\tCPL\t0\t0\n\
C3\tISO\t0\t0\n\
C4\tIN\tCPL\t558.84682f\n\
C5\tISO\tOUT\t558.84682f\n'

import passive_auto_design.structure.lumped_element as LMP
def test_capacitor():
    """
    unity test for capacitor object
    """
    CAP = LMP.Capacitor(1e-6, 1e-3, 1)
    assert CAP.par["cap"] == 8.8541878128e-15
    
    CAP.set_x_with_y("eps_r", "cap", 1e-15)
    assert CAP.par["eps_r"] == 0.11294090917221976
    assert CAP.par["cap"] == 1e-15
    
def test_resistor():
    """
    unity test for capacitor object
    """
    RES = LMP.Resistor()
    assert RES.par["res"] == 1e-12
    
    RES.set_x_with_y("length", "res", 1e3)
    assert RES.par["length"] == 1000000026385065.9
    assert RES.par["res"] == 1e3

def test_inductor():
    """
    unity test for capacitor object
    """
    IND = LMP.Inductor()
    assert IND.par["ind"] == 1.5432565424041825e-10
    
    IND.set_x_with_y("k_1", "ind", 1e-9)
    assert IND.par["k_1"] == 8.196952235094303
    assert IND.par["ind"] == 1e-9
