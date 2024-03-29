import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import passive_auto_design.devices.taper as tap
from passive_auto_design.special import reflexion_coef
from passive_auto_design.units.physical_dimension import PhysicalDimension


N_STEP = st.number_input("Step Number", min_value=3, step=1, value=61)
Z_START = st.number_input("Starting Impedance", min_value=0.0, step=0.1, value=50.0)
Z_STOP = st.number_input("Ending Impedance", min_value=0.0, step=0.1, value=377.0)
E = 1.77  # USI
C_0 = 2.988e8  # m/s
TOT_LENGTH = (
    st.number_input("Total Length (mm)", min_value=0.0, step=0.1, value=10.0) * 1e-3
)

Z_LINEAR = tap.linear_taper(Z_START, Z_STOP, N_STEP)  # Ohm
Z_KLOPF = tap.klopfenstein_taper(Z_START, Z_STOP, N_STEP)  # Ohm
DELAY = np.sqrt(E) * TOT_LENGTH / (C_0 * N_STEP)  # s

F_SWEEP = np.arange(0, 50e9, 0.1e9)
GAMMA_LINEAR = PhysicalDimension(
    value=np.zeros(F_SWEEP.shape, dtype=complex), scale="lin", unit=""
)
GAMMA_KLOPF = PhysicalDimension(
    value=np.zeros(F_SWEEP.shape, dtype=complex), scale="lin", unit=""
)

for i in range(F_SWEEP.size):
    Phase = -DELAY * 2 * np.pi * F_SWEEP[i]
    GAMMA_LINEAR[i] = reflexion_coef(Z_LINEAR.value, Phase).value
    GAMMA_KLOPF[i] = reflexion_coef(Z_KLOPF.value, Phase).value

tap_prof = plt.figure()
plt.grid(True)
X_POS = np.linspace(-TOT_LENGTH / 2, TOT_LENGTH / 2, N_STEP)
plt.plot(X_POS, Z_LINEAR.value)
plt.plot(X_POS, Z_KLOPF.value)
plt.xlabel("Position (mm)")
plt.ylabel(r"Impedance ($\Omega$)")
plt.legend(["linear tapper", "klopfenstein tapper"])


freq_resp = plt.figure()
plt.grid(True)
plt.plot(F_SWEEP * 1e-9, GAMMA_LINEAR.dB().value)
plt.plot(F_SWEEP * 1e-9, GAMMA_KLOPF.dB().value)
plt.legend(["linear tapper", "klopfenstein tapper"])
plt.xlabel("Frequency (GHz)")
plt.ylabel("Return Loss (dB)")
col = st.columns(2)
col[0].pyplot(tap_prof)
col[1].pyplot(freq_resp)
