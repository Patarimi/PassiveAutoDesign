# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 16:10:47 2019

@author: Patarimi
"""
import numpy as np
from scipy.optimize import minimize_scalar
from ..special import u0, eps0, c0, Nm_to_dBcm, eta0


class Waveguide:
    """
        Create an SIW object with a given geometry
    """

    def __init__(self, _metal, _diel, _height):
        self.metal = _metal
        self.diel = _diel
        self.width = 0.0
        self.first_cut_off = 0.0
        self.height = _height
        self.eta = np.sqrt(u0 / (self.diel.epsilon * eps0))

    @property
    def width(self) -> float:
        if self.f_c <= 0.0:
            return self._w
        self._w = c0 / (self.f_c * 2 * np.sqrt(self.diel.epsilon))
        return self._w

    @width.setter
    def width(self, _width):
        """
            set the width of the wave-guide and update the cut-off frequency
        """
        self._w = _width

    @property
    def first_cut_off(self):
        self.f_c = self.f_cut_off()
        return self.f_c

    @first_cut_off.setter
    def first_cut_off(self, _fc):
        """
            set the cut-off frequency of the wave-guide and update the width
        """
        self.f_c = _fc

    def f_cut_off(self, _m=1, _n=0):
        """
            return the value of the cut-off frequency of the TEM mode _m, _n
        """
        eps = self.diel.epsilon
        return c0 * np.sqrt((_m * np.pi / self.width) ** 2 + (_n * np.pi / self.height) ** 2) / (
                2 * np.pi * np.sqrt(eps))

    def calc_k(self, _freq):
        """
            convert the freq in pulsation in the given substrate
        """
        return np.sqrt(self.diel.epsilon) * 2 * np.pi * _freq / c0

    def calc_lambda(self, _f):
        """
        return the wavelength inside the waveguide at the given frequency _f
        """
        return c0 / (_f * np.sqrt(1 - (self.f_c / _f) ** 2))

    def calc_beta(self, _freq):
        """
            return the value of the velocity (beta)
        """
        return np.sqrt(self.calc_k(_freq) ** 2 - (np.pi / self.width) ** 2)

    def calc_a_d(self, _freq):
        """
            return the value of the dielectric loss in dB/m at the frequency freq (array-like)
        """
        k = self.calc_k(_freq)
        tan_d = self.diel.tan_d
        beta = self.calc_beta(_freq)
        return Nm_to_dBcm * k ** 2 * tan_d / (2 * beta)

    def calc_a_c(self, _freq):
        """
            return the value of the conductor loss in dB/m at the frequency freq (array-like)
        """
        r_s = np.sqrt(2 * np.pi * _freq * u0 / (2 * self.metal.rho))
        eta = self.eta
        k = self.calc_k(_freq)
        beta = self.calc_beta(_freq)
        height = self.height
        width = self.width
        return Nm_to_dBcm * r_s * (2 * height * np.pi ** 2 + width ** 3 * k ** 2) / \
            ((width ** 3) * height * beta * k * eta)

    def calc_ksr(self, _freq):
        """
            return the coefficient of the added conductor loss introduce by surface roughness
        """
        rho = self.metal.rho
        skin_d = 1 / np.sqrt(rho * np.pi * _freq * u0)
        rough = self.diel.roughness
        if rough <= 0:
            raise ValueError("Roughness must be above zero. \
Value can be set through /self.diel.roughness/")
        return 2 * np.arctan(1.4 * (rough / skin_d) ** 2) / np.pi

    def calc_pphc(self, _freq, _e_0):
        """
            return the peak power handling capability in watt
            at the _freq frequency (in GHz) and for a maximum electric field _e_0 (in V/m)
        """
        width = self.width
        if width <= 0.0:
            raise ValueError("Width must be above zero. \
Value can be set using set_width() or set_f_c()")
        height = self.height
        f_c = self.first_cut_off
        eps = self.diel.epsilon
        return 0.25 * np.sqrt(eps) * np.sqrt(1 - (f_c / _freq) ** 2) * width * height * _e_0 ** 2 / eta0

    def calc_aphc(self, _freq, _t_max, t_amb=295) -> float:
        # using doi.org/10.1109/TADVP.2008.927814
        a = self.width
        alpha = self.calc_a_c(_freq) / Nm_to_dBcm + self.calc_a_d(_freq) / Nm_to_dBcm
        # see page 346 of Heat Transfert, 10th edition
        h_uc = 1.32*((_t_max - t_amb)/a)**0.25
        h_dc = 0.59*((_t_max - t_amb)/a)**0.25
        # see page 461 of Heat Transfert, 10th edition (with A2 >> A1)
        sigma = 5.669*1e-8  # W/m²K^4 Stefan-Boltzmann constant
        epsilon = 0.65      # emissivity of the copper
        h_r = sigma*epsilon*(_t_max**2 + t_amb**2)*(_t_max + t_amb)
        return (h_uc + h_dc + 2*h_r)*a*(_t_max - t_amb)/alpha

    def print_info(self):
        """
            output the size and the upper mode cut-off frequency
        """
        fc_01 = self.f_cut_off(0, 1)
        print(f'Width: {self.width * 1e3:.2f} mm\tfc01: {fc_01 * 1e-9:.2f} GHz')

    def get_sparam(self, _freq, _length):
        """
            return the 4 scattering parameters of a wave-guide section
            of the given length for the given frequency
        """
        s11 = 0
        alpha = self.calc_a_c(_freq) + (1 + self.calc_ksr(_freq)) * self.calc_a_d(_freq)
        s21 = (1 - s11) * np.exp(-(alpha + 1j * self.calc_beta(_freq)) * _length)
        return s21


class AF_SIW(Waveguide):
    """
        Create an AF-SIW object with a given geometry
    """

    def __init__(self, _metal, _diel, _height, _slab):
        self.slab = _slab
        Waveguide.__init__(self, _metal, _diel, _height)
        self.width = 0.0
        self.first_cut_off = 0.0

    @property
    def width(self) -> float:
        if self.f_c > 0:
            slb = self.slab
            sqr_eps = np.sqrt(self.diel.epsilon)
            tan = np.tan(2 * slb * np.pi * self.f_c / c0) * sqr_eps
            self._w = 2 * slb + np.arctan(1 / tan) * c0 / (sqr_eps * np.pi * self.f_c)
        return self._w

    @width.setter
    def width(self, _width):
        """
            set the width of the wave-guide and update the cut-off frequency
        """
        self._w = _width

    @property
    def slab(self) -> float:
        return self._slab

    @slab.setter
    def slab(self, _s: float):
        if _s <= 0:
            raise ValueError("Slab must be above zero. Please use Waveguide class")
        self._slab = _s

    @property
    def first_cut_off(self) -> float:
        if self.width > 0:
            self.f_c = self.f_cut_off(1, 0)
        return self.f_c

    @first_cut_off.setter
    def first_cut_off(self, _fc):
        """
            set the cut-off frequency of the wave-guide and update the width
        """
        self.f_c = _fc

    def f_cut_off(self, _m=1, _n=0) -> float:
        """
            return the value of the cut-off frequency of the TEM mode _m, _n
        """
        if _n > 0:
            raise ValueError("Value of _n greater than 0 are not supported")
        if _m % 2 == 1:
            res = minimize_scalar(self.__odd_fc)
        else:
            f_c = self.f_c
            res = minimize_scalar(self.__even_fc, bounds=(1.5 * f_c, 5 * f_c), method='bounded')
        return res.x

    def __odd_fc(self, _fc):
        if _fc <= 0:  # frequency must be strictly positive
            return 1e12
        slb = self._slab
        wth = self._w
        sqr_eps = np.sqrt(self.diel.epsilon)
        return np.abs(
            sqr_eps * np.tan(2 * np.pi * _fc * slb / c0)
            - 1 / np.tan(sqr_eps * np.pi * _fc * (wth - 2 * slb) / c0))

    def __even_fc(self, _fc):
        slb = self._slab
        wth = self._w
        sqr_eps = np.sqrt(self.diel.epsilon)
        return np.abs(
            sqr_eps * np.tan(2 * np.pi * _fc * slb / c0)
            + np.tan(sqr_eps * np.pi * _fc * (wth - 2 * slb) / c0))

    def calc_a_d(self, _freq):
        return 0

    def calc_ksr(self, _freq):
        rho = self.metal.rho
        skin_d = 1 / np.sqrt(rho * np.pi * _freq * u0)
        rough = self.metal.roughness
        return 2 * np.arctan(1.4 * (rough / skin_d) ** 2) / np.pi

    def print_info(self):
        """
            output the size and the upper mode cut-off frequency
        """
        fc_20 = self.f_cut_off(2, 0)
        print(f'Width: {self.width * 1e3:.2f} mm\tfc20: {fc_20 * 1e-9:.2f} GHz')
