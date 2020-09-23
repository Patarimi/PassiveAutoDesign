# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
from numpy import round
import passive_auto_design.structure.waveguide as wg
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

import passive_auto_design.structure.transformer as tf
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
    assert transfo.model == {'ls': 0.0001376861381145666,
                             'rs': 0.13257484962738228,
                             'lp': 0.0001376861381145666,
                             'rp': 0.13257484962738228,
                             'k': 0.9,
                             'cg': 8.854187812800001e-05,
                             'cm': 0.0035416751251200005,
                             }

import passive_auto_design.structure.lumped_element as LMP
def test_capacitor():
    """
    unity test for capacitor object
    """
    cap = LMP.Capacitor(1e-6, 1e-3, 1)
    assert cap.par["cap"] == 8.8541878128e-15

    cap.set_x_with_y("eps_r", "cap", 1e-15)
    assert cap.par["eps_r"] == 0.11294090917221976
    assert cap.par["cap"] == 1e-15

def test_resistor():
    """
    unity test for capacitor object
    """
    res = LMP.Resistor()
    assert res.par["res"] == 1e-12

    res.set_x_with_y("length", "res", 1e3)
    assert res.par["length"] == 1000000026385065.9
    assert res.par["res"] == 1e3

def test_inductor():
    """
    unity test for capacitor object
    """
    ind = LMP.Inductor()
    assert ind.par["ind"] == 1.5432565424041825e-10

    ind.set_x_with_y("k_1", "ind", 1e-9)
    assert ind.par["k_1"] == 8.196952235094303
    assert ind.par["ind"] == 1e-9
