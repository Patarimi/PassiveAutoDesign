# -*- coding: utf-8 -*-
"""

"""
import numpy as np
from passive_auto_design.special import u0
import passive_auto_design.components.lumped_element as lmp


class Transformer(lmp.LumpedElement):
    """
    Create a transformer object with the specified geometry _primary & _secondary
    (which are dict defined as :
        {'di':_di,'n_turn':_n_turn, 'width':_width, 'gap':_gap, 'height':height})
    and calculate the associated electrical model
    """

    def __init__(self, primary, secondary, rho=0., eps_r=0., h_mut=0., h_gnd=0.):
        lmp.LumpedElement.__init__(self)
        self.par = {}
        self.par["rho"] = rho
        self.par["eps_r"] = eps_r
        self.par["h_mut"] = h_mut
        self.par["h_gnd"] = h_gnd
        self.par["lp"] = primary
        self.par["ls"] = secondary
        self.par["rp"] = self.r_geo(True)
        self.par["rs"] = self.r_geo(False)
        self.par["cm"] = self.cc_geo(True)
        self.par["cg"] = self.cc_geo(False)
        self.par["k"] = self.k_geo()
        self.ref = "k"

    def calc_ref_value(self):
        for subpart in ("ls", "lp", "rp", "rs", "cm", "cg"):
            self.par[subpart].calc_ref_value()
        return self.k_geo()

    def cc_geo(self, _mutual=True):
        """
        return the value of the distributed capacitance of the described transformer
        if _mutual, return the capacitance between primary and secondary
        else, return the capacitance to the ground plane
        """
        l1 = self.par["lp"].par
        l2 = self.par["ls"].par
        if _mutual:
            dist = float(self.par["h_mut"])
            d_i = np.max([l2["d_i"], l1["d_i"]])
            d_o = np.min([l1["d_i"] + l1["n_turn"] * l1["width"], l2["d_i"] + l2["n_turn"] * l2["width"]])
        else:
            dist = float(self.par["h_gnd"])
            d_i = np.min([l2["d_i"], l1["d_i"]])
            d_o = np.max([l1["d_i"] + l1["n_turn"] * l1["width"], l2["d_i"] + l2["n_turn"] * l2["width"]])
        eps_r = float(self.par["eps_r"])
        area = 4 * (d_o ** 2 - d_i ** 2) * (1 + 2 * np.sqrt(2))
        cap = lmp.Capacitor(area, dist, eps_r)
        return cap

    def r_geo(self, _of_primary=True):
        """
        return the value of the resistance of the described transformer
        """
        if _of_primary:
            geo = self.par["lp"].par
        else:
            geo = self.par["ls"].par
        rho = self.par["rho"]
        n_t = geo["n_turn"]
        l_tot = (
            8
            * np.tan(np.pi / 8)
            * n_t
            * (geo["d_i"] + geo["width"] + (n_t - 1) * (geo["width"] + geo["gap"]))
        )
        r_dc = lmp.Resistor(geo["width"], l_tot, rho)
        return r_dc

    def k_geo(self):
        """
        return the value of the coupling between the two inductors.

        """
        l1 = self.par["lp"].par
        l2 = self.par["ls"].par
        c1 = l1["width"]*l1["n_turn"] + l1["gap"]*(l1["n_turn"]-1)
        d1 = l1["d_i"]
        c2 = l2["width"]*l2["n_turn"] + l2["gap"]*(l2["n_turn"]-1)
        d2 = l2["d_i"]
        return 0.99*(np.max([d1, d2])-np.min([c1+d1, c2+d2]))/(np.max([c1+d1, c2+d2])-np.min([d1, d2]))
