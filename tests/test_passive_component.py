# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: mpoterea
"""
import numpy as np
import pytest
import os
import passive_auto_design.passive_component as pac
import passive_auto_design.substrate as sub
from passive_auto_design.ngspice_warper import set_path

SUB = sub.Substrate('tests/passive_component_tech.yml')
def test_coupler():
    CPL = pac.Coupler(SUB)
    if os.name == 'nt':
        set_path('../ng_spice/')
        res = CPL.design(1e9, 50, _maxiter=0)
        assert np.round(1000*res.x[0], 3) == 1.10e-02
        assert np.round(res.x[1], 3) == 2
        assert np.round(1000*res.x[2], 3) == 1.258
        assert np.round(1000*res.x[3], 3) == 2.00e-03
        res = CPL.design(1e9, 50, _maxiter=1)
        CPL.print(res)
   
def test_balun():
    BLN = pac.Balun(SUB)
    ZS_TARG = np.array([20+1j*40])
    ZL_TARG = np.array([50 + 1j*0])
    F_TARG = np.array([4e9])
    if os.name == 'nt':
        res = BLN.design(F_TARG, ZS_TARG, ZL_TARG, 1)
        BLN.print(res)

def test_special():
    with pytest.raises(ValueError):
        assert pac.std_dev(np.array([20+1j*40]), np.array([20+1j*40, 50]))
