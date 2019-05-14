# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:27:56 2019
Feed validated values to Coupleur_Cost. Results should be close to zero.

@author: mpoterea
"""

import numpy as np
import matplotlib.pyplot as plt
import PassiveAutoDesign as pad
import csv

Cost = list()   #contains deviation between calculation and validated values
f = list()      #reference frequency (for investigation, plot drawing purpose)
z = list()      #reference impedanc (id.)

with open('./test_set/coupleur_data.csv', newline='') as data_file:
    data_raw = csv.reader(data_file, delimiter='\t')
    for row in data_raw:
        try:
            x = np.array((float(row[0]), float(row[1]), float(row[2]), float(row[3])))
            d = float(row[4])
            eps_r = float(row[5])
            k = float(row[6])
            f.append(float(row[7]))
            z.append(complex(float(row[8]), float(row[9])))
            Cost.append(pad.Coupleur_Cost(x, d, eps_r, k, float(row[7]), complex(float(row[8]), float(row[9]))))
        except:
            print('line skip :'+str(row))
Cost_res = np.array(Cost)
f_ref = np.array(f)
z_ref = np.array(z)

plt.subplot(121)
plt.plot(f_ref*1e-9, 100*Cost_res, 'rx')
plt.ylabel("Error (%)")
plt.xlabel("Frequency (GHz)")

plt.subplot(122)
plt.plot(np.abs(z_ref), 100*Cost_res, 'rx')
plt.ylabel("Error (%)")
plt.xlabel('Impedance (Omega)')