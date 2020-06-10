# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 08:13:38 2020

@author: mpoterea
"""

import abc
from scipy.optimize import minimize_scalar
from passive_auto_design.special import u0, eps0

class LumpedElement(metaclass=abc.ABCMeta):
    """
        class of standard lumped element, to be inhereted by all lumped elements
    """
    def __init__(self):
        self._par = {}
        self.ref = None
    
    @property
    def par(self):
        return self._par
    
    @par.setter
    def par(self, key_pair):
        self._par.update(key_pair)
    
    def set_x_with_y(self, x_key, y_key, y_value):
        """
            set the value of the X_key for a Y_value of the Y_key
        """
        self.par = {y_key: y_value}
        minimize_scalar(self.cost, args=(x_key))

    def cost(self, x_value, x_key):
        self.par = {x_key: x_value}
        return abs(self.calc_ref_value() - self.par[self.ref])
    
    @abc.abstractmethod
    def calc_ref_value(self):
        raise NotImplementedError

class Resistor(LumpedElement):
    """
        class describing a resistor behavior
    """
    def __init__(self, section = 1e-3, length = 1, rho = 1e-15):
        LumpedElement.__init__(self)
        self.par = {'section': section,
                    'length': length,
                    'rho': rho,
                    }
        self.ref = "res"
        self.par.update({"res": self.calc_ref_value()})
    def calc_ref_value(self):
        return self.par["rho"]*self.par["length"]/self.par["section"]

class Capacitor(LumpedElement):
    """
        class describing a capacitor behavior
    """
    def __init__(self, area=1e-6, dist=1e-3, eps_r=1):
        LumpedElement.__init__(self)
        self.ref = "cap"
        self.par = {"eps_r": eps_r,
                    "area": area,
                    "dist": dist,
                    }
        self.par.update({"cap": self.calc_ref_value()})
    def calc_ref_value(self):
        return eps0*self.par["eps_r"]*self.par["area"]/self.par["dist"]

class Inductor(LumpedElement):
    """
        class describing a inductor behavior
    """
    def __init__(self, d_i=100e-6, n_turn=1, width=3e-6, gap=1e-6):
        LumpedElement.__init__(self)
        self.ref = "ind"
        self.par = {"d_i": d_i,
                    "n_turn": n_turn,
                    "width": width,
                    "gap": gap,
                    "k_1": 1.265,
                    "k_2": 2.093,
                    }
        self.par.update({"ind": self.calc_ref_value()})
    def calc_ref_value(self):
        outer_diam = self.par['d_i']+2*self.par['n_turn']*self.par['width']\
                +2*(self.par['n_turn']-1)*self.par['gap']
        try:
            self.par["d_o"] = outer_diam
        except KeyError:
            self.par.update({"d_o": outer_diam})
        rho = (self.par['d_i']+outer_diam)/2
        density = (outer_diam-self.par['d_i'])/(outer_diam+self.par['d_i'])
        return self.par['k_1']*u0*self.par['n_turn']**2*rho/(1+self.par['k_2']*density)

class Mutual(LumpedElement):
    """
        class describing a mutual inductor behavior
    """
    def __init__(self, ind1, ind2):
        self.ref = "k"
        LumpedElement.__init__(self)
        self.ind1 = ind1
        self.ind2 = ind2
        self.par = {"cpl_eq": 1}
        self.par.update({"k": self.__calc_ref_value()})
    def calc_ref_value(self):
        cpl = self.par["cpl_eq"]
        return cpl*(min(self.ind1.par["d_o"], self.ind2.par["d_o"])-\
                    max(self.ind1.par["d_i"], self.ind2.par["d_i"]))
