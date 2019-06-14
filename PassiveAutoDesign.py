# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing
import ngspice_warper as ng

#Coupler Specific Function
class Coupler:
    """
        Create a coupler object
    """
    def __init__(self, _substrate, _fc=1e9, _zc=50):
        self.substrate = _substrate
        self.geometry = [0, 0, 0, 0]
        self.f_c = _fc
        self.z_c = _zc
    def cost(self, solution, dist, eps_r, k):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        solution[1] = np.round(solution[1])
        l_p = l_geo(solution[0], solution[3], solution[1], solution[2])
        c_m = cc_geo(solution[0], solution[1], solution[2], dist, eps_r)
        c_g = cc_geo(solution[0], solution[1], solution[2], 9.54e-6, eps_r)
        r_p = r_geo(solution[0], solution[1], solution[2], 3e-6, 17e-9)
        b_model = bytes(ng.generate_model_transfo(l_p, c_g, c_m, k, r_p), encoding='UTF-8')
        b_simulation = bytes(ng.generate_ac_simulation(self.z_c, self.f_c, 1), encoding='UTF-8')
        z_eff, ihsr = ng.get_results(b_model+b_simulation)
        if ihsr > 26.7:
            return std_dev(np.array([z_eff]), np.array([self.z_c]))
        return std_dev(np.array([z_eff, ihsr]), np.array([self.z_c, 26.7]))
    def design(self, f_targ, z_targ, bounds, dist, eps_r, k):
        """
            design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
            return an optimization results (res)
        """
        self.f_c = f_targ
        self.z_c = z_targ
        res = dual_annealing(self.cost, bounds, maxiter=200, args=(dist, eps_r, k))
        return res
    def print(self, res, bounds):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(bounds)*1e6
        print(f'Solution funds with remaining error of: {res.fun:.2e}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(bounds[1])[0]:.2g}\t\
    {(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'best point  :\t{sol[0]:.2g}\t{res.x[1]:.2g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(bounds[1])[1]:.2g}\t\
    {(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')

#Impendance Transformer Specific Function
class Balun:
    """
        Create a balun object
    """
    def __init__(self, _substrate, _fc=1e9, _z_source=50, _z_load=50):
        self.substrate = _substrate
        self.geometry = [0, 0, 0, 0]
        self.f_c = _fc
        self.z_src = _z_source
        self.z_ld = _z_load
    def cost(self, sol, k):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        sol[1] = np.round(sol[1])
        sol[5] = np.round(sol[5])
        l_source = l_geo(sol[0], sol[3], sol[1], sol[2])
        l_load = l_geo(sol[4], sol[7], sol[5], sol[6])
        alpha = (1-k**2)/k**2
        n_turn = k*np.sqrt(l_source/l_load)
        z_l = 1j*l_source*(k**2)*2*np.pi*self.f_c
        zs_r = alpha*z_l + z_l*(n_turn**2)*self.z_ld/(z_l+self.z_ld*(n_turn**2))
        zl_r = ((np.conj(self.z_src)+alpha*z_l)*z_l/(np.conj(self.z_src)+z_l+alpha*z_l))/n_turn**2
        return std_dev(zs_r, self.z_src) + std_dev(zl_r, self.z_ld)
    def design(self, _f_targ, _zl_targ, _zs_targ, _bounds, _k):
        """
            design an impedance transformer with the targeted specifications (f_targ, zl_targ, zs_targ)
            return an optimization results (res)
        """
        self.f_c = _f_targ
        self.z_src = _zs_targ
        self.z_ld = _zl_targ
        res = dual_annealing(self.cost, _bounds, maxiter=1000, args=(_k))
        return res
    def print(self, res, bounds):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(bounds)*1e6
        print(f'Solution funds with remaining error of: {res.fun:.2e}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(bounds[1])[0]:.2g}\t\
    {(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'primary dim.:\t{sol[0]:.2g}\t{res.x[1]:.2g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'secondary dim.:\t{sol[4]:.2g}\t{res.x[5]:.2g}\t{sol[6]:.3g}\t{sol[7]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(bounds[1])[1]:.2g}\t\
    {(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')

#General Purpose Function
def l_geo(width, gap, n_turn, inner_diam):
    """
        return the value of the distributed inductance of the described transformer
    """
    k_1 = 2.25   #constante1 empirique pour inductance
    k_2 = 3.55   #constante2 empirique pour inductance
    outer_diam = inner_diam + 2*n_turn*width+2*(n_turn-1)*gap
    rho = (inner_diam+outer_diam)/2
    density = (outer_diam-inner_diam)/(outer_diam+inner_diam)
    return k_1*4*np.pi*1e-7*n_turn**2*rho/(1+k_2*density)
def cc_geo(width, n_turn, inner_diam, dist, eps_r):
    """
        return the value of the distributed capacitance of the described transformer
    """
    c_1 = 6.86344013   #constante1 empirique pour capacité
    c_2 = 5.24903708   #constante2 empirique pour capacité
    eps_0 = 8.85418782e-12
    return width*eps_0*eps_r*(c_1+c_2*(n_turn-1))*inner_diam/dist
def r_geo(width, n_turn, inner_diam, height, rho=17e-10):
    """
        return the value of the resistance of the described transformer
    """
    c_1 = 6.86344013   #constante1 empirique pour capacité
    c_2 = 5.24903708   #constante2 empirique pour capacité
    return rho*(c_1+c_2*(n_turn-1))*inner_diam/(width*height)
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
