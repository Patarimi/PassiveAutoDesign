# -*- coding: utf-8 -*-
"""
This module give function to ease the design of RF-tapper
"""
import numpy as np
from scipy.special import i1
from scipy.integrate import quad

def __gamma(_z_load, _z0=50):
    return (_z0-_z_load)/(_z0+_z_load)

def calc_RL_tot(_z_steps, _phi_step):
    """
    return the coefficient reflexion of a given sequence of transmission lines
    with the given_z_steps profile and equal length of _phi_steps degrees
    """
    n_step = _z_steps.size
    z_tot = _z_steps[-1:]
    for i in range(n_step):
        z_0 = _z_steps[n_step-i-1]
        z_tot = z_0*(z_tot+1j*z_0*np.tan(_phi_step))/(z_0+1j*z_tot*np.tan(_phi_step))
    return __gamma(_z_steps[0], z_tot)

def klopfenstein_tapper(_z_start, _z_stop, _n_step, _rhomax=0.01):
    """
    return the _n_step profile of impedance for a transition from
    _z_start to _z_stop
    """
    rho0 = __gamma(_z_start, _z_stop)
    z_mid = 0.5*np.log(_z_stop*_z_start)
    n_mid = int(np.floor(_n_step/2))
    a_coeff = np.arccosh(rho0/_rhomax)
    ln_z = np.zeros((_n_step,))
    for i in range(1, n_mid+1):
        ln_z[i+n_mid] = z_mid + _rhomax*(1+a_coeff**2*__phi(a_coeff, i/n_mid))
        ln_z[n_mid-i] = z_mid + _rhomax*(1-a_coeff**2*__phi(a_coeff, i/n_mid))
    ln_z[n_mid] = z_mid + _rhomax
    return np.exp(ln_z)

def __phi(_a_coeff, _y_pos):
    phi_r = quad(lambda x: i1(_a_coeff*np.sqrt(1-x**2))/(_a_coeff*np.sqrt(1-x**2)), 0, _y_pos)
    return phi_r[0]
