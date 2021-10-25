# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: Patarimi

This Script is given as an example.
First, it loads a model map.
Then, it designs an hybrid coupler and an impedance transformer.
"""
import passive_auto_design.devices.coupler as cpl

MODEL_MAP_PATH = "./tests/default.map"

# Creation of a coupler in the BEOL substrate at central frequency f_c and with z_c characteristic impedance
CPL_TST = cpl.Coupler(modelmapfile=MODEL_MAP_PATH)
# Design inputs
CPL_TST.f_c = 18e9
CPL_TST.z_c = 50
RES = CPL_TST.design()
CPL_TST.print(RES)
