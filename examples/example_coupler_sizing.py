# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
First, it loads a modelmap.
Then, it designs an hybrid coupler and an impendance tranformer.
"""
import passive_auto_design.components.coupler as cpl
MODELMAP_PATH = "./tests/default.map"

#Creation of a coupler in the BEOL substrate at F_TARG and with ZC_TARG characteristic impedance
CPL_TST = cpl.Coupler(modelmapfile = MODELMAP_PATH)
# Design inputs
CPL_TST.f_c = 18e9
CPL_TST.z_c = 50
RES = CPL_TST.design()
CPL_TST.print(RES)
