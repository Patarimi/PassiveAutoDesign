"""
Define constants and function dedicated to RF-conception
"""
import numpy as np
from .units.physical_dimension import PhysicalDimension


# Other functions
def gamma(_z_load: PhysicalDimension, _z0: PhysicalDimension = 50):
    """
    return the reflexion coefficient of an interface between two impedances.
    """
    v = np.array((_z0 - _z_load) / (_z0 + _z_load))
    return PhysicalDimension(value=v, scale="lin", unit="")


def std_dev(measured, targeted):
    """
    return the standard deviation between an array_like of results and their references.
    """
    tmp = np.array(np.abs(gamma(measured, targeted).value) ** 2)
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


def reflexion_coef(_z_steps: PhysicalDimension, _phi_step: float):
    """
    return the coefficient reflexion of a given sequence of transmission lines
    with the given_z_steps profile and equal length of _phi_steps degrees
    """
    n_step = _z_steps.shape[0]

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
    ref_c = reflexion_coef(_z_steps, _phi_step)
    return PhysicalDimension(value=np.sqrt(1 - ref_c**2), scale="lin", unit="")
