# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 15:58:12 2020

@author: mpoterea
"""
import csv
import numpy as np
import passive_auto_design.passive_component.coupler as cpl

with open('tests/coupleur_data.csv', newline='') as data_file:
    DATA_RAW = csv.reader(data_file, delimiter='\t')
    
    for row in DATA_RAW:
        try:
            if row[0]=='with':
                modelmap = row[1]
            else:
                x = {'width':float(row[0]), 'n_turn':float(row[1]), 'di':float(row[2]), 'gap':float(row[3])}
                k = float(row[4])
                f = float(row[5])
                z = complex(float(row[6]), float(row[7]))
                # calculation of deviation between calculation and validated values
                CPL = cpl.Coupler(f, z, k)
                CPL.transfo.set_primary(x)
                CPL.transfo.set_secondary(x)
                Cost = np.abs(S[0]-(50-z)/(z+50))
                # output creation Cost and sweept variables
                OUTPUT.append((Cost, x['di'], x['n_turn']))
        except ValueError:
            #importation error gestion
            if row[0]=='#W':
                pass
