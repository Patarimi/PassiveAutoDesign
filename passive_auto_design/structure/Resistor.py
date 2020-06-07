# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 08:03:56 2020

@author: mpoterea
"""

from scipy.optimize import minimize_scalar

class resistor:
    def __init__(self, section=1e-3, length=1, rho=1e-15):
        self.par = {"rho": rho,
                    "section": section,
                    "length": length,
                    }
        self.par.update({"res": self.__res_value()})
    
    def set_X_with_Y(self, X_key, Y_key, Y_value):
        """
            set the value of the X_key for a Y_value of the Y_key
        """
        self.par[Y_key] = Y_value
        minimize_scalar(self.__cost, args=(X_key))
        
    def __cost(self, X_value, X_key):
        self.par[X_key] = X_value
        return abs(self.__res_value() - self.par["res"])
    
    def __res_value(self):
        return self.par["rho"]*self.par["length"]/self.par["section"]