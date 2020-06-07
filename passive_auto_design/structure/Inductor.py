# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 08:13:38 2020

@author: mpoterea
"""

from scipy.optimize import minimize_scalar
from passive_auto_design.special import u0

class inductor:
    def __init__(self, d_i=100e-6, n_turn=1, width=3e-6, gap=1e-6):
        self.par = {"d_i": d_i,
                    "n_turn": n_turn,
                    "width": width,
                    "gap": gap,
                    "k_1": 1.265,
                    "k_2": 2.093,
                    }
        self.par.update({"ind": self.__ind_value()})
    
    def set_X_with_Y(self, X_key, Y_key, Y_value):
        """
            set the value of the X_key for a Y_value of the Y_key
        """
        self.par[Y_key] = Y_value
        minimize_scalar(self.__cost, args=(X_key))
        
    def __cost(self, X_value, X_key):
        self.par[X_key] = X_value
        return abs(self.__ind_value() - self.par["ind"])
    
    def __ind_value(self):
        outer_diam = self.par['d_i']\
            +2*self.par['n_turn']*self.par['width']\
                +2*(self.par['n_turn']-1)*self.par['gap']
        rho = (self.par['d_i']+outer_diam)/2
        density = (outer_diam-self.par['d_i'])/(outer_diam+self.par['d_i'])
        return self.par['k_1']*u0*self.par['n_turn']**2*rho/(1+self.par['k_2']*density)