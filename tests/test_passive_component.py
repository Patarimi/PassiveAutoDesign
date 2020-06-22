# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: mpoterea
"""
import pytest
import numpy as np
import passive_auto_design.passive_component.coupler as cpl
import passive_auto_design.passive_component.balun as bln
import passive_auto_design.passive_component.Taper as tpr

modelmappath = 'tests/default.map'
def test_coupler():
    CPL = cpl.Coupler(1e9, 50, modelmappath)
    res = CPL.design(_maxiter=0)
    assert np.round(1000*res.x[0], 3) == 0
    assert np.round(res.x[1], 3) == 2
    assert np.round(1000*res.x[2], 3) == 1.16
    assert np.round(1000*res.x[3], 3) == 1.00e-03
    CPL.print(res)
    res = CPL.design(_maxiter=1)
   
def test_balun():
    ZS_TARG = np.array([20 + 1j*40])
    ZL_TARG = np.array([50 + 1j*0.1])
    F_TARG = np.array([4e9])
    BLN = bln.Balun(F_TARG, ZL_TARG, ZS_TARG, modelmappath)
    BLN.k = 0.5
    with pytest.raises(ValueError):
        res = BLN.design(1)
    BLN.k = 0.8
    res = BLN.design(1)
    BLN.enforce_symmetrical()
    BLN.enforce_symmetrical(False)
    res = BLN.design(1)
    BLN.print(res)

def test_taper():
    z_res = tpr.klopfenstein_taper(25, 50, 3)
    z_ref = [25.84, 35.71, 49.34]
    assert all(np.round(z_res,2) == z_ref)
    assert np.round(np.abs(tpr.calc_RL_tot(z_res, 45)),3) == 0.17
    z_res = tpr.linear_taper(25, 50, 3)
    z_ref = [25, 37.5, 50]
    assert all(np.round(z_res,2) == z_ref)
