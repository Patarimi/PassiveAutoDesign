# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing

#Coupler Specific Function
def coupleur_f_c(l_c, c_c, k):
    """
        return the central frequency of an hybrid coupler with l inductance,
        c capacitance and k coupling
    """
    if(l_c <= 0)or(c_c <= 0)or(k == 1):
        return -1
    return (2-k)/(2*np.pi*np.sqrt(l_c*c_c))

def coupleur_z_c(l_c, c_c):
    """
        return the characteristic impedance of an hybrid coupler
        with l inductance and c capacitance
    """
    if(l_c <= 0)or(c_c <= 0):
        return -1
    return np.sqrt(l_c/c_c)

def coupleur_cost(solution, dist, eps_r, k, f_targ, z_targ):
    """
        return the cost (standard deviation)
        between the proposed solution and the targeted specifications
    """
    solution[1] = np.round(solution[1])
    l_c = l_geo(solution[0], solution[3], solution[1], solution[2])
    c_c = cc_geo(solution[0], solution[1], solution[2], eps_r, dist)
    f_eff = coupleur_f_c(l_c, c_c, k)
    z_eff = coupleur_z_c(l_c, c_c)
    return std_dev(np.array([f_eff, z_eff]), np.array([f_targ, z_targ]))

def coupleur_design(f_targ, z_targ, bounds, dist, eps_r, k):
    """
        design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
        return an optimization results (res)
    """
    res = dual_annealing(coupleur_cost, bounds, maxiter=2000, args=(dist, eps_r, k, f_targ, z_targ))
    return res




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
    