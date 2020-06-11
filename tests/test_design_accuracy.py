# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:27:56 2019
Feed validated values to Coupleur_Cost. Results should be close to zero.

@author: mpoterea
"""
#%% Comparison between EM simulation results and coupler_cost function results
import numpy as np
import pystest
import matplotlib.pyplot as plt
import passive_auto_design.passive_component.Coupler as pad
import passive_auto_design.substrate as sub
from passive_auto_design.ngspice_warper import set_path, OS_OK

if not OS_OK:
    pytest.skip("skipping windows-only tests", allow_module_level=True)
set_path('../ng_spice/')
BEOL = sub.Substrate('tests/passive_component_tech.yml')

# %% drawing of the cost function versus di and W
W_TABLE = np.arange(10e-6, 20e-6, 1e-6)
DI_TABLE = np.arange(100e-6, 400e-6, 50e-6)
DI, W = np.meshgrid(DI_TABLE, W_TABLE)

COST = np.zeros(DI.shape)
i = 0
for w in W_TABLE:
    j = 0
    for di in DI_TABLE:
        CPL = pad.Coupler(BEOL, 5e9, 50)
        if OS_OK:
            COST[i, j] = CPL.cost([w, 2, di, 2.1e-6])
        j += 1
    i += 1
FIG = plt.figure()
plt.grid(True)
CS = plt.contour(DI*1e6, W*1e6, -COST)
plt.clabel(CS, inline=1, fontsize=10)
plt.title("-Cost (dB)")
plt.ylabel("Width (µm)")
plt.xlabel("Inner Diameter (µm)")
#calculation of the first guess
CPL.design(_maxiter=0)
plt.plot(CPL.transfo.prim['di']*1e6, CPL.transfo.prim['width']*1e6, 'rx')
