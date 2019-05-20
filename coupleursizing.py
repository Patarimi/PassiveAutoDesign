# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea
"""

import numpy as np
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

#design transformateur d'impedances
ZS_TARG = 20+1j*40
ZL_TARG = 50 + 1j*0
K_COEFF = 0.9
ALPHA = (1-K_COEFF**2)/K_COEFF**2
F_TARG = 50e9
Q_S = np.imag(ZS_TARG)/np.real(ZS_TARG)
Q_L = np.imag(ZL_TARG)/np.real(ZL_TARG)
A_FACT = (2*ALPHA*Q_S+Q_S+Q_L)/(2*(ALPHA+1))
B_FACT = np.sqrt((2*ALPHA*Q_S+Q_S+Q_L)**2-4*(ALPHA**2+ALPHA)*(1+Q_S**2))/(2*(ALPHA+1))
Z_T = np.array([A_FACT+B_FACT, A_FACT-B_FACT])

LS = np.real(ZS_TARG)*Z_T/((1-K_COEFF**2)*(2*np.pi*F_TARG))
LL = np.real(ZL_TARG)*Z_T*(1+Q_L**2)/(ALPHA*(1+(Q_S-Z_T)**2)*(2*np.pi*F_TARG))

BOUNDS = list(zip(X_MIN+X_MIN, X_MAX+X_MAX))
RES = pad.balun_design(F_TARG, ZL_TARG, ZS_TARG, BOUNDS, K_COEFF)
pad.balun_print(RES, BOUNDS)

LS_SYNTH = pad.l_geo(RES.x[0], RES.x[3], RES.x[1], RES.x[2])
LL_SYNTH = pad.l_geo(RES.x[4], RES.x[7], RES.x[5], RES.x[6])
