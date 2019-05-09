# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np

def Coupleur_F_c(L, Cc, k):
    if(L<=0)or(Cc<=0)or(k==1):
        return -1
    else:
        return (2-k)/(2*np.pi*np.sqrt(L*Cc))

def Coupleur_Z_c(L, Cc):
    if(L<=0)or(Cc<=0):
        return -1
    else:
        return np.sqrt(L/Cc)

def Coupleur_Cost(x, d, eps_r, k, F_targ, Z_targ):
    x[1] = np.round(x[1])
    L = L_geo(x[0], x[3], x[1], x[2])
    Cc = Cc_geo(x[0], x[1], x[2], eps_r, d)
    F_eff = Coupleur_F_c(L, Cc, k)
    Z_eff = Coupleur_Z_c(L, Cc)
    return StdDev(np.array([F_eff, Z_eff]), np.array([F_targ, Z_targ]))

def L_geo(W, G, n, di):
    K1 = 2.25   #constante1 empirique pour inductance
    K2 = 3.55   #constante2 empirique pour inductance
    A = K1*4*np.pi*1e-7*n**2
    do = di + 2*n*W+2*(n-1)*G
    return 0.5*A*(di+do)/(1+K2*((do-di)/(do+di)))

def Cc_geo(W, n, di, eps_r, d):
    c1 = 2.32   #constante1 empirique pour capacité
    c2 = 3.3    #constante2 empirique pour capacité  
    eps_0 = 8.854e-12
    return W*(eps_0*eps_r*(c1+c2*(n-1))*di)/d

def StdDev(Mes, Target):
    Ml = Mes.size
    if(Ml==Target.size):
        D = np.zeros((Ml, 1))
        for t in range(Ml):
            D[t] = ((Mes[t]-Target[t])/(Mes[t]+Target[t]))**2
        return np.sqrt(np.sum(D))
    else:
        return 100

    