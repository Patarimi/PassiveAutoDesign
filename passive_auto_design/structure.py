# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 16:10:47 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import minimize_scalar

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
class Transformer:
    """
        Create a transformator object with the specified geometry _primary & _secondary
        (which are dict defined as :
            {'di':_di,'n_turn':_n_turn, 'width':_width, 'gap':_gap, 'height':height})
        and calculate the associated electrical model
    """
    def __init__(self, _primary, _secondary, _eps_r=4.2, _dist=9, _dist_sub=1e9, _freq=1e9):
        self.prim = _primary
        self.second = _secondary
        self.dist = _dist
        self.dist_sub = _dist_sub
        self.freq = _freq
        self.eps_r = _eps_r
        self.model = {'lp':self.l_geo(True),
                      'rp':self.r_geo(True, 17e-9),
                      'ls':self.l_geo(False),
                      'rs':self.r_geo(False, 17e-9),
                      'cg':self.cc_geo(False),
                      'cm':self.cc_geo(True),
                      }
    def set_primary(self, _primary):
        """
            modify the top inductor and refresh the related model parameters
        """
        self.prim = _primary
        self.model['lp'] = self.l_geo(True)
        self.model['rp'] = self.r_geo(True, 17e-9)
        self.model['cg'] = self.cc_geo(False)
        self.model['cm'] = self.cc_geo(True)
    def set_secondary(self, _secondary):
        """
            modify the bottom inductor and refresh the related model parameters
        """
        self.second = _secondary
        self.model['ls'] = self.l_geo(False)
        self.model['rs'] = self.r_geo(False, 17e-9)
        self.model['cg'] = self.cc_geo(False)
        self.model['cm'] = self.cc_geo(True)
    def l_geo(self, _of_primary=True):
        """
            return the value of the distributed inductance of the described transformer
            if _of_primary, return the value of the top inductor
            else, return the value of the bottom inductor
        """
        k_1 = 1.265   #constante1 empirique pour inductance
        k_2 = 2.093   #constante2 empirique pour inductance
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        outer_diam = geo['di']+2*geo['n_turn']*geo['width']+2*(geo['n_turn']-1)*geo['gap']
        rho = (geo['di']+outer_diam)/2
        density = (outer_diam-geo['di'])/(outer_diam+geo['di'])
        return k_1*4*np.pi*1e-7*geo['n_turn']**2*rho/(1+k_2*density)
    def cc_geo(self, _mutual=True):
        """
            return the value of the distributed capacitance of the described transformer
            if _mutual, return the capacitance between primary and secondary
            else, return the capacitance to the ground plane
        """
        if _mutual:
            dist = self.dist
        else:
            dist = self.dist_sub
        c_1 = 8.275   #constante1 empirique pour capacité
        c_2 = 5.250   #constante2 empirique pour capacité
        n_t = self.prim['n_turn']
        return self.prim['width']*eps0*self.eps_r*(c_1+c_2*(n_t-1))*self.prim['di']/dist
    def r_geo(self, _of_primary=True, rho=17e-10):
        """
            return the value of the resistance of the described transformer
        """
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        n_t = geo['n_turn']
        height = geo['height']
        l_tot = 8*np.tan(np.pi/8)*n_t*(geo['di']+geo['width']+(n_t-1)*(geo['width']+geo['gap']))
        r_dc = rho*l_tot/(geo['width']*height)
        skin_d = np.sqrt(rho/(u0*self.freq*np.pi))
        r_ac = rho*l_tot/((1+height/geo['width'])*skin_d*(1-np.exp(-height/skin_d)))
        return r_dc + r_ac
    def generate_spice_model(self, k_ind):
        """
            Generate a equivalent circuit of a transformer with the given values
        """
        return f'Transformer Model\n\n\
L1		IN	1	{self.model["lp"]*1e12:.1f}p\n\
R1		1	OUT	{self.model["rp"]*1e3:.1f}m\n\
L2		CPL	2	{self.model["ls"]*1e12:.1f}p\n\
R2		2	ISO	{self.model["rs"]*1e3:.1f}m\n\
K		L1	L2	{k_ind:.3n}\n\
CG1		IN	0	{self.model["cg"]*1e15/4:.1f}f\n\
CG2		OUT	0	{self.model["cg"]*1e15/4:.1f}f\n\
CG3		ISO	0	{self.model["cg"]*1e15/4:.1f}f\n\
CG4		CPL	0	{self.model["cg"]*1e15/4:.1f}f\n\
CM1		IN	CPL	{self.model["cm"]*1e15/2:.1f}f\n\
CM2		ISO	OUT	{self.model["cm"]*1e15/2:.1f}f\n\n'
