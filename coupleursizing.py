# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
First, it describes the subtrate BOEL.
Then, it designs an hybrid coupler and an impendance tranformer.
"""
import numpy as np
import PassiveAutoDesign as pad
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
#Creation of a coupler in the BEOL substrate at 49.8 GHz and with 50 impendance
CPL_TST = pad.Coupler(BEOL)
RES = CPL_TST.design(49.8e9, 50.0)
CPL_TST.print(RES)
#Write the spice model of the optimal design found
with open('./cache/model_coupler.cir', 'w') as file:
    file.write(CPL_TST.transfo.generate_spice_model(0.9))

#%% Balun Design
# Design inputs
ZS_TARG = np.array([20+1j*40])
ZL_TARG = np.array([50 + 1j*0])
F_TARG = np.array([4e9])
K_COEFF = 0.9
# Creation of an impedance tranformer from ZS_TARG to ZL_TARG af F_TARG
BALUN_TST = pad.Balun(BEOL)
RES2 = BALUN_TST.design(F_TARG, ZL_TARG, ZS_TARG)
BALUN_TST.print(RES2)
# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
#Write the spice model of the optimal design found
with open('./cache/model_balun.cir', 'w') as file:
    file.write(BALUN_TST.transfo.generate_spice_model(0.9))
