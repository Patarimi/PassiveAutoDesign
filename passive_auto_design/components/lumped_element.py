# -*- coding: utf-8 -*-
"""

"""
import abc
import functools
from scipy.optimize import minimize_scalar
from matplotlib.ticker import EngFormatter
from passive_auto_design.special import u0, eps0


class LumpedElement(metaclass=abc.ABCMeta):
    """
    class of standard lumped element, to be inherited by all lumped elements
    """

    def __init__(self):
        self._par = {}
        self.ref = None

    @property
    def par(self):
        """
        Returns
        -------
        Dictionary
            Parameters of the lumped component.

        """
        return self._par

    @par.setter
    def par(self, key_pair):
        self._par.update(key_pair)

    #TODO enable multiple x_keys
    def set_x_with_y(self, x_key, y_key, y_value):
        """
        set the value of the X_key for a Y_value of the Y_key
        """
        res = minimize_scalar(self.__cost, args=(x_key, y_key, y_value))
        return res.x[0]

    @functools.lru_cache()
    def __cost(self, x_value : float, x_key : str, y_key : str, y_value : float):
        if y_key.find(".") > 0:
            comp, ref = y_key.split(".", 1)
            self.par[comp].par.update({ref: y_value})
        else:
            self.par = {y_key: y_value}
        if x_key.find(".") > 0:
            comp, x_k = x_key.split(".", 1)
            self.par[comp].par.update({x_k: x_value})
            return abs(self.par[comp].calc_ref_value() - self.par[comp].par[self.par[comp].ref])
        self.par = {x_key: x_value}
        return abs(self.calc_ref_value() - self.par[self.ref])

    @abc.abstractmethod
    def calc_ref_value(self, subpart=""):
        """
        Definition of the behavioral equation of the lumped element.
        Returns
        -------
        Value of self.par[self.ref] calculated with the other value in self.par.
        """


Res = EngFormatter(unit=r"$\Omega$")


class Resistor(LumpedElement):
    """
    class describing a resistor behavior
    """

    def __init__(self, section=1e-3, length=1, rho=1e-15):
        LumpedElement.__init__(self)
        self.par = {
            "section": section,
            "length": length,
            "rho": rho,
        }
        self.ref = "res"
        self.par.update({"res": self.calc_ref_value()})

    def __str__(self):
        return Res(self.par["res"])

    def calc_ref_value(self):
        return max([self.par["rho"] * self.par["length"] / self.par["section"], 0.])


Cap = EngFormatter(unit="F")


class Capacitor(LumpedElement):
    """
    class describing a capacitor behavior
    """

    def __init__(self, area=1e-6, dist=1e-3, eps_r=1):
        LumpedElement.__init__(self)
        self.ref = "cap"
        self.par = {
            "eps_r": eps_r,
            "area": area,
            "dist": dist,
        }
        self.par.update({"cap": self.calc_ref_value()})

    def __str__(self):
        return Cap(self.par["cap"])

    def calc_ref_value(self):
        return eps0 * self.par["eps_r"] * self.par["area"] / self.par["dist"]


Ind = EngFormatter(unit="H")


class Inductor(LumpedElement):
    """
    class describing a inductor behavior
    """

    def __init__(self, d_i=100e-6, n_turn=1, width=3e-6, gap=1e-6, k_1=2.25, k_2=3.55):
        LumpedElement.__init__(self)
        self.ref = "ind"
        self.par = {
            "d_i": d_i,
            "n_turn": n_turn,
            "width": width,
            "gap": gap,
            "k_1": k_1,
            "k_2": k_2,
        }
        self.par.update({"ind": self.calc_ref_value()})

    def __str__(self):
        return Ind(self.par["ind"])

    def calc_ref_value(self):
        n = self.par["n_turn"]
        outer_diam = self.par["d_i"] + 2 * n * self.par["width"] + 2 * (n - 1) * self.par["gap"]
        self.par.update({"d_o": outer_diam})
        rho = (self.par["d_i"] + outer_diam) / 2
        density = (outer_diam - self.par["d_i"]) / (outer_diam + self.par["d_i"])
        return self.par["k_1"] * u0 * n ** 2 * rho / (1 + self.par["k_2"] * density)
