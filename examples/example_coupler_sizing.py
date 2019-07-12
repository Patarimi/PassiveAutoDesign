# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
First, it describes the subtrate BOEL.
Then, it designs an hybrid coupler and an impendance tranformer.
"""
import numpy as np
import passive_component as pad
import substrate as sub
#Definition of the substrate different layers
BEOL = sub.Substrate()
BEOL.add_layer(sub.Layer('M_top', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.sub[BEOL.get_index_of('M_top')].set_rules(2e-6, 20e-6, 2.1e-6)
BEOL.add_layer(sub.Layer('Via', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('M_bot', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.sub[BEOL.get_index_of('M_bot')].set_rules(2e-6, 20e-6, 2.1e-6)
BEOL.add_layer(sub.Layer('Inter', 9.54e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('gnd_plane', 3e-6, sub.COPPER, sub.SILICON_OXYDE))

#%% Hybrid Coupler Design
# Design inputs
F_TARG = 18e9
ZC_TARG = 50
K_COEFF = 0.99
#Creation of a coupler in the BEOL substrate at F_TARG and with ZC_TARG characteristic impedance
CPL_TST = pad.Coupler(BEOL, _k=K_COEFF)
RES = CPL_TST.design(F_TARG, ZC_TARG)
CPL_TST.print(RES)
#Write the spice model of the optimal design found
with open('./cache/model_coupler.cir', 'w') as file:
    file.write(CPL_TST.transfo.generate_spice_model(K_COEFF))

#%% Balun Design
# Design inputs
ZS_TARG = np.array([20+1j*40])
ZL_TARG = np.array([50 + 1j*0])
F_TARG = np.array([4e9])
# Creation of an impedance tranformer from ZS_TARG to ZL_TARG at F_TARG
BALUN_TST = pad.Balun(BEOL, _k=K_COEFF)
RES2 = BALUN_TST.design(F_TARG, ZL_TARG, ZS_TARG)
BALUN_TST.print(RES2)
# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
#Write the spice model of the optimal design found
with open('./cache/model_balun.cir', 'w') as file:
    file.write(BALUN_TST.transfo.generate_spice_model(K_COEFF))