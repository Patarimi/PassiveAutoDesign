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

    def set_x_with_y(self, x_key, y_key, y_value):
        """
        set the value of the X_key for a Y_value of the Y_key
        """
        minimize_scalar(self.__cost, args=(x_key, y_key, y_value))

    @functools.lru_cache()
    def __cost(self, x_value, x_key, y_key, y_value):
        self.par = {x_key: x_value}
        if isinstance(y_value, float):
            self.par = {y_key: y_value}
            return abs(self.calc_ref_value() - self.par[self.ref])
        err = 0
        for y_val in y_value:
            self.par = {y_key: y_val}
            err += abs(self.calc_ref_value() - self.par[self.ref])
        return err

    @abc.abstractmethod
    def calc_ref_value(self):
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
        return self.par["rho"] * self.par["length"] / self.par["section"]


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

    def __init__(self, d_i=100e-6, n_turn=1, width=3e-6, gap=1e-6):
        LumpedElement.__init__(self)
        self.ref = "ind"
        self.par = {
            "d_i": d_i,
            "n_turn": n_turn,
            "width": width,
            "gap": gap,
            "k_1": 1.265,
            "k_2": 2.093,
        }
        self.par.update({"ind": self.calc_ref_value()})

    def __str__(self):
        return Ind(self.par["ind"])

    def calc_ref_value(self):
        outer_diam = (
            self.par["d_i"]
            + 2 * self.par["n_turn"] * self.par["width"]
            + 2 * (self.par["n_turn"] - 1) * self.par["gap"]
        )
        self.par.update({"d_o": outer_diam})
        rho = (self.par["d_i"] + outer_diam) / 2
        density = (outer_diam - self.par["d_i"]) / (outer_diam + self.par["d_i"])
        return (
            self.par["k_1"]
            * u0
            * self.par["n_turn"] ** 2
            * rho
            / (1 + self.par["k_2"] * density)
        )


Mut = EngFormatter()


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
        self.par.update({"k": self.calc_ref_value()})

    def __str__(self):
        return Mut(self.par["k"])

    def calc_ref_value(self):
        cpl = self.par["cpl_eq"]
        return cpl * (
            min(self.ind1.par["d_o"], self.ind2.par["d_o"])
            - max(self.ind1.par["d_i"], self.ind2.par["d_i"])
        )
