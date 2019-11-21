# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
First, it loads a subtrate BEOL.
Then, it designs an hybrid coupler and an impendance tranformer.
"""
import numpy as np
import passive_auto_design.substrate as sub
from passive_auto_design.ngspice_warper import set_path
import passive_auto_design.passive_component.Coupler as cpl
import passive_auto_design.passive_component.Balun as bln

#setting the installation directory of the ngspice software (to be install separately)
set_path('../ng_spice/')

#Loading the tech.yml file (see example_susbtrate.py)
BEOL = sub.Substrate('./tech.yml')

#%% Coupler Design
#Creation of a coupler in the BEOL substrate at F_TARG and with ZC_TARG characteristic impedance
CPL_TST = cpl.Coupler(BEOL, _k=0.99)
# Design inputs
CPL_TST.f_c = 18e9
CPL_TST.z_c = 50
RES = CPL_TST.design()
CPL_TST.print(RES)
#Write the spice model of the optimal design found
with open('model_coupler.cir', 'w') as file:
    file.write(CPL_TST.transfo.generate_spice_model(CPL_TST.k))

#%% Balun Design
BALUN_TST = bln.Balun(BEOL)
# Design inputs
BALUN_TST.f_c = np.array([18e9])
BALUN_TST.z_ld = np.array([2 - 1j*11])
BALUN_TST.z_src = np.array([18 - 1j*30])
BALUN_TST.k = 0.8

# Creation of an impedance tranformer from ZS_TARG to ZL_TARG at F_TARG
RES2 = BALUN_TST.design()
BALUN_TST.print(RES2)

# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']

#Write the spice model of the optimal design found
with open('model_balun.cir', 'w') as file:
    file.write(BALUN_TST.transfo.generate_spice_model(BALUN_TST.k))
