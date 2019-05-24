# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing
import ngspice_warper as ng

#Coupler Specific Function
def coupler_cost(solution, dist, eps_r, k, f_targ, z_targ):
    """
        return the cost (standard deviation)
        between the proposed solution and the targeted specifications
    """
    solution[1] = np.round(solution[1])
    l_c = l_geo(solution[0], solution[3], solution[1], solution[2])
    c_m = cc_geo(solution[0], solution[1], solution[2], eps_r, dist)
    c_g = cc_geo(solution[0], solution[1], solution[2], eps_r, 9.54e-6)
    z_eff, ihsr = ng.get_results(ng.generate_model_transfo(l_c, c_g, c_m, k, f_targ))
    return std_dev(np.array([z_eff]), np.array([z_targ]))+(26.7-ihsr)/(26.7+ihsr)

def coupler_design(f_targ, z_targ, bounds, dist, eps_r, k):
    """
        design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
        return an optimization results (res)
    """
    res = dual_annealing(coupler_cost, bounds, maxiter=200, args=(dist, eps_r, k, f_targ, z_targ))
    return res

def coupler_print(res, bounds):
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
def balun_cost(sol, k, zl_targ, zs_targ, f_targ):
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
    z_load = 1j*l_source*(k**2)*2*np.pi*f_targ
    zs_r = alpha*z_load + z_load*(n_turn**2)*zl_targ/(z_load+zl_targ*(n_turn**2))
    zl_r = ((np.conj(zs_targ)+alpha*z_load)*z_load/(np.conj(zs_targ)+z_load+alpha*z_load))/n_turn**2
    return std_dev(np.array([zs_r, zl_r]), np.array([zs_targ, zl_targ]))

def balun_design(f_targ, zl_targ, zs_targ, bounds, k):
    """
        design an impedance transformer with the targeted specifications (f_targ, zl_targ, zs_targ)
        return an optimization results (res)
    """
    res = dual_annealing(balun_cost, bounds, maxiter=1000, args=(k, zl_targ, zs_targ, f_targ))
    return res

def balun_print(res, bounds):
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

def cc_geo(width, n_turn, inner_diam, eps_r, dist):
    """
        return the value of the distributed capacitance of the described transformer
    """
    c_1 = 6.86344013   #constante1 empirique pour capacité
    c_2 = 5.24903708   #constante2 empirique pour capacité
    eps_0 = 8.85418782e-12
    return width*eps_0*eps_r*(c_1+c_2*(n_turn-1))*inner_diam/dist

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
