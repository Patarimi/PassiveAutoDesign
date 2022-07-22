# -*- coding: utf-8 -*-
"""
This module give function to ease the design of RF-tapper
"""
import numpy as np
from scipy.special import i1
from scipy.integrate import quad
from passive_auto_design.special import gamma
from passive_auto_design.units.physical_dimension import PhysicalDimension


def linear_taper(_z_start, _z_stop, _n_step):
    """
    return the _n_step profile of impedance for a transition from
    _z_start to _z_stop
    """
    return PhysicalDimension(
        np.linspace(_z_start, _z_stop, _n_step, dtype=complex),
        scale="lin",
        unit=r"\Omega",
    )


def klopfenstein_taper(_z_start, _z_stop, _n_step, _rhomax=0.01):
    """
    return the _n_step profile of impedance for a transition from
    _z_start to _z_stop
    """
    rho0 = gamma(_z_start, _z_stop)
    z_mid = 0.5 * np.log(_z_stop * _z_start)
    n_mid = int(np.floor(_n_step / 2))
    a_coeff = np.arccosh(rho0.value / _rhomax)
    ln_z = np.zeros((_n_step,))
    for i in range(1, n_mid + 1):
        ln_z[i + n_mid] = z_mid + _rhomax * (
            1 + a_coeff**2 * __phi(a_coeff, i / n_mid)
        )
        ln_z[n_mid - i] = z_mid + _rhomax * (
            1 - a_coeff**2 * __phi(a_coeff, i / n_mid)
        )
    ln_z[n_mid] = z_mid + _rhomax
    return PhysicalDimension(np.exp(ln_z, dtype=complex), scale="lin", unit=r"\Omega")


def __phi(_a_coeff, _y_pos):
    phi_r = quad(__phase_equation, 0, _y_pos, args=_a_coeff)
    return phi_r[0]


def __phase_equation(x, a):
    a = np.abs(a)
    return i1(a * np.sqrt(1 - x**2)) / (a * np.sqrt(1 - x**2))
