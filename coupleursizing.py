# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example. First, it describes the subtrate BOEL.
Then, it designs an hybrid coupler and an impendance tranformer.
"""

import numpy as np
import PassiveAutoDesign as pad
import substrate as sub

#%% Hybrid Coupleur Design
# Technological/geometrical constraints
OUTER_DIAM_TARG = 490e-6  #maximal outer diameter
#x0 = (#largeur de la piste, #nombre de tour, #diamètre interne, #écart inter-tour)
X_MAX = (20e-6, 4, 2*OUTER_DIAM_TARG, 2.15e-6)
X_MIN = (2e-6, 1, 50e-6, 2.1e-6)

#Definition of the substrate different layers
BEOL = sub.Substrate()
BEOL.add_layer(sub.Layer('M6', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.sub[BEOL.get_index_of('M6')].set_rules(2e-6, 20e-6, 2.1e-6)
BEOL.add_layer(sub.Layer('Via5', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('M5', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.sub[BEOL.get_index_of('M5')].set_rules(2e-6, 20e-6, 2.1e-6)
BEOL.add_layer(sub.Layer('Inter', 9.54e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('gnd_plane', 3e-6, sub.COPPER, sub.SILICON_OXYDE))

#Creation of a coupler in the BEOL substrate at 49.8 GHz and with 50 impendance
CPL_TST = pad.Coupler(BEOL)
RES = CPL_TST.design(49.8e9, 50.0, list(zip(X_MIN, X_MAX)))
CPL_TST.print(RES, list(zip(X_MIN, X_MAX)))

#Write the spice model of the optimal design found
with open('./cache/model_ind.cir', 'w') as file:
    file.write(CPL_TST.transfo.generate_spice_model(0.9))

ZS_TARG = np.array([20+1j*40, 20+1j*40])
ZL_TARG = np.array([50 + 1j*0, 0.1])
F_TARG = np.array([4e9, 8e9])

#%% Balun Design
# Desing inputs
K_COEFF = 0.9
# Technological/geometrical constraints
BOUNDS = list(zip(X_MIN+X_MIN, X_MAX+X_MAX))
# Creation of an impedance tranformer from ZS_TARG to ZL_TARG af F_TARG
BALUN_TST = pad.Balun(BEOL)
RES2 = BALUN_TST.design(F_TARG, ZL_TARG, ZS_TARG, BOUNDS)
BALUN_TST.print(RES2, BOUNDS)
# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
