# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 11:40:48 2020

@author: Potéreau
"""

import passive_auto_design.components.balun as bln
MODELMAP_PATH = "./tests/default.map"

BALUN_TST = bln.Balun(modelmapfile = MODELMAP_PATH)

# Design inputs
BALUN_TST.f_c = 18e9
BALUN_TST.z_ld = 2 - 1j*11
BALUN_TST.z_src = 50 - 1j*0.1

# Creation of an impedance tranformer from ZS_TARG to ZL_TARG at F_TARG
BALUN_TST.enforce_symmetrical("load")
RES2 = BALUN_TST.design()
BALUN_TST.print(RES2)

# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
