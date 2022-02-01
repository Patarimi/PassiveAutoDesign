# -*- coding: utf-8 -*-
"""

"""
import numpy as np
import yaml
from matplotlib.ticker import EngFormatter
from scipy.optimize import minimize, OptimizeResult
from ..components.transformer import Transformer
from ..special import std_dev, quality_f


EngFor = EngFormatter()


class Balun:
    """
    Create a balun object
    """

    def __init__(self, _fc=1e9, _z_source=50, _z_load=50, _k=0.9):
        self.f_c = _fc
        self.z_src = _z_source
        self.z_ld = _z_load
        self.k = _k
        self.is_symmetrical = False

    def design(self):
        """
        design an impedance transformer
        with the targeted specifications (f_targ, zl_targ, zs_targ, k)
        return the two ideal transformers solution
        """
        k = self.k
        alpha = (1 - k ** 2) / k
        q_s = -quality_f(self.z_src)
        q_l = -quality_f(self.z_ld)
        # assuming perfect inductor for first calculation
        r_l1 = 0
        r_l2 = 0
        q_s_prime = q_s * np.real(self.z_src) / (np.real(self.z_src) + r_l1)
        q_l_prime = q_l * np.real(self.z_ld) / (np.real(self.z_ld) + r_l2)
        b_coeff = 2 * alpha * q_s_prime + q_s_prime + q_l_prime
        discr = b_coeff ** 2 - 4 * alpha * (alpha + 1) * (1 + q_s_prime ** 2)
        if discr < 0:
            raise ValueError(
                "Negative value in square root,\
try to increase the coupling factor or the load quality factor\
or try to lower the source quality factor"
            )
        z_sol = np.array(
            (
                (b_coeff + np.sqrt(discr)) / (2 * (alpha + 1)),
                (b_coeff - np.sqrt(discr)) / (2 * (alpha + 1)),
            )
        )
        qxl1 = z_sol / (1 - k ** 2)
        qxl2 = z_sol * (1 + q_l_prime ** 2) / (alpha * (1 + (q_s_prime - z_sol) ** 2))
        l_sol1 = qxl1 * np.real(self.z_src) / (2 * np.pi * self.f_c)
        l_sol2 = qxl2 * np.real(self.z_ld) / (2 * np.pi * self.f_c)
        return l_sol1, l_sol2

    def __enforce_symmetrical(self, _q_val, _of_load=True):
        """
        return the 'distance' to a symmetrical balun (ie. primary = secondary)
        if _of_load, altering the load impedance
        else altering the source impedance
        """
        k = self.k
        alpha = (1 - k ** 2) / k
        if _of_load:
            q_s = -quality_f(self.z_src)
            q_l = _q_val
        else:
            q_s = _q_val
            q_l = -quality_f(self.z_ld)
        b_coeff = 2 * alpha * q_s + q_s + q_l
        discr = b_coeff ** 2 - 4 * alpha * (alpha + 1) * (1 + q_s ** 2)
        if discr < 0:
            return np.inf
        z_sol = np.array(
            (
                (b_coeff + np.sqrt(discr)) / (2 * (alpha + 1)),
                (b_coeff - np.sqrt(discr)) / (2 * (alpha + 1)),
            )
        )
        qxl1 = z_sol / (1 - k ** 2)
        qxl2 = z_sol * (1 + q_l ** 2) / (alpha * (1 + (q_s - z_sol) ** 2))
        qxl_ratio = np.real(self.z_ld) / np.real(self.z_src)
        return np.abs(np.min(qxl1 / qxl2) - qxl_ratio)

    def enforce_symmetrical(self, side="load", _verbose=False):
        """
        alter the value of the load impedance (if side="load") or the source impedance
        in order to realize a symmetrical balun (ie. primary = secondary)
        """
        if side == "load":
            old_z = self.z_ld
            _through_load = True
        else:
            old_z = self.z_src
            _through_load = False
        res = minimize(
            self.__enforce_symmetrical,
            -quality_f(old_z),
            args=_through_load,
            method="Nelder-Mead",
        )
        new_z = np.real(old_z) * (1 - 1j * res.x[0])
        if _verbose:
            print(f"old z_ld: ${complex(old_z):5.2f}")
            print(f"new z_ld: ${complex(new_z):5.2f}")
        if _through_load:
            self.z_ld = complex(new_z)
        else:
            self.z_src = complex(new_z)
        self.is_symmetrical = True

    def print(self):
        message = f"target : f={EngFor(self.f_c)}Hz"
        return message
