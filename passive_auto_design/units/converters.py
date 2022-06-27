import numpy as np
from typing import List
from .noise import PhaseNoise
from .time import Frequency, Time
from .physical_dimension import PhysicalDimension


def int_phase_noise(
    pn_db: PhaseNoise,
    freq: Frequency,
    f_min: Frequency = None,
    f_max: Frequency = None,
):
    """

    Parameters
    ----------
    pn_db : PhaseNoise
        List of the phase noise in dBc/Hz
    freq : Frequency
        List of the corresponding frequency (in Hz)
    f_min, f_max : Frequency
        if not None, calculation is done from f_min to f_max (with interpolation)


    Returns
    -------
    float
        integrated phase noise of the piece wise phase noise curve (in radian)

    """
    pn_shape = len(pn_db.value)
    f_shape = len(freq.value)
    if pn_shape != f_shape:
        raise ValueError(f"Expected identical shape, got {pn_shape} and {f_shape}")
    ipn = PhysicalDimension(value=(0.0,), scale="lin", unit="")
    for i in range(pn_shape - 1):
        if f_min is not None and f_min.value > freq[i + 1].value:
            # skipping all part bellow f_min
            continue
        if f_min is not None and f_min > freq[i]:
            f1 = f_min if type(f_min) is Frequency else Frequency(value=f_min)
            pn1_db = __pn_interpol(pn_db[i : i + 2], freq[i : i + 2], f_min)
        else:
            f1 = freq[i]
            pn1_db = pn_db[i]

        if f_max is not None and freq[i] > f_max:
            continue
        if f_max is not None and freq[i + 1] < f_max:
            f2 = f_max if type(f_max) is Frequency else Frequency(value=f_max)
            pn2_db = __pn_interpol(pn_db[i : i + 2], freq[i : i + 2], f_max)
        else:
            f2 = freq[i + 1]
            pn2_db = pn_db[i + 1]
        A = (pn1_db - pn2_db) / (f1.dB() - f2.dB())
        ipn += (f2 * pn2_db.lin() - f1 * pn1_db.lin()) / (A + 1)
    return ipn


def __pn_interpol(pn_db: PhaseNoise, freq: Frequency, f_int: Frequency):
    """
    interpolator for phase noise
    """
    a = (pn_db[1] - pn_db[0]) / (freq[1].dB() - freq[0].dB())
    b = pn_db[1] - a * freq[1].dB()
    return b + a * f_int.dB()


def to_jitter(ipn, f0):
    """

    Parameters
    ----------
    ipn : float
        integrated phase noise of a system
    f0 : float
        central frequency of the system

    Returns
    -------
    float
        equivalent jitter in seconds

    """
    return Time(value=np.sqrt(2 * ipn.value) / (2 * np.pi * f0))
