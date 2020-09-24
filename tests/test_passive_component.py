# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: mpoterea
"""
import numpy as np
import pytest
import passive_auto_design.components.coupler as cpl
import passive_auto_design.components.balun as bln
import passive_auto_design.components.taper as tpr
from passive_auto_design.special import reflexion_coef, transmission_coef

modelmappath = 'tests/default.map'
def test_coupler():
    CPL = cpl.Coupler(1e9, 50, modelmappath)
    res = CPL.design(_maxiter=0)
    assert round(1e6*res.x[0], 3) == 0.015
    assert round(res.x[1], 3) == 2
    assert round(1e6*res.x[2], 3) == 1156.925
    assert round(1e6*res.x[3], 3) == 0.5
    CPL.print(res)
    res = CPL.design(_maxiter=1)
   
def test_balun():
    ZS_TARG = np.array([20 + 1j*40])
    ZL_TARG = np.array([50 + 1j*0.1])
    F_TARG = np.array([4e9])
    BLN = bln.Balun(F_TARG, ZL_TARG, ZS_TARG)
    BLN.enforce_symmetrical()
    res = BLN.design(1)
    BLN.enforce_symmetrical(False)
    BLN.is_symmetrical = False
    res = BLN.design(1)
    BLN.print(res)
    BLN.transfo.model["k"] = 0.2
    with pytest.raises(ValueError):
        res = BLN.design(1)

def test_taper():
    z_res = tpr.klopfenstein_taper(25, 50, 3)
    z_ref = [25.84, 35.71, 49.34]
    assert all(np.round(z_res,2) == z_ref)
    assert np.round(np.abs(reflexion_coef(z_res, 45)),3) == 0.17
    assert np.round(np.abs(transmission_coef(z_res, 45)), 3) == 0.986
    z_res = tpr.linear_taper(25, 50, 3)
    z_ref = [25, 37.5, 50]
    assert all(np.round(z_res,2) == z_ref)
