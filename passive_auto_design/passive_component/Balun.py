# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing
from ..structure.Transformer import Transformer
from ..special import std_dev, qual_f

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
    def __cost_geo_vs_targ(self, geo, _l_targ, _is_primary=True):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        if _is_primary:
            self.transfo.set_primary({'di':geo[2],
                                      'n_turn':np.round(geo[1]),
                                      'width':geo[0],
                                      'gap':geo[3],
                                      'height':self.transfo.prim['height']})
            l_sol = self.transfo.model['lp']
            r_sol = self.transfo.model['rp']
        else:
            self.transfo.set_secondary({'di':geo[2],
                                        'n_turn':np.round(geo[1]),
                                        'width':geo[0],
                                        'gap':geo[3],
                                        'height':self.transfo.second['height']})
            l_sol = self.transfo.model['lp']
            r_sol = self.transfo.model['rp']
        return std_dev(l_sol, _l_targ)+np.sum(r_sol)/100
    def design(self, _maxiter=1000):
        """
            design an impedance transformer
            with the targeted specifications (f_targ, zl_targ, zs_targ)
            return an optimization results (res)
        """
        alpha = (1-self.k**2)/self.k
        q_s = -qual_f(self.z_src)
        q_l = -qual_f(self.z_ld)
        #assuming perfect inductor for first calculation
        r_l1 = 0
        r_l2 = 0
        for i in range(2):
            q_s_prime = q_s * np.real(self.z_src)/(np.real(self.z_src)+r_l1)
            q_l_prime = q_l * np.real(self.z_ld)/(np.real(self.z_ld)+r_l2)
            b_coeff = (2*alpha*q_s_prime+q_s_prime+q_l_prime)
            discr = b_coeff**2-4*alpha*(alpha+1)*(1+q_s_prime**2)
            if discr < 0:
                ValueError("Negative value in square root,\
try to increase the coupling factor or the load quality factor\
or try to lower the source quality factor")
            z_sol = np.array(((b_coeff+np.sqrt(discr))/(2*(alpha+1)),
                              (b_coeff-np.sqrt(discr))/(2*(alpha+1))))
            qxl1 = z_sol/(1-self.k**2)
            qxl2 = z_sol*(1+q_l_prime**2)/(alpha*(1+(q_s_prime-z_sol)**2))
            l_sol1 = qxl1*np.real(self.z_src)/(2*np.pi*self.f_c)
            l_sol2 = qxl2*np.real(self.z_ld)/(2*np.pi*self.f_c)
            if l_sol1[0]*l_sol2[0] > l_sol1[1]*l_sol2[1]:
                #selecting the solution giving the smallest inductors
                l_1 = l_sol1[1]
                l_2 = l_sol2[1]
            else:
                l_1 = l_sol1[0]
                l_2 = l_sol2[0]
            #find the inductor geometry that give the desired inductances
            res1 = dual_annealing(self.__cost_geo_vs_targ, self.bounds[0:4], args=(l_1), maxiter=_maxiter)
            res2 = dual_annealing(self.__cost_geo_vs_targ, self.bounds[4:], args=(l_2, False), maxiter=_maxiter)
            r_l1 = self.transfo.model['rs']
            r_l2 = self.transfo.model['rp']
        res = OptimizeResult()
        res.x = np.concatenate((res1.x, res2.x))
        res.fun = (res1.fun + res2.fun)/2
        res.message = res1.message
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
        print(f'primary dim.:\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'secondary dim.:\t{sol[4]:.2g}\t{res.x[5]:.0g}\t{sol[6]:.3g}\t{sol[7]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
