# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
First, it loads a subtrate BEOL.
Then, it designs an hybrid coupler and an impendance tranformer.
"""
import numpy as np
import passive_auto_design.passive_component as pad
import passive_auto_design.substrate as sub
from passive_auto_design.ngspice_warper import set_path

#setting the installation directory of the ngspice software (to be install separately)
set_path('../Spice64/bin/')

#Loading the tech.yml file (see example_susbtrate.py)
BEOL = sub.Substrate('./tech.yml')
#%% Coupler Design
# Design inputs
F_TARG = 18e9
ZC_TARG = 50
K_COEFF = 0.99
#Creation of a coupler in the BEOL substrate at F_TARG and with ZC_TARG characteristic impedance
CPL_TST = pad.Coupler(BEOL, _k=K_COEFF)
RES = CPL_TST.design(F_TARG, ZC_TARG)
CPL_TST.print(RES)
#Write the spice model of the optimal design found
with open('model_coupler.cir', 'w') as file:
    file.write(CPL_TST.transfo.generate_spice_model(K_COEFF))

#%% Balun Design
# Design inputs
ZS_TARG = np.array([18 - 1j*30])
ZL_TARG = np.array([2 - 1j*11])
F_TARG = np.array([4e9])
# Creation of an impedance tranformer from ZS_TARG to ZL_TARG at F_TARG
BALUN_TST = pad.Balun(BEOL, _k=K_COEFF)
RES2 = BALUN_TST.design(F_TARG, ZL_TARG, ZS_TARG)
BALUN_TST.print(RES2)
# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
#Write the spice model of the optimal design found
with open('model_balun.cir', 'w') as file:
    file.write(BALUN_TST.transfo.generate_spice_model(K_COEFF))
