# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np

def F_c(L, Cc, k):
    return 1/(2*np.pi*np.sqrt(L*Cc*(1-k**2)))

def Z_c(L, Cc):
    return np.sqrt(L/Cc)

def L_geo(W, G, n, di):
    K1 = 2.25   #constante1 empirique pour inductance
    K2 = 3.55   #constante2 empirique pour inductance
    A = K1*4*np.pi*1e-7*n**2
    do = di + 2*n*W+2*(n-1)*G
    return 0.5*A*(di+do)/(1+K2*((do-di)/(do+di)))

def Cc_geo(W, n, di, eps_r, d):
    c1 = 2.32   #constante1 empirique pour capacité
    c2 = 3.3    #constante2 empirique pour capacité  
    return W*(8.854e-12*eps_r*(c1+c2*(n-1))*di)/d

def StdDev(Mes, Target):
    Ml = Mes.size
    if(Ml==Target.size):
        D = np.zeros([Ml-1, 1])
        for t in range(Ml):
            D[t] = ((Mes[t]-Target[t])/(Mes[t]+Target[t]))**2
            return np.sqrt(np.sum(D))
    else:
        return 0
    
def borne(a, Max, Min):
    return np.max([Min, np.min([a, Max])])
    
    