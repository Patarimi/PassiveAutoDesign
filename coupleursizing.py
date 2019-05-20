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

#                         F_targ, Z_targ, bounds                   d,      eps_r, k
RES = pad.coupleur_design(5e9, 50.0, list(zip(X_MIN, X_MAX)), 1.35e-6, 4.3, 0.9)
pad.coupleur_print(RES, list(zip(X_MIN, X_MAX)))

