# -*- coding: utf-8 -*-
"""

"""
import numpy as np
import yaml
from scipy.optimize import minimize, OptimizeResult
from ..components.transformer import Transformer
from ..special import std_dev, quality_f


class Balun:
    """
    Create a balun object
    """

    def __init__(self, _fc=1e9, _z_source=50, _z_load=50, modelmapfile=None):
        self.f_c = _fc
        self.z_src = _z_source
        self.z_ld = _z_load
        self.is_symmetrical = False
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
        self.bounds = np.array(
            [
                width_lim,  # width
                turn_lim,  # turn number
                (width_lim[1], 1e6),  # inner diameter
                (gap_lim, 1e6),  # gap
                width_lim,
                turn_lim,
                (width_lim[1], 1e6),
                (gap_lim, 1e6),
            ]
        )
        geo = {
            "di": 20,
            "n_turn": 1,
            "width": 2e-6,
            "gap": 2e-6,
        }
        self.transfo = Transformer(geo, geo, _fc, modelmapfile)

    def __cost_geo_vs_targ(self, geo, _l_targ, _is_primary=True):
        """
        return the cost (standard deviation)
        between the proposed solution and the targeted specifications
        """
        if _is_primary:
            self.transfo.set_primary(
                {
                    "di": geo[2],
                    "n_turn": np.round(geo[1]),
                    "width": geo[0],
                    "gap": geo[3],
                }
            )
            l_sol = self.transfo.model["lp"]
            r_sol = self.transfo.model["rp"]
        else:
            self.transfo.set_secondary(
                {
                    "di": geo[2],
                    "n_turn": np.round(geo[1]),
                    "width": geo[0],
                    "gap": geo[3],
                }
            )
            l_sol = self.transfo.model["lp"]
            r_sol = np.array(self.transfo.model["rp"])
        return std_dev(l_sol, _l_targ) + np.sum(r_sol) / 100

    def design(self, _maxiter=1000):
        """
        design an impedance transformer
        with the targeted specifications (f_targ, zl_targ, zs_targ)
        return an optimization results (res)
        """
        k = self.transfo.model["k"]
        alpha = (1 - k ** 2) / k
        q_s = -quality_f(self.z_src)
        q_l = -quality_f(self.z_ld)
        # assuming perfect inductor for first calculation
        r_l1 = 0
        r_l2 = 0
        for i in range(2):
            q_s_prime = q_s * np.real(self.z_src) / (np.real(self.z_src) + r_l1)
            q_l_prime = q_l * np.real(self.z_ld) / (np.real(self.z_ld) + r_l2)
            b_coeff = 2 * alpha * q_s_prime + q_s_prime + q_l_prime
            discr = b_coeff ** 2 - 4 * alpha * (alpha + 1) * (1 + q_s_prime ** 2)
            if discr < 0:
                raise ValueError(
                    "Negative value in square root,\
 try to increase the coupling factor or the load quality factor\
or try to lower the source quality factor"
                )
            z_sol = np.array(
                (
                    (b_coeff + np.sqrt(discr)) / (2 * (alpha + 1)),
                    (b_coeff - np.sqrt(discr)) / (2 * (alpha + 1)),
                )
            )
            qxl1 = z_sol / (1 - k ** 2)
            qxl2 = (
                z_sol * (1 + q_l_prime ** 2) / (alpha * (1 + (q_s_prime - z_sol) ** 2))
            )
            l_sol1 = qxl1 * np.real(self.z_src) / (2 * np.pi * self.f_c)
            l_sol2 = qxl2 * np.real(self.z_ld) / (2 * np.pi * self.f_c)
            if l_sol1[0] * l_sol2[0] > l_sol1[1] * l_sol2[1]:
                # selecting the solution giving the smallest inductors
                l_1 = l_sol1[1]
                l_2 = l_sol2[1]
            else:
                l_1 = l_sol1[0]
                l_2 = l_sol2[0]
            # find the inductor geometry that give the desired inductances
            res1 = minimize(
                fun=self.__cost_geo_vs_targ,
                x0=[x for x in self.transfo.prim.values()],
                bounds=self.bounds[0:4],
                args=l_1,
                options={'maxiter': _maxiter},
            )
            if self.is_symmetrical:
                self.__cost_geo_vs_targ(res1.x, l_2, _is_primary=False)
                res2 = res1
            else:
                res2 = minimize(
                    fun=self.__cost_geo_vs_targ,
                    x0=[x for x in self.transfo.prim.values()],
                    bounds=self.bounds[4:],
                    args=(l_2, False),
                    options={'maxiter': _maxiter},
                )
            r_l1 = self.transfo.model["rs"]
            r_l2 = self.transfo.model["rp"]
        res = OptimizeResult()
        res.x = np.concatenate((res1.x, res2.x))
        res.fun = (res1.fun + res2.fun) / 2
        res.message = res1.message
        return res

    def __enforce_symmetrical(self, _q_val, _of_load=True):
        """
        return the 'distance' to a symmetrical balun (ie. primary = secondary)
        if _of_load, altering the load impedance
        else altering the source impedance
        """
        k = self.transfo.model["k"]
        alpha = (1 - k ** 2) / k
        if _of_load:
            q_s = -quality_f(self.z_src)
            q_l = _q_val
        else:
            q_s = _q_val
            q_l = -quality_f(self.z_ld)
        b_coeff = 2 * alpha * q_s + q_s + q_l
        discr = b_coeff ** 2 - 4 * alpha * (alpha + 1) * (1 + q_s ** 2)
        if discr < 0:
            return np.inf
        z_sol = np.array(
            (
                (b_coeff + np.sqrt(discr)) / (2 * (alpha + 1)),
                (b_coeff - np.sqrt(discr)) / (2 * (alpha + 1)),
            )
        )
        qxl1 = z_sol / (1 - k ** 2)
        qxl2 = z_sol * (1 + q_l ** 2) / (alpha * (1 + (q_s - z_sol) ** 2))
        qxl_ratio = np.real(self.z_ld) / np.real(self.z_src)
        return np.abs(np.min(qxl1 / qxl2) - qxl_ratio)

    def enforce_symmetrical(self, side="load", _verbose=True):
        """
        alter the value of the load impedance (if side="load") or the source impedance
        in order to realize a symmetrical balun (ie. primary = secondary)
        """
        if side == "load":
            old_z = self.z_ld
            _through_load = True
        else:
            old_z = self.z_src
            _through_load = False
        res = minimize(
            self.__enforce_symmetrical,
            -quality_f(old_z),
            args=_through_load,
            method="Nelder-Mead",
        )
        new_z = np.real(old_z) * (1 - 1j * res.x)
        if _verbose:
            print(f"old z_ld: ${complex(old_z):5.2f}")
            print(f"new z_ld: ${complex(new_z):5.2f}")
        if _through_load:
            self.z_ld = new_z
        else:
            self.z_src = new_z
        self.is_symmetrical = True

    def print(self, res):
        """
        print a summary of the solution (res)
        with a comparison to the boundaries
        """
        message = ""
        sol = res.x * 1e6
        bds = np.array(self.bounds) * 1e6
        message += f"Solution funds with remaining error of: {float(res.fun):.2e}\n"
        message += "Termination message of algorithm: " + str(res.message) + "\n"
        message += "\t\t\tW (µm)\tn\tdi (µm)\tG (µm)\n"
        message += f"lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}\n"
        message += (
            f"primary dim.:\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}\n"
        )
        message += f"secondary dim.:\t{sol[4]:.2g}\t{res.x[5]:.0g}\t{sol[6]:.3g}\t{sol[7]:.2g}\n"
        message += f"upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}\n"
        return message
