# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import numpy as np
import matplotlib.pyplot as plt
import passive_auto_design.components.taper as tap
from passive_auto_design.special import dB, reflexion_coef

N_STEP = 61
Z_START = 50
Z_STOP = 377
E = 1.77  # USI
C_0 = 2.988e8  # m/s
TOT_LENGTH = 10e-3  # m

Z_LINEAR = tap.linear_taper(Z_START, Z_STOP, N_STEP)  # Ohm
Z_KLOPF = tap.klopfenstein_taper(Z_START, Z_STOP, N_STEP)  # Ohm
DELAY = np.sqrt(E) * TOT_LENGTH / (C_0 * N_STEP)  # s

F_SWEEP = np.arange(0, 50e9, 0.1e9)
GAMMA_LINEAR = np.zeros(F_SWEEP.shape, dtype=complex)
GAMMA_KLOPF = np.zeros(F_SWEEP.shape, dtype=complex)
for i in range(F_SWEEP.size):
    Phase = -DELAY * 2 * np.pi * F_SWEEP[i]
    GAMMA_LINEAR[i] = reflexion_coef(Z_LINEAR, Phase)
    GAMMA_KLOPF[i] = reflexion_coef(Z_KLOPF, Phase)

plt.figure()
plt.grid(True)
X_POS = np.linspace(-TOT_LENGTH/2, TOT_LENGTH/2, N_STEP)
plt.plot(X_POS, Z_LINEAR)
plt.plot(X_POS, Z_KLOPF)
plt.xlabel("Frequency (GHz)")
plt.ylabel(r"Impedance ($\Omega$)")
plt.legend(['linear tapper', 'klopfenstein tapper'])

plt.figure()
plt.grid(True)
plt.plot(F_SWEEP*1e-9, dB(GAMMA_LINEAR))
plt.plot(F_SWEEP*1e-9, dB(GAMMA_KLOPF))
plt.legend(['linear tapper', 'klopfenstein tapper'])
plt.xlabel("Frequency (GHz)")
plt.ylabel("Return Loss (dB)")
