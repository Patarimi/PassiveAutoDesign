# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
First, it loads a subtrate BEOL.
Then, it designs an hybrid coupler and an impendance tranformer.
"""
import passive_auto_design.components.coupler as cpl
import passive_auto_design.components.balun as bln

MODELMAP_PATH = "./tests/default.map"

#%% Coupler Design
#Creation of a coupler in the BEOL substrate at F_TARG and with ZC_TARG characteristic impedance
CPL_TST = cpl.Coupler(modelmapfile = MODELMAP_PATH)
# Design inputs
CPL_TST.f_c = 18e9
CPL_TST.z_c = 50
RES = CPL_TST.design()
CPL_TST.print(RES)

#%% Balun Design
BALUN_TST = bln.Balun(modelmapfile = MODELMAP_PATH)
# Design inputs
BALUN_TST.f_c = 18e9
BALUN_TST.z_ld = 2 - 1j*11
BALUN_TST.z_src = 50 - 1j*0.1

# Creation of an impedance tranformer from ZS_TARG to ZL_TARG at F_TARG
BALUN_TST.enforce_symmetrical(False)
RES2 = BALUN_TST.design()
BALUN_TST.print(RES2)

# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
