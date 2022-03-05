# -*- coding: utf-8 -*-
"""
Define constants and function dedicated to RF-conception
"""
import numpy as np

# Constants
u0 = 4 * np.pi * 1e-7  # H/m
c0 = 299792458  # m/s
eps0 = 8.8541878128e-12  # F/m
eta0 = np.sqrt(u0 / eps0)  # Ohm
Nm_to_dBcm = 8.686 / 100


# Other functions
def gamma(_z_load: float, _z0: float = 50):
    return (_z0 - _z_load) / (_z0 + _z_load)


def std_dev(measured, targeted):
    """
    return the standard deviation between an array_like of results and their references.
    """
    tmp = np.array(np.abs(gamma(measured, targeted)) ** 2)
    return np.sqrt(np.sum(tmp))


def dB(c):
    """
    Return the decibel value of the given imaginary number.
    """
    if c == 0:
        return -np.inf
    return 10 * np.log10(np.abs(c))


def lin(d):
    """
    return the linear magnitude of the given magnitude in decibel
    """
    return 10 ** (d / 10)


def ihsr(_s31, _s21):
    """
    Return the IHSR (Ideal Hybrid Splitting Ratio) for the given gains
    """
    if _s21 == 1j * _s31 or _s21 == -1j * _s31:
        return np.inf
    ihsr_log = dB((_s21 - 1j * _s31) / (_s21 + 1j * _s31))
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


def friis(f, gain):
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

    m = gain.shape[0]
    n = f.shape[0]
    if m != n - 1:
        raise ValueError("gain should have 1 item less than noise factor f")
    g_tot = 1
    f_lin = lin(f)
    res = f_lin[0]
    for i in range(m):
        g_tot *= lin(gain[i])
        res += (f_lin[i + 1] - 1) / g_tot
    return dB(res)


def int_phase_noise(pn_db, freq, f_min=None, f_max=None):
    """

    Parameters
    ----------
    pn_db : np.Array
        List of the phase noise in dBc/Hz
    freq : np.Array
        List of the corresponding frequency (in Hz)
    f_min, f_max : float
        if not None, calculation is done from f_min to f_max (with interpolation)


    Returns
    -------
    float
        integrated phase noise of the piece wise phase noise curve (in radian)

    """
    pn_shape = pn_db.size
    f_shape = freq.size
    if pn_shape != f_shape:
        raise ValueError(f"Expected identical shape, got {pn_shape} and {f_shape}")
    ipn = 0
    for i in range(pn_shape - 1):
        if f_min is not None and f_min > freq[i + 1]:
            # skipping all part bellow f_min
            continue
        if f_min is not None and f_min > freq[i]:
            f1 = f_min
            pn1_db = __pn_interpol(pn_db[i : i + 2], freq[i : i + 2], f_min)
        else:
            f1 = freq[i]
            pn1_db = pn_db[i]

        if f_max is not None and freq[i] > f_max:
            continue
        if f_max is not None and freq[i + 1] < f_max:
            f2 = f_max
            pn2_db = __pn_interpol(pn_db[i : i + 2], freq[i : i + 2], f_max)
        else:
            f2 = freq[i + 1]
            pn2_db = pn_db[i + 1]
        A = (pn1_db - pn2_db) / dB(f1 / f2)
        ipn += (f2 * lin(pn2_db) - f1 * lin(pn1_db)) / (A + 1)
    return ipn


def __pn_interpol(pn_db, freq, f_int):
    """
    interpolator for phase noise
    """
    a = (pn_db[1] - pn_db[0]) / (10 * np.log10(freq[1] / freq[0]))
    b = pn_db[1] - a * 10 * np.log10(freq[1])
    return b + a * 10 * np.log10(f_int)


def ipn_to_jitter(ipn, f0):
    """

    Parameters
    ----------
    ipn : float
        integrated phase noise of an system
    f0 : float
        central frequency of the system

    Returns
    -------
    float
        equivalent jitter in seconds

    """
    return np.sqrt(2 * ipn) / (2 * np.pi * f0)
