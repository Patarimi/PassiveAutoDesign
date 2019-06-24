# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:27:56 2019
Feed validated values to Coupleur_Cost. Results should be close to zero.

@author: mpoterea
"""
# Comparison between EM simulation results and coupler_cost function results
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import PassiveAutoDesign as pad
import substrate as sub
import ngspice_warper as ng

OUTPUT = list()   #contains list of tuples (cost, param sweep for plotting)
# importation of reference data and cost calculation
with open('./test_set/coupleur_data.csv', newline='') as data_file:
    DATA_RAW = csv.reader(data_file, delimiter='\t')
    for row in DATA_RAW:
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
                with open('./cache/model_coupler.cir', 'w') as file:
                    file.write(CPL.transfo.generate_spice_model(k))
                S = ng.get_results(b_model+b_simulation)
                Cost = np.abs(S[0]-(50-z)/(z+50))
                # output creation Cost and sweept variables
                OUTPUT.append((Cost, x['di'], x['n_turn']))
        except ValueError:
            #importation error gestion
            if row[0]!='#W':
                print('line skip :'+str(row))
COST_RES = np.array(OUTPUT)

plt.figure()
plt.plot(COST_RES[0:5, 1]*1e6, 100*COST_RES[0:5, 0], 'rx')
plt.plot(COST_RES[5:9, 1]*1e6, 100*COST_RES[5:9, 0], 'b+')
plt.legend(['n=2', 'n=1'])
plt.ylabel("Error (%)")
plt.xlabel("Inner Diameter (µm)")
plt.ylim(bottom=0)
plt.xlim(left=0)
plt.grid(True)
TMP = list(100*COST_RES[:,0])
print(f'Typical Error\nmin:\t{np.min(TMP):2.1f}\nmed:\t{np.median(TMP):2.1f}\nmax:\t{np.max(TMP):2.1f}')

# %% drawing of the cost function versus di and W

W_TABLE = np.arange(3e-6, 10e-6, 0.1e-6)
DI_TABLE = np.arange(450e-6, 800e-6, 10e-6)
DI, W = np.meshgrid(DI_TABLE, W_TABLE)

COST_TOT = list()
for w in W_TABLE:
    COST_VS_DI = list()
    for di in DI_TABLE:
        CPL = pad.Coupler(BEOL, 5e9, 50)
        COST_VS_DI.append(CPL.cost([w, 1, di, 2.1e-6]))
    COST_TOT.append(COST_VS_DI)

FIG = plt.figure()
AX = FIG.add_subplot(111, projection='3d')
AX.plot_surface(DI*1e6, W*1e6, 100*(1-np.array(COST_TOT)), cmap=cm.coolwarm)
AX.set_zlabel("Ideality (%)")
AX.set_ylabel("Width (µm)")
AX.set_xlabel("Inner Diameter (µm)")
