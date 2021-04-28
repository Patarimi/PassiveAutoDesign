# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 11:40:48 2020

@author: Patarimi
"""

import passive_auto_design.components.balun as bln
MODEL_MAP_PATH = "./tests/default.map"

# Creation of an impedance transformer
BALUN_TST = bln.Balun(modelmapfile=MODEL_MAP_PATH)

# Design inputs
BALUN_TST.f_c = 18e9
BALUN_TST.z_ld = 2 - 1j*11
BALUN_TST.z_src = 50 - 1j*0.1

# force symmetrical balun by altering load
BALUN_TST.enforce_symmetrical("load")
RES2 = BALUN_TST.design()
BALUN_TST.print(RES2)

# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model['ls']
LL_SYNTH = BALUN_TST.transfo.model['lp']
