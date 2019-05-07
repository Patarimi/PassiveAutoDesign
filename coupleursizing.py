# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea
"""

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import Lib as li

# consignes
F_targ = 40e9     #fréquence de fonctionnement souhaitée
Z_targ = 50.0        #impédance caractéristique
do_targ = 300e-6 #diamètre externe maximum des bobines
W_min = 2e-6
W_max = 12e-6
n_min = 1
n_max=4         #nombre de tours maximum des bobines
di_min = 2e-6
di_max = 2*do_targ

N=10            #nombre maximum d'intération de l'algorithme
k=0.9           #couplage des inductances

#initialisation
x0 = [W_min + np.random.random()*(W_max-W_min), 
      np.random.randint(n_min, n_max),         #nombre de tour
      di_min + np.random.random()*(di_max-di_min)]  #diamètre interne

eps_r = 4.3 #permitivité relative du silicium
G = 2.1e-6  #espace inter-tour
d = 1.35e-6 #distance entre les deux inductances

def Cost(x):
    W = x[0]
    G = 2.1e-6
    n = np.round(x[1])
    di=x[2]
    L = li.L_geo(W, G, n, di)
    Cc = li.Cc_geo(W, n, di, eps_r, d)
    F_eff = li.F_c(L, Cc, k)
    Z_eff = li.Z_c(L, Cc)
    return li.StdDev(np.array([F_eff, Z_eff]), np.array([F_targ, Z_targ]))

res = minimize(Cost, x0, method='nelder-mead', options={'xtol': 1e-15, 'disp': True})

W = res.x[0]
G = 2.1e-6
n = np.round(res.x[1])
di= res.x[2]
L = li.L_geo(W, G, n, di)
Cc = li.Cc_geo(W, n, di, eps_r, d)
do = di + 2*n*W+2*(n-1)*G
F_eff = li.F_c(L, Cc, k)
Z_eff = li.Z_c(L, Cc)
print(Cost(res.x))
