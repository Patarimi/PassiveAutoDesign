# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 16:10:47 2019

@author: Patarimi
"""
import numpy as np
from scipy.optimize import minimize_scalar
from ..special import u0, eps0, c0, Nm_to_dBcm, eta0


class SIW:
    """
        Create an SIW object with a given geometry
    """
    def __init__(self, _metal, _diel, _height):
        self.metal = _metal
        self.diel = _diel
        self.height = _height
        self.width = 0
        self.f_c = 0
        self.eta = np.sqrt(u0/(self.diel.epsilon*eps0))
    def set_width(self, _width):
        """
            set the width of the wave-guide and update the cut-off frequency
        """
        self.width = _width
        self.f_c = self.calc_fc(1, 0)
    def set_fc(self, _fc):
        """
            set the cut-off frequency of the wave-guide and update the width
        """
        self.f_c = _fc
        self.width = c0/(_fc*2*np.sqrt(self.diel.epsilon))
    def calc_fc(self, _m, _n):
        """
            return the value of the cut-off frequency of the TEM mode _m, _n
        """
        eps = self.diel.epsilon
        return c0*np.sqrt((_m*np.pi/self.width)**2+(_n*np.pi/self.height)**2)/(2*np.pi*np.sqrt(eps))
    def calc_k(self, _freq):
        """
            convert the freq in pulsation in the given substrate
        """
        return np.sqrt(self.diel.epsilon)*2*np.pi*_freq/c0
    def calc_lambda(self, _f):
        """
        return the wavelength inside the waveguide at the given frequency _f
        """
        return c0/(_f*np.sqrt(1-(self.f_c/_f)**2))
    def calc_beta(self, _freq):
        """
            return the value of the velocity (beta)
        """
        return np.sqrt(self.calc_k(_freq)**2-(np.pi/self.width)**2)
    def calc_a_d(self, _freq):
        """
            return the value of the dielectric loss in dB/m at the frequency freq (array-like)
        """
        k = self.calc_k(_freq)
        tan_d = self.diel.tand
        beta = self.calc_beta(_freq)
        return Nm_to_dBcm * k ** 2 * tan_d / (2 * beta)

    def calc_a_c(self, _freq):
        """
            return the value of the conductor loss in dB/m at the frequency freq (array-like)
        """
        r_s = np.sqrt(2*np.pi*_freq*u0/(2*self.metal.rho))
        eta = self.eta
        k = self.calc_k(_freq)
        beta = self.calc_beta(_freq)
        height = self.height
        width = self.width
        return Nm_to_dBcm * r_s * (2 * height * np.pi ** 2 + width ** 3 * k ** 2) /\
            ((width ** 3) * height * beta * k * eta)

    def calc_ksr(self, _freq):
        """
            return the coefficient of the added conductor loss introduce by surface rougthness
        """
        rho = self.metal.rho
        skin_d = 1/np.sqrt(rho*np.pi*_freq*u0)
        rougth = self.diel.rougthness
        if rougth <= 0:
            raise ValueError("Rougthness must be above zero. \
Value can be set through /self.diel.rougthness/")
        return 2*np.arctan(1.4*(rougth/skin_d)**2)/np.pi
    def calc_pphc(self, _freq, _e_0):
        """
            return the peak power handling capability in watt
            at the _freq frequency (in GHz) and for a maximum electric field _e_0 (in V/m)
        """
        width = self.width
        if width <= 0:
            raise ValueError("Width must be above zero. \
Value can be set using set_width() or set_f_c()")
        height = self.height
        f_c = self.f_c
        eps = self.diel.epsilon
        return 0.25*np.sqrt(eps)*np.sqrt(1-(f_c/_freq)**2)*width*height*_e_0**2/eta0
    def print_info(self):
        """
            output the size and the upper mode cut-off frequency
        """
        fc_01 = self.calc_fc(0, 1)
        print(f'Width: {self.width*1e3:.2f} mm\tfc01: {fc_01*1e-9:.2f} GHz')
    def get_sparam(self, _freq, _length):
        """
            return the 4 scattering parameters of a wave-guide section
            of the given length for the given frequency
        """
        s11 = 0
        alpha = self.calc_a_c(_freq)+(1+self.calc_ksr(_freq))*self.calc_a_d(_freq)
        s21 = (1-s11)*np.exp(-(alpha+1j*self.calc_beta(_freq))*_length)
        return s21
class AF_SIW(SIW):
    """
        Create an AF-SIW object with a given geometry
    """
    def __init__(self, _metal, _diel, _height, _slab):
        SIW.__init__(self, _metal, _diel, _height)
        if _slab <= 0:
            raise ValueError("Slab must be above zero. Please use SIW class")
        self.slab = _slab
    def set_fc(self, _fc):
        """
            set the cut-off frequency of the wave-guide and update the width
        """
        self.f_c = _fc
        slb = self.slab
        sqr_eps = np.sqrt(self.diel.epsilon)
        tan = np.tan(2*slb*np.pi*_fc/c0)*sqr_eps
        self.width = 2*slb+np.arctan(1/tan)*c0/(sqr_eps*np.pi*_fc)
    def calc_fc(self, _m, _n=0):
        """
            return the value of the cut-off frequency of the TEM mode _m, _n
        """
        if _n > 0:
            raise ValueError("Value of _n greater than 0 are not supported")
        if _m%2==1:
            res = minimize_scalar(self.__odd_fc)
        else:
            if self.f_c <= 0:
                self.f_c = self.calc_fc(1, 0)
            res = minimize_scalar(self.__even_fc, bounds=(1.5*self.f_c, 5*self.f_c), method='bounded')
        return res.x
    def __odd_fc(self, _fc):
        if _fc <= 0: #frequency must be stricly positive
            return 1e12
        slb = self.slab
        wth = self.width
        sqr_eps = np.sqrt(self.diel.epsilon)
        return np.abs(sqr_eps*np.tan(2*np.pi*_fc*slb/c0)-1/np.tan(sqr_eps*np.pi*_fc*(wth-2*slb)/c0))
    def __even_fc(self, _fc):
        slb = self.slab
        wth = self.width
        sqr_eps = np.sqrt(self.diel.epsilon)
        return np.abs(sqr_eps*np.tan(2*np.pi*_fc*slb/c0)+np.tan(sqr_eps*np.pi*_fc*(wth-2*slb)/c0))
    def calc_a_d(self, _freq):
        return 0
    def calc_ksr(self, _freq):
        rho = self.metal.rho
        skin_d = 1/np.sqrt(rho*np.pi*_freq*u0)
        rougth = self.metal.rougthness
        return 2*np.arctan(1.4*(rougth/skin_d)**2)/np.pi
    def print_info(self):
        """
            output the size and the upper mode cut-off frequency
        """
        fc_20 = self.calc_fc(2, 0)
        print(f'Width: {self.width*1e3:.2f} mm\tfc20: {fc_20*1e-9:.2f} GHz')
