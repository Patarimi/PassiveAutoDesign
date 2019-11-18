# -*- coding: utf-8 -*-
"""
Define constants and function dedicated to RF-conception
"""
import numpy as np

# Constants
u0 = 4*np.pi*1e-7 #H/m
c0 = 299792458 #m/s
eps0 = 8.8541878128e-12 #F/m
eta0 = np.sqrt(u0/eps0) #Ohm
NmtodBcm = 8.686/100

# Other functions
def std_dev(mesured, targeted):
    """
        return the standard deviation bewteen an array_like of results and their references.
    """
    m_l = mesured.size
    if m_l == targeted.size:
        std_d = np.zeros((m_l, 1))
        for t_i in range(m_l):
            std_d[t_i] = np.abs((mesured[t_i]-targeted[t_i])/(mesured[t_i]+targeted[t_i]))**2
        return np.sqrt(np.sum(std_d))
    raise ValueError("mesured and targeted must be the same size")

def dB(cmplx):
    """
        Return the decibel value of the given imaginary number.
    """
    return 20*np.log10(np.abs(cmplx))

def ihsr(_s31, _s21):
    """
        Return the IHSR (Ideal Hybrid Splitting Ratio) for the given gains
    """
    return -np.min((dB(_s21-1j*_s31), dB(_s21+1j*_s31)))

def qual_f(_z):
    """
    return the quality factor of a components
    """
    return np.imag(_z)/np.real(_z)
