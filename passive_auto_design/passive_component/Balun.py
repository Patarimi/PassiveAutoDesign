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
    def cost(self, sol, _l1, _l2):
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
                                    'height':self.transfo.second['height']})
        l_sol = np.array((self.transfo.model['lp'], self.transfo.model['ls']))
        r_sol = np.array((self.transfo.model['rp'], self.transfo.model['rs']))
        l_targ = np.array((_l1, _l2))
        return std_dev(l_sol, l_targ)+np.sum(r_sol)/100
    def design(self, _f_targ, _zl_targ, _zs_targ, _maxiter=1000):
        """
            design an impedance transformer
            with the targeted specifications (f_targ, zl_targ, zs_targ)
            return an optimization results (res)
        """
        self.f_c = _f_targ
        self.z_src = _zs_targ
        self.z_ld = _zl_targ
        alpha = (1-self.k**2)/self.k
        q_s = -qual_f(_zs_targ)
        q_l = -qual_f(_zl_targ)
        b_coeff = (2*alpha*q_s+q_s+q_l)
        discr = b_coeff**2-4*alpha*(alpha+1)*(1+q_s**2)
        if discr < 0:
            ValueError("Negative value in square root,\
try to increase the coupling factor or the load quality factor\
or try to lower the source quality factor")
        z_sol = np.array(((b_coeff+np.sqrt(discr))/(2*(alpha+1)),
                          (b_coeff-np.sqrt(discr))/(2*(alpha+1))))
        qxl1 = z_sol/(1-self.k**2)
        qxl2 = z_sol*(1+q_l**2)/(alpha*(1+(q_s-z_sol)**2))
        l_sol1 = qxl1*np.real(_zs_targ)/(2*np.pi*_f_targ)
        l_sol2 = qxl2*np.real(_zl_targ)/(2*np.pi*_f_targ)
        if l_sol1[0]*l_sol2[0] > l_sol1[1]*l_sol2[1]:
            #selecting the solution giving the smallest inductors
            l_1 = l_sol1[1]
            l_2 = l_sol2[1]
        else:
            l_1 = l_sol1[0]
            l_2 = l_sol2[0]
        #find the inductor geometry that give the desired inductances
        res = dual_annealing(self.cost, self.bounds, args=(l_1, l_2), maxiter=_maxiter)
        return res
    def print(self, res):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(self.bounds)*1e6
        print(f'Solution funds with remaining error of: {float(res.fun):5.2f}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'primary dim.:\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'secondary dim.:\t{sol[4]:.2g}\t{res.x[5]:.0g}\t{sol[6]:.3g}\t{sol[7]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
