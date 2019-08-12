# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing, minimize_scalar
import simulation.ngspice_warper as ng
from design.structure import Transformer

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
        b_model = bytes(self.transfo.generate_spice_model(self.k), encoding='UTF-8')
        b_simulation = bytes(ng.generate_ac_simulation(self.f_c, self.f_c, 1), encoding='UTF-8')
        s_p = ng.get_results(b_model+b_simulation)
        if ihsr(s_p[1], s_p[2]) > 26.7:
            return np.abs(s_p[0])
        return np.abs(s_p[0])+26.7-ihsr(s_p[1], s_p[2])
    def __cost_est_inductance(self, _di):
        self.transfo.prim['di'] = _di
        return np.abs(self.transfo.l_geo()-self.z_c/(2*np.pi*self.f_c))
    def __cost_est_capacitance(self, _width):
        self.transfo.prim['width'] = _width
        return np.abs(self.transfo.cc_geo()+self.transfo.cc_geo(False)-1/(self.z_c*2*np.pi*self.f_c))
    def design(self, f_targ, z_targ, _maxiter=500):
        """
            design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
            return an optimization results (res)
        """
        self.f_c = f_targ
        self.z_c = z_targ
        #finding the inner diameter that give the correct inductance
        minimize_scalar(self.__cost_est_inductance, bounds=self.bounds[2])
        #finding the path width that give the correct capacitor
        minimize_scalar(self.__cost_est_capacitance, bounds=self.bounds[0])
        geo = self.transfo.prim
        x_0 = np.array([geo['width'], geo['n_turn'], geo['di'], geo['gap']])
        res = dual_annealing(self.cost, self.bounds, x0=x_0, maxiter=_maxiter)
        return res
    def print(self, res):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(self.bounds)*1e6
        print(f'Solution funds with remaining error of: {float(res.fun):.2f}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'best point  :\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
class Balun:
    """
        Create a balun object
    """
    def __init__(self, _substrate, _fc=1e9, _z_source=50, _z_load=50, _k=0.9):
        eps_r = _substrate.sub[1].dielectric.epsilon
        h_int = _substrate.sub[1].height
        h_sub = _substrate.sub[3].height
        self.f_c = _fc
        self.z_src = _z_source
        self.z_ld = _z_load
        self.k = _k
        self.bounds = np.array([(_substrate.sub[0].width['min'], _substrate.sub[0].width['max']),
                                (1, 4),
                                (_substrate.sub[0].width['max'], 20*_substrate.sub[0].width['max']),
                                (_substrate.sub[0].gap, 1.01*_substrate.sub[0].gap),
                                (_substrate.sub[2].width['min'], _substrate.sub[2].width['max']),
                                (1, 4),
                                (_substrate.sub[2].width['max'], 20*_substrate.sub[2].width['max']),
                                (_substrate.sub[2].gap, 1.01*_substrate.sub[2].gap)])
        geo = {'di':20,
               'n_turn':1,
               'width':2e-6,
               'gap':2e-6,
               'height':_substrate.sub[0].height}
        self.transfo = Transformer(geo, geo, eps_r, h_int, h_sub)
    def cost(self, sol):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        self.transfo.set_primary({'di':sol[2],
                                  'n_turn':np.round(sol[1]),
                                  'width':sol[0],
                                  'gap':sol[3],
                                  'height':self.transfo.prim['height']})
        self.transfo.set_secondary({'di':sol[6],
                                    'n_turn':np.round(sol[5]),
                                    'width':sol[4],
                                    'gap':sol[7],
                                    'height':self.transfo.prim['height']})
        l_source = self.transfo.model['ls']
        l_load = self.transfo.model['lp']
        k = self.k
        alpha = (1-k**2)/k**2
        n_turn = k*np.sqrt(l_source/l_load)
        z_l = 1j*l_source*(k**2)*2*np.pi*self.f_c
        zs_r = alpha*z_l + z_l*(n_turn**2)*self.z_ld/(z_l+self.z_ld*(n_turn**2))
        zl_r = ((np.conj(self.z_src)+alpha*z_l)*z_l/(np.conj(self.z_src)+z_l+alpha*z_l))/n_turn**2
        return std_dev(zs_r, self.z_src) + std_dev(zl_r, self.z_ld)
    def design(self, _f_targ, _zl_targ, _zs_targ, _maxiter=500):
        """
            design an impedance transformer
            with the targeted specifications (f_targ, zl_targ, zs_targ)
            return an optimization results (res)
        """
        self.f_c = _f_targ
        self.z_src = _zs_targ
        self.z_ld = _zl_targ
        res = dual_annealing(self.cost, self.bounds, maxiter=_maxiter)
        return res
    def print(self, res):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(self.bounds)*1e6
        print(f'Solution funds with remaining error of: {res.fun:.2e}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'primary dim.:\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'secondary dim.:\t{sol[4]:.2g}\t{res.x[5]:.0g}\t{sol[6]:.3g}\t{sol[7]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
# Other functions
def std_dev(mesured, targeted):
    """
        return the standard deviation bewteen an array_like of results and their references.
    """
    m_l = mesured.size
    if m_l == targeted.size:
        std_d = np.zeros((m_l, 1))
        for t_i in range(m_l):
            std_d[t_i] = np.abs((mesured[t_i]-targeted[t_i])/(mesured[t_i]+targeted[t_i]))**2
        return np.sqrt(np.sum(std_d))
    return 100
def dB(cmplx):
    """
        Return the decibel value of the given imaginary number.
    """
    return 20*np.log10(np.abs(cmplx))
def ihsr(_s31, _s21):
    """
        Return the IHSR (Ideal Hybrid Splitting Ratio) for the given gains
    """
    return -np.min((dB(_s21-1j*_s31), dB(_s21+1j*_s31)))
