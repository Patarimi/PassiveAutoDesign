# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: Patarimi
"""
import numpy as np
import pytest
import passive_auto_design.components.coupler as cpl
import passive_auto_design.components.balun as bln
import passive_auto_design.components.taper as tpr
from passive_auto_design.special import reflexion_coef, transmission_coef

MODEL_MAP_PATH = 'tests/default.map'


def test_coupler():
    """
    test function for the coupler class
    """
    coupler = cpl.Coupler(1e9, 50, MODEL_MAP_PATH)
    res = coupler.design(_maxiter=0)
    assert round(1e6*res.x[0], 3) == 0.015
    assert round(res.x[1], 3) == 2
    assert round(1e6*res.x[2], 3) == 1156.925
    assert round(1e6*res.x[3], 3) == 0.5
    coupler.print(res)
    coupler.design(_maxiter=1)


def test_balun():
    """
    test function for the balun class
    """
    zs_target = np.array([20 + 1j*40])
    zl_target = np.array([50 + 1j*0.1])
    f_target = np.array([4e9])
    balun = bln.Balun(f_target, zl_target, zs_target)
    balun.enforce_symmetrical()
    balun.design(1)
    balun.enforce_symmetrical(False)
    balun.is_symmetrical = False
    res = balun.design(1)
    balun.print(res)
    balun.transfo.model["k"] = 0.2
    with pytest.raises(ValueError):
        balun.design(1)


def test_taper():
    """
    test function for the taper class
    """
    z_res = tpr.klopfenstein_taper(25, 50, 3)
    z_ref = [25.84, 35.71, 49.34]
    assert all(np.round(z_res, 2) == z_ref)
    assert np.round(np.abs(reflexion_coef(z_res, 45)), 3) == 0.17
    assert np.round(np.abs(transmission_coef(z_res, 45)), 3) == 0.986
    z_res = tpr.linear_taper(25, 50, 3)
    z_ref = [25, 37.5, 50]
    assert all(np.round(z_res, 2) == z_ref)
