# -*- coding: utf-8 -*-
"""
Created on Mon May 13 17:27:56 2019
Feed validated values to Coupleur_Cost. Results should be close to zero.

@author: Patarimi
"""
# %% Comparison between EM simulation results and coupler_cost function results
# The cost function should as close as possible to zero.
import csv
import numpy as np
import matplotlib.pyplot as plt
import passive_auto_design.components.coupler as cpl

OUTPUT = list()  # contains list of tuples (cost, param sweep for plotting)
# importation of reference data and cost calculation
with open("tests/coupleur_data.csv", newline="") as data_file:
    DATA_RAW = csv.reader(data_file, delimiter="\t")
    for row in DATA_RAW:
        try:
            if row[0] == "with":
                model_map = row[1]
            else:
                x = {
                    "width": float(row[0]),
                    "n_turn": float(row[1]),
                    "di": float(row[2]),
                    "gap": float(row[3]),
                }
                f = float(row[5])
                z = complex(float(row[6]), float(row[7]))
                # calculation of deviation between calculation and validated values
                CPL = cpl.Coupler(f, z)
                CPL.transfo.set_primary(x)
                CPL.transfo.set_secondary(x)
                Zp = CPL.transfo.circuit.network.z[0]
                Cost = np.abs((Zp[0, 0] - z) / (Zp[0, 0] + z))
                # output creation Cost and swept variables
                OUTPUT.append((Cost, x["di"], x["n_turn"]))
        except ValueError:
            # importation error gestion
            if row[0] == "#W":
                pass
COST_RES = np.array(OUTPUT)
ERROR = list(100 * COST_RES[:, 0])

plt.figure()
plt.plot(COST_RES[0:5, 1] * 1e6, 100 * COST_RES[0:5, 0], "rx")
plt.plot(COST_RES[5:9, 1] * 1e6, 100 * COST_RES[5:9, 0], "b+")
plt.legend(["n=2", "n=1"])
plt.ylabel("Error (%)")
plt.xlabel("Inner Diameter (µm)")
plt.ylim(bottom=0)
plt.xlim(left=0)
plt.grid(True)
print(
    f"Typical Error\
      \nmin:\t{np.min(ERROR):2.1f}\
          \nmed:\t{np.median(ERROR):2.2f}\
              \nmax:\t{np.max(ERROR):2.1f}"
)
assert np.median(ERROR) <= 39
assert np.max(ERROR) <= 63
