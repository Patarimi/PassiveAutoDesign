# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea
"""

import PassiveAutoDesign as pad

#design coupleur hybride
#limites
OUTER_DIAM_TARG = 490e-6  #diamètre externe maximum des bobines
#x0 = (#largeur de la piste, #nombre de tour, #diamètre interne, #écart inter-tour)
X_MAX = (20e-6, 4, 2*OUTER_DIAM_TARG, 2.15e-6)
X_MIN = (2e-6, 1, 50e-6, 2.1e-6)

res = pad.Coupleur_Design(5e9,   50.0,   list(zip(x_min, x_max)), 1.35e-6, 4.3,   0.9)
print(f'Solution funds with remaining error of: {res.fun:.2e}')
print('Termination message of algorithm: '+str(res.message))
print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
print(f'lower bound :\t{1e6*x_min[0]:.2g}\t{x_min[1]:.2g}\t{1e6*x_min[2]:.2g}\t{1e6*x_min[3]:.2g}')
print(f'best point  :\t{1e6*res.x[0]:.2g}\t{res.x[1]:.2g}\t{1e6*res.x[2]:.3g}\t{1e6*res.x[3]:.2g}')
print(f'lower bound :\t{1e6*x_max[0]:.2g}\t{x_max[1]:.2g}\t{1e6*x_max[2]:.2g}\t{1e6*x_max[3]:.2g}')#                         F_targ, Z_targ, bounds                   d,      eps_r, k
