# -*- coding: utf-8 -*-
"""
Define constants and function dedicated to RF-conception
"""
import numpy as np
from passive_auto_design.units.physical_dimension import PhysicalDimension
from passive_auto_design.units.time import Frequency

# Other functions
def gamma(_z_load: float, _z0: float = 50):
    return (_z0 - _z_load) / (_z0 + _z_load)


def std_dev(measured, targeted):
    """
    return the standard deviation between an array_like of results and their references.
    """
    tmp = np.array(np.abs(gamma(measured, targeted)) ** 2)
    return np.sqrt(np.sum(tmp))


def ihsr(_s31, _s21):
    """
    Return the IHSR (Ideal Hybrid Splitting Ratio) for the given gains
    """
    if _s21 == 1j * _s31 or _s21 == -1j * _s31:
        return np.inf
    ihsr_log = 10 * np.log10(np.abs((_s21 - 1j * _s31) / (_s21 + 1j * _s31)))
    return -np.minimum(ihsr_log, -ihsr_log)


def quality_f(_z):
    """
    return the quality factor of a components
    """
    return np.imag(_z) / np.real(_z)


def reflexion_coef(_z_steps, _phi_step):
    """
    return the coefficient reflexion of a given sequence of transmission lines
    with the given_z_steps profile and equal length of _phi_steps degrees
    """
    n_step = len(_z_steps)

    z_tot = _z_steps[-1:]
    for i in range(n_step):
        z_0 = _z_steps[n_step - i - 1]
        z_tot = (
            z_0
            * (z_tot + 1j * z_0 * np.tan(_phi_step))
            / (z_0 + 1j * z_tot * np.tan(_phi_step))
        )
    return gamma(_z_steps[0], z_tot)


def transmission_coef(_z_steps, _phi_step):
    return np.sqrt(1 - reflexion_coef(_z_steps, _phi_step) ** 2)


def frac_bandwidth(f_min, f_max):
    return 100 * np.abs(f_max - f_min) / np.sqrt(f_max * f_min)


def friis(f: Frequency, gain: PhysicalDimension):
    """

    Parameters
    ----------
    f : np.Array
        List of the noise figure (in dB) of each block.
    gain : np.Array
        List of the gain of each block (in dB).


    Returns
    -------
    float
        Total noise figure of the system

    """

    m = gain.shape()[0]
    n = f.shape()[0]
    if m != n - 1:
        raise ValueError("gain should have 1 item less than noise factor f")
    g_tot = PhysicalDimension(
        value=[
            1.0,
        ],
        scale="lin",
        unit="",
    )
    f_lin = f.lin()
    res = f_lin[0]
    for i in range(m):
        g_tot *= gain[i].lin()
        res += (f_lin[i + 1] - 1) / g_tot
    return res.dB()
