# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea
"""

import numpy as np
import PassiveAutoDesign as pad
import substrate as sub

#Hybrid Coupleur Design
#Limits
OUTER_DIAM_TARG = 490e-6  #diamètre externe maximum des bobines
#x0 = (#largeur de la piste, #nombre de tour, #diamètre interne, #écart inter-tour)
X_MAX = (20e-6, 4, 2*OUTER_DIAM_TARG, 2.15e-6)
X_MIN = (2e-6, 1, 50e-6, 2.1e-6)

#Definition of the substrate different layers
BEOL = sub.Substrate()
BEOL.add_layer(sub.Layer('M6', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('Via5', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('M5', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('Inter', 9.54e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('gnd_plane', 3e-6, sub.COPPER, sub.SILICON_OXYDE))

#Creation of a coupleur in the BEOL substrate at 49.8 GHz and with 50 impendance
CPL_TST = pad.Coupler(BEOL)
RES = CPL_TST.design(49.8e9, 50.0, list(zip(X_MIN, X_MAX)))
CPL_TST.print(RES, list(zip(X_MIN, X_MAX)))

#Write the spice model of the optimal design found
with open('./cache/model_ind.cir', 'w') as file:
    file.write(CPL_TST.transfo.generate_spice_model(0.9))

# %%design transformateur d'impedances
# consignes
ZS_TARG = np.array([20+1j*40, 20+1j*40])
ZL_TARG = np.array([50 + 1j*0, 0.1])
F_TARG = np.array([4e9, 8e9])
K_COEFF = 0.9
#calcul inductances source (LS) et load (LL) théoriques
ALPHA = (1-K_COEFF**2)/K_COEFF**2
Q_S = np.imag(ZS_TARG)/np.real(ZS_TARG)
Q_L = np.imag(ZL_TARG)/np.real(ZL_TARG)
A_FACT = (2*ALPHA*Q_S+Q_S+Q_L)/(2*(ALPHA+1))
B_FACT = np.sqrt((2*ALPHA*Q_S+Q_S+Q_L)**2-4*(ALPHA**2+ALPHA)*(1+Q_S**2))/(2*(ALPHA+1))
Z_T = np.array([A_FACT+B_FACT, A_FACT-B_FACT])
LS = np.dot(np.real(ZS_TARG)*Z_T, 1/((1-K_COEFF**2)*(2*np.pi*F_TARG)))
LL = np.real(ZL_TARG)*Z_T*(1+Q_L**2)/(ALPHA*(1+(Q_S-Z_T)**2)*(2*np.pi*F_TARG))

#limites
BOUNDS = list(zip(X_MIN+X_MIN, X_MAX+X_MAX))
#optimisation
BALUN_TST = pad.Balun(BEOL)
RES2 = BALUN_TST.design(F_TARG, ZL_TARG, ZS_TARG, BOUNDS)
BALUN_TST.print(RES2, BOUNDS)

#valeurs LS et LL synthetisées par l'optimisation
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
