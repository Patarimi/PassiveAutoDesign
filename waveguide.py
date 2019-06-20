# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 16:10:47 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import minimize_scalar
import warnings

u0 = 4*np.pi*1e-7 #H/m
c0 = 299792458 #m/s
eps0 = 8.8541878128e-12 #F/m
eta0 = np.sqrt(u0/eps0) #Ohm
NmtodBcm = 8.686/100

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
        tand = self.diel.tand
        beta = self.calc_beta(_freq)
        return NmtodBcm*k**2*tand/(2*beta)
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
        return NmtodBcm*r_s*(2*height*np.pi**2+width**3*k**2)/((width**3)*height*beta*k*eta)
    def calc_ksr(self, _freq):
        """
            return the coefficient of the added conductor loss introduce by surface rougthness
        """
        rho = self.metal.rho
        skin_d = 1/np.sqrt(rho*np.pi*_freq*u0)
        rougth = self.diel.rougthness
        return 2*np.arctan(1.4*(rougth/skin_d)**2)/np.pi
    def calc_pphc(self, _freq, _e_0):
        """
            return the peak power handling capability in watt
        """
        width = self.width
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
class AF_SIW(SIW):
    """
        Create an AF-SIW object with a given geometry
    """
    def __init__(self, _metal, _diel, _height, _slab):
        SIW.__init__(self, _metal, _diel, _height)
        if _slab == 0:
            warnings.warn("Slab size null, please use SIW class", RuntimeWarning)
        self.slab = _slab
    def set_width(self, _width):
        """
            set the width of the wave-guide and update the cut-off frequency
        """
        self.width = _width
        self.f_c = self.__even_fc()
    def set_fc(self, _fc):
        """
            set the cut-off frequency of the wave-guide and update the width
        """
        self.f_c = _fc
        slb = self.slab
        sqr_eps = np.sqrt(self.diel.epsilon)
        tan = np.tan(2*slb*np.pi*_fc/c0)*sqr_eps
        self.width = 2*slb+np.arctan(1/tan)*c0/(sqr_eps*np.pi*_fc)
    def __even_fc(self, _fc):
        width = self.slab
        sqr_eps = np.sqrt(self.diel.epsilon)
        return sqr_eps*np.tan(-2*np.pi*_fc*width/c0)+np.tan(-sqr_eps*2*np.pi*_fc*width/c0)
    def __odd_fc(self, _fc):
        width = self.slab
        sqr_eps = np.sqrt(self.diel.epsilon)
        return sqr_eps*np.tan(-2*np.pi*_fc*width/c0)+np.tan(-sqr_eps*2*np.pi*_fc*width/c0)
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
        sol = minimize_scalar(self.__odd_fc)
        print(f'Width: {self.width*1e3:.2f} mm\tfc01: {sol.x*1e-9:.2f} GHz')
