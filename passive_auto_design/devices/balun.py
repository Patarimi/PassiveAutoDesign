# -*- coding: utf-8 -*-
"""
    Class to calculate the inductors values of an impedance transformer.
"""
import numpy as np
from scipy.optimize import minimize
from ..special import quality_f
from ..unit import Frequency


class Balun:
    """
    Create a balun object
    """

    def __init__(self, _fc=1e9, _z_source=50, _z_load=50, _k=0.9):
        self.f_c = _fc
        self.z_src = _z_source
        self.z_ld = _z_load
        self.k = _k

    def design(self, XL_add=(0.0, 0.0), XS_add=(0.0, 0.0)):
        """
        design an impedance transformer
        with the targeted specifications (f_targ, zl_targ, zs_targ, k)
        return the two ideal transformers solution
        """
        k = self.k
        alpha = (1 - k ** 2) / k ** 2
        q_s = -quality_f(self.z_src + 1j * np.array(XS_add))
        q_l = -quality_f(self.z_ld + 1j * np.array(XL_add))
        # assuming perfect inductor for first calculation
        r_l1, r_l2 = 0.0, 0.0
        q_s_prime = q_s * np.real(self.z_src) / (np.real(self.z_src) + r_l1)
        q_l_prime = q_l * np.real(self.z_ld) / (np.real(self.z_ld) + r_l2)
        b_coeff = 2 * alpha * q_s_prime + q_s_prime + q_l_prime
        discr = b_coeff ** 2 - 4 * alpha * (alpha + 1) * (1 + q_s_prime ** 2)
        z_sol = np.array(
            (
                (b_coeff[0] + np.sqrt(discr[0])) / (2 * (alpha + 1)),
                (b_coeff[1] - np.sqrt(discr[1])) / (2 * (alpha + 1)),
            )
        )
        qxl1 = z_sol / (1 - k ** 2)
        qxl2 = z_sol * (1 + q_l_prime ** 2) / (alpha * (1 + (q_s_prime - z_sol) ** 2))
        l_sol1 = qxl1 * np.real(self.z_src) / (2 * np.pi * self.f_c)
        l_sol2 = qxl2 * np.real(self.z_ld) / (2 * np.pi * self.f_c)
        return l_sol1, l_sol2

    def __enforce_symmetrical(self, _q_val, _of_load=True, sol=0):
        """
        return the 'distance' to a symmetrical balun (ie. primary = secondary)
        if _of_load, altering the load impedance
        else altering the source impedance
        """
        k = self.k
        alpha = (1 - k ** 2) / k ** 2
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
        return np.abs(qxl1[sol] / qxl2[sol] - qxl_ratio)

    def enforce_symmetrical(self, side="load", _verbose=False):
        """
        return the reactance to be added to the load (if side="load") or the source impedance
        in order to realize a symmetrical balun (ie. primary = secondary)
        the two solution match the two solutions of the design
        """
        if side == "load":
            old_z = self.z_ld
            _through_load = True
        else:
            old_z = self.z_src
            _through_load = False
        res0 = minimize(
            self.__enforce_symmetrical,
            -quality_f(old_z),
            args=(_through_load, 0),
            method="Nelder-Mead",
        )
        res1 = minimize(
            self.__enforce_symmetrical,
            -quality_f(old_z),
            args=(_through_load, 1),
            method="Nelder-Mead",
        )
        delta_X = (
            -np.real(old_z) * res0.x[0] - np.imag(old_z),
            -np.real(old_z) * res1.x[0] - np.imag(old_z),
        )
        if _verbose:
            print(f"X_{side} must be change by {delta_X[0]:5.2f} or {delta_X[1]:5.2f}")
        return delta_X

    def print(self):
        message = f"target : f={Frequency(self.f_c)}"
        return message
