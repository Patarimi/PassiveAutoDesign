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
Z_targ = 50.0     #impédance caractéristique
do_targ = 300e-6  #diamètre externe maximum des bobines

#limites
#x0 = (#largeur de la piste, #nombre de tour, #diamètre interne, #écart inter-tour)
x_max = (20e-6,                 4,              2*do_targ,          12e-6)
x_min = (2e-6,                  1,              2e-6,               2.1e-6)

#constantes physiques
eps_r = 4.3#permitivité relative du silicium
d = 1.5e-6 #distance entre les deux inductances
k=0.9      #couplage des inductances

res = dual_annealing(pad.Coupleur_Cost, list(zip(x_min, x_max)), maxiter=2000, args=(d, eps_r, k, F_targ, Z_targ))
print(res.fun)
print(res.message)

print(f'lower bound : ({x_min[0]:.2e}, {x_min[1]:.2g}, {x_min[2]:.2e}, {x_min[3]:.2e})')
print(f'best point  : ({res.x[0]:.2e}, {res.x[1]:.2g}, {res.x[2]:.2e}, {res.x[3]:.2e})')
print(f'lower bound : ({x_max[0]:.2e}, {x_max[1]:.2g}, {x_max[2]:.2e}, {x_max[3]:.2e})')

L = pad.L_geo(res.x[0], res.x[3], res.x[1], res.x[2])
Cc = pad.Cc_geo(res.x[0], res.x[1], res.x[2], eps_r, d)
F_eff = pad.Coupleur_F_c(L, Cc, k)
Z_eff = pad.Coupleur_Z_c(L, Cc)
