# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: Patarimi
"""
import numpy as np
import passive_auto_design.devices.coupler as cpl
import passive_auto_design.devices.balun as bln
import passive_auto_design.devices.taper as tpr
from passive_auto_design.special import reflexion_coef, transmission_coef


def test_coupler():
    """
    test function for the coupler class
    """
    coupler = cpl.Coupler(1e9, 50)
    assert round(1e9 * coupler.l, 3) == 11.252
    assert round(1e12 * coupler.c, 3) == 4.501
    assert str(coupler) == "L: 11.2523 nH\tC: 4.5009 pF"


def test_balun():
    """
    test function for the balun class
    """
    zs_target = 100 - 1j * 300
    zl_target = 50 - 1j * 100
    f_target = 60e9
    balun = bln.Balun(f_target, zl_target, zs_target, 0.8)
    L1, L2 = balun.design()
    assert round(L1[1] * 1e12) == 157
    assert round(L1[0] * 1e12) == 1552
    assert round(L2[1] * 1e12) == 580
    assert round(L2[0] * 1e12) == 3369

    delta_X = balun.enforce_symmetrical(_verbose=True)
    assert round(delta_X[0]) == 304
    assert round(delta_X[1]) == 190

    delta_X = balun.enforce_symmetrical(side="source", _verbose=True)
    assert round(delta_X[0]) == 122
    assert round(delta_X[1]) == -128

    assert (
        str(balun)
        == "target : fc=60 GHz\tzs=50 - j100 $\Omega$\tzl=100 - j300 $\Omega$"
    )


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
