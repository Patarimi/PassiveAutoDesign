# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict
from scipy.optimize import minimize_scalar
from matplotlib.ticker import EngFormatter
from ..units.constants import eps0


class LumpedElement(BaseModel, ABC):
    """
    class of standard lumped element, to be inherited by all lumped elements
    """

    dim: Dict[str, float]
    const: Dict[str, float]
    model: Dict[str, float] = {}

    def __init__(self, dim, const, **data):
        BaseModel.__init__(self, dim=dim, const=const, **data)
        self.model = self.get_model()

    # TODO enable multiple x_keys
    def set_model_with_dim(self, target_model: Dict[str, float], dim_key: str) -> float:
        """
        set the value of the dim_key to achieve the target model
        """
        res = minimize_scalar(self.__cost, args=(dim_key, target_model))
        self.model = self.get_model()
        return res.x

    def __cost(
        self, x_value: float, x_key: str, target_model: Dict[str, float]
    ) -> float:
        if x_key in self.dim:
            self.dim[x_key] = x_value
        if x_key in self.const:
            self.const[x_key] = x_value
        tmp_model = self.get_model()
        cost = 0
        for key in target_model.keys():
            cost += (target_model[key] - tmp_model[key]) ** 2 / (
                target_model[key] + tmp_model[key]
            ) ** 2
        return cost

    @abstractmethod
    def get_model(self):
        """
        Definition of the behavioral equation of the lumped element.
        Returns
        -------
        Dict[str, float]: list of the electrical parameter of the lumped element model
        """


Res = EngFormatter(unit=r"$\Omega$")


class Resistor(LumpedElement):
    """
    class describing a resistor behavior
    """

    def __init__(self, section=1e-3, length=1, rho=1e-15):
        param = {"section": section, "length": length}
        const = {"rho": rho}
        LumpedElement.__init__(self, dim=param, const=const)

    def __str__(self):
        return Res(self.model["res"])

    def get_model(self):
        return {
            "res": max(
                [self.const["rho"] * self.dim["length"] / self.dim["section"], 0.0]
            )
        }


Cap = EngFormatter(unit="F")


class Capacitor(LumpedElement):
    """
    class describing a capacitor behavior
    - dimension:
        - area: area of plate
        - dist: distance between plates
    - constant:
        - eps_r: relative permittivity of isolator
    - behavioral:
        - cap: capacitor
    """

    def __init__(self, area=1e-6, dist=1e-3, eps_r=1):
        dim = {"area": area, "dist": dist}
        const = {"eps_r": eps_r}
        LumpedElement.__init__(self, dim=dim, const=const)

    def __str__(self):
        return Cap(self.model["cap"])

    def get_model(self):
        return {"cap": eps0 * self.const["eps_r"] * self.dim["area"] / self.dim["dist"]}
