# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import yaml
import numpy as np
from scipy.optimize import minimize, minimize_scalar, OptimizeResult
from ..components.transformer import Transformer
from ..special import ihsr


class Coupler:
    """
    Create a coupler object
    """

    def __init__(self, _fc=1e9, _zc=50, modelmapfile=None, bounds=None):
        self.f_c = _fc
        self.z_c = _zc
        if modelmapfile is None:
            modelmapfile = "tests/default.map"
        with open(modelmapfile, "r") as file:
            self.modelmap = yaml.full_load(file)
        width_lim = (
            float(self.modelmap["width"]["min"]),
            float(self.modelmap["width"]["max"]),
        )
        turn_lim = (
            float(self.modelmap["turn"]["min"]),
            float(self.modelmap["turn"]["max"]),
        )
        gap_lim = float(self.modelmap["gap"])
        if bounds is None:
            self.bounds = np.array(
                [
                    width_lim,  # width
                    turn_lim,  # turn number
                    (width_lim[1], 20 * width_lim[1]),  # inner diameter
                    (gap_lim, 1.01 * gap_lim),  # gap
                ]
            )
        else:
            self.bounds = bounds
        geo = {
            "di": 20,
            "n_turn": 2,
            "width": self.bounds[0, 0],
            "gap": self.bounds[3, 0],
        }
        self.transfo = Transformer(geo, geo, _fc, modelmapfile)

    def cost(self, sol):
        """
        return the cost (standard deviation)
        between the proposed solution and the targeted specifications
        """
        geo = {
            "di": sol[2],
            "n_turn": np.round(sol[1]),
            "width": sol[0],
            "gap": sol[3],
        }
        self.transfo.set_primary(geo)
        self.transfo.set_secondary(geo)
        s_p = self.transfo.circuit.s_external[0]
        return np.abs(s_p[0, 0]) + np.max([26.7 - ihsr(s_p[1, 0], s_p[0, 1]), 0])

    def __cost_est_inductance(self, _di):
        self.transfo.prim["di"] = _di
        return np.abs(self.transfo.l_geo() - self.z_c / (2 * np.pi * self.f_c))

    def __cost_est_capacitance(self, _width):
        self.transfo.prim["width"] = _width
        return np.abs(
            self.transfo.cc_geo()
            + self.transfo.cc_geo(False)
            - 1 / (self.z_c * 2 * np.pi * self.f_c)
        )

    def design(self, _maxiter=500):
        """
        design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
        return an optimization results (res)
        """
        # finding the inner diameter that give the correct inductance
        minimize_scalar(self.__cost_est_inductance, bounds=self.bounds[2])
        # finding the path width that give the correct capacitor
        res_int = minimize_scalar(self.__cost_est_capacitance, bounds=self.bounds[0])
        geo = self.transfo.prim
        x_0 = np.array([geo["width"], geo["n_turn"], geo["di"], geo["gap"]])
        if _maxiter == 0:  # just get the first guess
            res = OptimizeResult()
            res.x = x_0
            res.fun = res_int.fun
            res.message = "First Guess"
            return res
        res = minimize(self.cost, x0=x_0)
        return res

    def print(self, res):
        """
        print a summary of the solution (res)
        with a comparison to the boundaries
        """
        sol = res.x * 1e6
        bds = np.array(self.bounds) * 1e6
        print(f"Solution funds with remaining error of: {float(res.fun):.2e}")
        print("Termination message of algorithm: " + str(res.message))
        print("\t\tW (µm)\tn\tdi (µm)\tG (µm)")
        print(
            f"lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}"
        )
        print(
            f"best point  :\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}"
        )
        print(
            f"upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}"
        )
