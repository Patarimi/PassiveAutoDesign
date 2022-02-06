# -*- coding: utf-8 -*-
"""

"""
import numpy as np
import yaml
import skrf as rf
from passive_auto_design.special import u0
import passive_auto_design.components.lumped_element as lmp


class Transformer:
    """
    Create a transformer object with the specified geometry _primary & _secondary
    (which are dict defined as :
        {'di':_di,'n_turn':_n_turn, 'width':_width, 'gap':_gap, 'height':height})
    and calculate the associated electrical model
    """

    def __init__(self, primary, secondary, freq=1e9, model_map_file=None):
        self.prim = primary
        self.second = secondary
        if isinstance(freq, rf.Frequency):
            self.freq = freq
        elif isinstance(freq, float):
            self.freq = rf.Frequency(freq, freq, 1, unit="Hz")
        else:
            self.freq = rf.Frequency.from_f(freq, unit="Hz")
        if model_map_file is None:
            model_map_file = "tests/default.map"
        with open(model_map_file, "r") as file:
            self.model_map = yaml.full_load(file)
        self.model = {}
        self.set_primary(primary)
        self.set_secondary(secondary)

    def set_primary(self, _primary):
        """
        modify the top inductor and refresh the related model parameters
        """
        self.prim = _primary
        self.model.update(
            {
                "lp": self.l_geo(True),
                "rp": self.r_geo(True),
                "cg": self.cc_geo(False),
                "cm": self.cc_geo(True),
                "k": self.k_geo(),
            }
        )
        try:
            self.circuit = self.__make_circuit()
        except KeyError:
            pass

    def set_secondary(self, _secondary):
        """
        modify the bottom inductor and refresh the related model parameters
        """
        self.second = _secondary
        self.model.update(
            {
                "ls": self.l_geo(False),
                "rs": self.r_geo(False),
                "cg": self.cc_geo(False),
                "cm": self.cc_geo(True),
                "k": self.k_geo(),
            }
        )
        try:
            self.circuit = self.__make_circuit()
        except KeyError:
            pass

    def l_geo(self, _of_primary=True):
        """
        return the value of the distributed inductance of the described transformer
        if _of_primary, return the value of the top inductor
        else, return the value of the bottom inductor
        """
        k_1 = float(self.model_map["mu_r"])  # constante1 empirique pour inductance
        k_2 = float(self.model_map["dens"])  # constante2 empirique pour inductance
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        outer_diam = (
            geo["di"]
            + 2 * geo["n_turn"] * geo["width"]
            + 2 * (geo["n_turn"] - 1) * geo["gap"]
        )
        rho = (geo["di"] + outer_diam) / 2
        density = (outer_diam - geo["di"]) / (outer_diam + geo["di"])
        return k_1 * u0 * geo["n_turn"] ** 2 * rho / (1 + k_2 * density)

    def cc_geo(self, _mutual=True):
        """
        return the value of the distributed capacitance of the described transformer
        if _mutual, return the capacitance between primary and secondary
        else, return the capacitance to the ground plane
        """
        if _mutual:
            dist = float(self.model_map["d_m"])
        else:
            dist = float(self.model_map["d_g"])
        n_t = self.prim["n_turn"]
        eps_r = float(self.model_map["eps_r"])
        area = n_t * self.prim["di"] * self.prim["width"]
        cap = lmp.Capacitor(area, dist, eps_r)
        return cap.par["cap"]

    def r_geo(self, _of_primary=True):
        """
        return the value of the resistance of the described transformer
        """
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        rho = self.model_map["rho"]
        n_t = geo["n_turn"]
        l_tot = (
            8
            * np.tan(np.pi / 8)
            * n_t
            * (geo["di"] + geo["width"] + (n_t - 1) * (geo["width"] + geo["gap"]))
        )
        r_dc = rho * l_tot / geo["width"]
        return np.maximum(r_dc, 0)

    def k_geo(self):
        """
        return the value of the coupling between the two inductors.

        """
        return self.model_map["cpl_eq"]

    def mutual_geo(self, z_0=50):
        """
        Create a transformer with a primary of l_1, and secondary of l_2
        and a coupling factor of k_mut
        """
        l_1 = self.model["lp"]
        l_2 = self.model["ls"]
        r_1 = self.model["rp"]
        r_2 = self.model["rs"]
        k_mut = self.model["k"]
        for f_t in self.freq.f:
            w_t = float(2 * np.pi * f_t)
            y_1 = 1 / (r_1 + 1j * w_t * l_1 * (1 - k_mut ** 2))
            y_2 = 1 / (r_2 + 1j * w_t * l_2 * (1 - k_mut ** 2))
            y_m = k_mut / (1e-30 + 1j * w_t * np.sqrt(l_1 * l_2) * (1 - k_mut ** 2))
            y_param = np.array(
                [
                    [
                        [y_1, -y_m, y_m, -y_1],
                        [-y_m, y_2, -y_2, y_m],
                        [y_m, -y_2, y_2, -y_m],
                        [-y_1, y_m, -y_m, y_1],
                    ]
                ]
            )
            try:
                y_params = np.vstack((y_params, y_param))
            except NameError:  # Only needed for first iteration.
                y_params = np.copy(y_param)
        ntwk = rf.Network(
            frequency=self.freq, s=rf.y2s(y_params), z0=z_0, name="coupled inductors"
        )
        return ntwk

    def __make_circuit(self):
        media = rf.media.DefinedGammaZ0(frequency=self.freq, Z0=50)
        transfo_ideal = self.mutual_geo()
        cap_g, ports = [], []
        for i in range(4):
            cap_g.append(media.capacitor(self.model["cg"], name=f"cg{i}"))
            ports.append(rf.Circuit.Port(self.freq, f"port{i}"))
        cap_m1 = media.capacitor(self.model["cm"], name="cm1")
        cap_m2 = media.capacitor(self.model["cm"], name="cm2")

        connections = []
        for i in range(4):
            connections.append([(ports[i], 0), (transfo_ideal, i), (cap_g[i], 0)])
        connections.append([(cap_m1, 0), (transfo_ideal, 0)])
        connections.append([(cap_m1, 1), (transfo_ideal, 1)])
        connections.append([(cap_m2, 0), (transfo_ideal, 3)])
        connections.append([(cap_m2, 1), (transfo_ideal, 2)])
        cir = rf.Circuit(connections)
        return cir
