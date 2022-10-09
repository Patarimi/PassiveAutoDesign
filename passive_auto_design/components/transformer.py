# -*- coding: utf-8 -*-
"""

"""
import numpy as np
import passive_auto_design.components.lumped_element as lmp
from passive_auto_design.components.inductor import Inductor


class Transformer(lmp.LumpedElement):
    """
    Create a transformer object with the specified Inductors primary & secondary
    and calculate the associated electrical model
    if sym=True, Create a symmetrical transformer (secondary is ignored and assume egal to primary)
    """

    sym: bool

    def __init__(
        self,
        primary: Inductor,
        secondary=None,
        rho=0.0,
        eps_r=0.0,
        h_mut=0.0,
        h_gnd=0.0,
        sym=False,
    ):
        const = {
            "eps_r": eps_r,
            "rho": rho,
        }
        dim = {
            "h_mut": h_mut,
            "h_gnd": h_gnd,
        }
        for key in primary.dim.keys():
            dim["lp." + key] = primary.dim[key]
            dim["ls." + key] = primary.dim[key] if sym else secondary.dim[key]
        lmp.LumpedElement.__init__(self, dim=dim, const=const, sym=sym)

    def get_model(self):
        primary = Inductor(
            self.dim["lp.d_i"],
            self.dim["lp.n_turn"],
            self.dim["lp.width"],
            self.dim["lp.gap"],
        )
        self.model["lp"] = primary.model["ind"]
        if self.sym:
            self.model["ls"] = primary.model["ind"]
        else:
            secondary = Inductor(
                self.dim["ls.d_i"],
                self.dim["ls.n_turn"],
                self.dim["ls.width"],
                self.dim["ls.gap"],
            )
            self.model["ls"] = secondary.model["ind"]
        self.model["rp"] = self.r_geo(True)
        self.model["rs"] = self.r_geo(False)
        self.model["cm"] = self.cc_geo(True)
        self.model["cg"] = self.cc_geo(False)
        self.model["k"] = self.k_geo()
        return self.model

    def cc_geo(self, _mutual=True):
        """
        return the value of the distributed capacitance of the described transformer
        if _mutual, return the capacitance between primary and secondary
        else, return the capacitance to the ground plane
        """
        dim = self.dim
        if _mutual:
            dist = float(self.dim["h_mut"])
            d_i = np.max([dim["lp.d_i"], dim["ls.d_i"]])
            d_o = np.min(
                [
                    d_i + dim["lp.n_turn"] * dim["lp.width"],
                    d_i + dim["ls.n_turn"] * dim["ls.width"],
                ]
            )
        else:
            dist = float(self.dim["h_gnd"])
            d_i = np.min([dim["ls.d_i"], dim["lp.d_i"]])
            d_o = np.max(
                [
                    d_i + dim["lp.n_turn"] * dim["lp.width"],
                    d_i + dim["ls.n_turn"] * dim["ls.width"],
                ]
            )
        eps_r = float(self.const["eps_r"])
        area = 4 * (d_o**2 - d_i**2) * (1 + 2 * np.sqrt(2))
        cap = lmp.Capacitor(area, dist, eps_r)
        return np.abs(cap.model["cap"])

    def r_geo(self, _of_primary=True):
        """
        return the value of the resistance of the described transformer
        """
        geo = "lp." if _of_primary else "lp."
        rho = self.const["rho"]
        n_t = self.dim[geo + "n_turn"]
        l_tot = (
            8
            * np.tan(np.pi / 8)
            * n_t
            * (
                self.dim[geo + "d_i"]
                + self.dim[geo + "width"]
                + (n_t - 1) * (self.dim[geo + "width"] + self.dim[geo + "gap"])
            )
        )
        r_dc = lmp.Resistor(self.dim[geo + "width"], l_tot, rho)
        return r_dc.model["res"]

    def k_geo(self):
        """
        return the value of the coupling between the two inductors.

        """
        dim = self.dim
        c1 = dim["lp.width"] * dim["lp.n_turn"] + dim["lp.gap"] * (dim["lp.n_turn"] - 1)
        d1 = dim["lp.d_i"]
        c2 = dim["ls.width"] * dim["ls.n_turn"] + dim["ls.gap"] * (dim["ls.n_turn"] - 1)
        d2 = dim["ls.d_i"]
        return (
            0.99
            * (np.max([d1, d2]) - np.min([c1 + d1, c2 + d2]))
            / (np.max([c1 + d1, c2 + d2]) - np.min([d1, d2]))
        )
