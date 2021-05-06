# -*- coding: utf-8 -*-
"""
Define constants and function dedicated to RF-conception
"""
import numpy as np
from numba import njit, vectorize

# Constants
u0 = 4*np.pi*1e-7  # H/m
c0 = 299792458  # m/s
eps0 = 8.8541878128e-12  # F/m
eta0 = np.sqrt(u0/eps0)  # Ohm
Nm_to_dBcm = 8.686 / 100


# Other functions
@vectorize(cache=True)
def gamma(_z_load, _z0=50):
    return (_z0-_z_load)/(_z0+_z_load)


@njit(cache=True)
def std_dev(measured, targeted):
    """
        return the standard deviation between an array_like of results and their references.
    """
    tmp = np.abs(gamma(measured, targeted)) ** 2
    return np.sqrt(np.sum(tmp))


@vectorize(cache=True)
def dB(c):
    """
        Return the decibel value of the given imaginary number.
    """
    if c == 0:
        return -np.inf
    return 10*np.log10(np.abs(c))


@vectorize(cache=True)
def lin(d):
    """
        return the linear magnitude of the given magnitude in decibel
    """
    return 10**(d/10)


@vectorize(cache=True)
def ihsr(_s31, _s21):
    """
        Return the IHSR (Ideal Hybrid Splitting Ratio) for the given gains
    """
    if _s21 == 1j*_s31 or _s21 == -1j*_s31:
        return np.inf
    ihsr_log = dB((_s21 - 1j * _s31) / (_s21 + 1j * _s31))
    return -np.minimum(ihsr_log, -ihsr_log)


@vectorize(cache=True)
def quality_f(_z):
    """
    return the quality factor of a components
    """
    return np.imag(_z)/np.real(_z)


@njit(cache=True)
def reflexion_coef(_z_steps, _phi_step):
    """
    return the coefficient reflexion of a given sequence of transmission lines
    with the given_z_steps profile and equal length of _phi_steps degrees
    """
    n_step = len(_z_steps)

    z_tot = _z_steps[-1:]
    for i in range(n_step):
        z_0 = _z_steps[n_step-i-1]
        z_tot = z_0*(z_tot+1j*z_0*np.tan(_phi_step))/(z_0+1j*z_tot*np.tan(_phi_step))
    return gamma(_z_steps[0], z_tot)


@njit(cache=True)
def transmission_coef(_z_steps, _phi_step):
    return np.sqrt(1-reflexion_coef(_z_steps, _phi_step)**2)


@vectorize(cache=True)
def frac_bandwidth(f_min, f_max):
    return 100*np.abs(f_max-f_min)/np.sqrt(f_max*f_min)


@njit(cache=True)
def friis(f, gain):
    """

    """
    m = gain.shape[0]
    n = f.shape[0]
    if m != n-1:
        raise ValueError("gain should have 1 item less than noise factor f")
    g_tot = 1
    f_lin = lin(f)
    res = f_lin[0]
    for i in range(m):
        g_tot *= lin(gain[i])
        res += (f_lin[i+1]-1)/g_tot
    return dB(res)
