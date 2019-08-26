# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:27:56 2019
Feed validated values to Coupleur_Cost. Results should be close to zero.

@author: mpoterea
"""
#%% Comparison between EM simulation results and coupler_cost function results
# The cost function should as close as possible to zero.
import csv
from passive_auto_design.ngspice_warper import set_path
set_path('../ng_spice/')

import numpy as np
import matplotlib.pyplot as plt
import passive_auto_design.passive_component as pad
import passive_auto_design.substrate as sub
import passive_auto_design.ngspice_warper as ng

OUTPUT = list()   #contains list of tuples (cost, param sweep for plotting)
# importation of reference data and cost calculation
with open('tests/coupleur_data.csv', newline='') as data_file:
    DATA_RAW = csv.reader(data_file, delimiter='\t')
    for row in DATA_RAW:
        ng.set_ports(['in', 'out', 'cpl', 'iso'])
        try:
            if row[0]=='with':
                BEOL = sub.Substrate(row[1])
            else:
                x = {'width':float(row[0]), 'n_turn':float(row[1]), 'di':float(row[2]), 'gap':float(row[3]), 'height':BEOL.sub[0].height}
                k = float(row[4])
                f = float(row[5])
                z = complex(float(row[6]), float(row[7]))
                # calculation of deviation between calculation and validated values
                CPL = pad.Coupler(BEOL, f, z, k)
                CPL.transfo.set_primary(x)
                CPL.transfo.set_secondary(x)
                b_model = bytes(CPL.transfo.generate_spice_model(k), encoding='UTF-8')
                b_simulation = bytes(ng.generate_ac_simulation(f, f, 1), encoding='UTF-8')
                S = ng.run_ac_sim(b_model+b_simulation)
                Cost = np.abs(S[0]-(50-z)/(z+50))
                # output creation Cost and sweept variables
                OUTPUT.append((Cost, x['di'], x['n_turn']))
        except ValueError:
            #importation error gestion
            if row[0]=='#W':
                pass
COST_RES = np.array(OUTPUT)
ERROR = list(100*COST_RES[:,0])

plt.figure()
plt.plot(COST_RES[0:5, 1]*1e6, 100*COST_RES[0:5, 0], 'rx')
plt.plot(COST_RES[5:9, 1]*1e6, 100*COST_RES[5:9, 0], 'b+')
plt.legend(['n=2', 'n=1'])
plt.ylabel("Error (%)")
plt.xlabel("Inner Diameter (µm)")
plt.ylim(bottom=0)
plt.xlim(left=0)
plt.grid(True)
print(f'Typical Error\nmin:\t{np.min(ERROR):2.1f}\nmed:\t{np.median(ERROR):2.2f}\nmax:\t{np.max(ERROR):2.1f}')
assert np.median(ERROR) <= 4.4
assert np.max(ERROR) <= 10.4
