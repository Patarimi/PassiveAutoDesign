# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea
"""

import numpy as np
from scipy.optimize import dual_annealing
import matplotlib.pyplot as plt
import PassiveAutoDesign as pad

# consignes
F_targ = 40e9     #fréquence de fonctionnement souhaitée
Z_targ = 50.0        #impédance caractéristique
do_targ = 300e-6 #diamètre externe maximum des bobines

k=0.9           #couplage des inductances

#limites
#x0 = (#largeur de la piste, #nombre de tour, #diamètre interne, #écart inter-tour)
x_max = (12e-6,                 4,              2*do_targ,          12e-6)
x_min = (2e-6,                  1,              2e-6,               2.1e-6)

#constantes physiques
eps_r = 4.3 #permitivité relative du silicium
d = 1.5e-6 #distance entre les deux inductances

def Cost(x):
    x[1] = np.round(x[1])
    L = pad.L_geo(x[0], x[3], x[1], x[2])
    Cc = pad.Cc_geo(x[0], x[1], x[2], eps_r, d)
    F_eff = pad.F_c(L, Cc, k)
    Z_eff = pad.Z_c(L, Cc)
    return pad.StdDev(np.array([F_eff, Z_eff]), np.array([F_targ, Z_targ]))

res = dual_annealing(Cost, list(zip(x_min, x_max)))
print(res.fun)

print(x_min)
print("(", end='')
for num in res.x:
    print("%.2g"%(num), end=' ')
print(")")
print(x_max)
