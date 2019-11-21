# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing, minimize_scalar, OptimizeResult
import passive_auto_design.ngspice_warper as ng
from ..structure.Transformer import Transformer
from ..special import ihsr

PORTS = (ng.Ports('IN', name='IN'),
         ng.Ports('OUT', name='OUT'),
         ng.Ports('CPL', name='CPL'),
         ng.Ports('ISO', name='ISO'))
class Coupler:
    """
        Create a coupler object
    """
    def __init__(self, _substrate, _fc=1e9, _zc=50, _k=0.99):
        esp_r = _substrate.sub[1].dielectric.epsilon
        h_int = _substrate.sub[1].height
        h_sub = _substrate.sub[3].height
        self.f_c = _fc
        self.z_c = _zc
        self.k = _k
        self.bounds = np.array([(_substrate.sub[0].width['min'], _substrate.sub[0].width['max']),
                                (1, 4),
                                (_substrate.sub[0].width['max'], 20*_substrate.sub[0].width['max']),
                                (_substrate.sub[0].gap, 3*_substrate.sub[0].gap)])
        geo = {'di':20,
               'n_turn':2,
               'width':self.bounds[0, 0],
               'gap':self.bounds[3, 0],
               'height':_substrate.sub[0].height}
        self.transfo = Transformer(geo, geo, esp_r, h_int, h_sub, _fc)
    def cost(self, sol):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        geo = {'di':sol[2],
               'n_turn':np.round(sol[1]),
               'width':sol[0],
               'gap':sol[3],
               'height':self.transfo.prim['height']}
        self.transfo.set_primary(geo)
        self.transfo.set_secondary(geo)
        s_p = ng.run_ac_sim(self.transfo.generate_spice_model(self.k),
                            ports = PORTS,
                            freq_ctrl = (self.f_c, self.f_c, 1))
        return np.abs(s_p[0])+np.max([26.7-ihsr(s_p[1], s_p[2]), 0])
    def __cost_est_inductance(self, _di):
        self.transfo.prim['di'] = _di
        return np.abs(self.transfo.l_geo()-self.z_c/(2*np.pi*self.f_c))
    def __cost_est_capacitance(self, _width):
        self.transfo.prim['width'] = _width
        return np.abs(self.transfo.cc_geo()+self.transfo.cc_geo(False)-1/(self.z_c*2*np.pi*self.f_c))
    def design(self, _maxiter=500):
        """
            design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
            return an optimization results (res)
        """
        #finding the inner diameter that give the correct inductance
        minimize_scalar(self.__cost_est_inductance, bounds=self.bounds[2])
        #finding the path width that give the correct capacitor
        res_int = minimize_scalar(self.__cost_est_capacitance, bounds=self.bounds[0])
        geo = self.transfo.prim
        x_0 = np.array([geo['width'], geo['n_turn'], geo['di'], geo['gap']])
        if _maxiter == 0: #just get the first guess
            res = OptimizeResult()
            res.x = x_0
            res.fun = res_int.fun
            res.message = 'First Guess'
            return res
        res = dual_annealing(self.cost, self.bounds, x0=x_0, maxiter=_maxiter)
        return res
    def print(self, res):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(self.bounds)*1e6
        print(f'Solution funds with remaining error of: {float(res.fun):.2e}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'best point  :\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
