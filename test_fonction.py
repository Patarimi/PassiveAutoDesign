# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:27:56 2019
Feed validated values to Coupleur_Cost. Results should be close to zero.

@author: mpoterea
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import PassiveAutoDesign as pad

OUTPUT = list()   #contains list of truples (cost, param sweep for plotting)

# importation of reference data and cost calculation
with open('./test_set/coupleur_data.csv', newline='') as data_file:
    DATA_RAW = csv.reader(data_file, delimiter='\t')
    for row in DATA_RAW:
        try:
            x = np.array((float(row[0]), float(row[1]), float(row[2]), float(row[3])))
            d = float(row[4])
            eps_r = float(row[5])
            k = float(row[6])
            f = float(row[7])
            z = complex(float(row[8]), float(row[9]))
            # calculation of deviation between calculation and validated values
            Cost = pad.coupleur_cost(x, d, eps_r, k, f, z)
            # output creation Cost and sweept variables
            OUTPUT.append((Cost, x[2], x[1]))
        except ValueError:
            #importation error gestion
            print('line skip :'+str(row))
COST_RES = np.array(OUTPUT)

plt.plot(COST_RES[0:5, 1]*1e6, 100*COST_RES[0:5, 0], 'rx')
plt.plot(COST_RES[5:9, 1]*1e6, 100*COST_RES[5:9, 0], 'b+')
plt.legend(['n=2', 'n=1'])
plt.ylabel("Error (%)")
plt.xlabel("Inner Diameter (µm)")
plt.ylim(bottom=0)
plt.xlim(left=0)
plt.grid(True)
