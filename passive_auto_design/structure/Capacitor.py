# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 18:31:45 2020

@author: mpoterea
"""
from scipy.optimize import minimize_scalar
from passive_auto_design.special import eps0

class capacitor:
    def __init__(self, area=1e-6, dist=1e-3, eps_r=1):
        self.par = {"eps_r": eps_r,
                    "area": area,
                    "dist": dist,
                    }
        self.par.update({"cap": self.__cap_value()})
    
    def set_X_with_Y(self, X_key, Y_key, Y_value):
        """
            set the value of the X_key for a Y_value of the Y_key
        """
        self.par[Y_key] = Y_value
        minimize_scalar(self.__cost, args=(X_key))
        
    def __cost(self, X_value, X_key):
        self.par[X_key] = X_value
        return abs(self.__cap_value() - self.par["cap"])
    
    def __cap_value(self):
        return eps0*self.par["eps_r"]*self.par["area"]/self.par["dist"]
