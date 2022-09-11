# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:47:26 2019

@author: Patarimi
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from passive_auto_design.substrate import AIR, COPPER, D5880, D6002
import passive_auto_design.components.waveguide as wg

# Specifications
conf, graph = st.tabs(["Config", "Graph"])
with conf:
    c1, c2 = st.columns(2)
    with c1:
        st.title("Graph Settings")
        F_MIN = st.number_input("f_min (Hz)", step=1.e6, min_value=0., value=27.e9)  # Hz
        F_MAX = st.number_input("f_max (Hz)", step=1.e6, min_value=0., value=31e9)  # Hz
        STEP = st.number_input("f_step (Hz)", step=1.e6, min_value=0., value=0.5e9)  # Hz
    with c2:
        st.title("Waveguide Config")
        FC10 = st.number_input("fc10 (Hz)", step=1e6, min_value=0., value=F_MIN/1.25)  # Hz

# creation of the guides in SIW
SIW_5880 = wg.Waveguide(COPPER, D5880, 0.508e-3)
SIW_5880.first_cut_off = FC10
st.title("Size")
st.write(SIW_5880.print_info())

SIW_6002 = wg.Waveguide(COPPER, D6002, 0.508e-3)
SIW_6002.first_cut_off = FC10
st.write(SIW_6002.print_info())

# determination de la largeur du AF-SIW avec une fréquence de coupure à fc10/1.25
SIW_AIR = wg.AF_SIW(COPPER, AIR, 1.6e-3, 0.508e-3)
SIW_AIR.first_cut_off = FC10
st.write(SIW_AIR.print_info())

# %% calcul des pertes dans les guides
#   Dielectric Loss
FREQ = np.linspace(F_MIN, F_MAX, int(1 + (F_MAX - F_MIN) / STEP))
AD_5880 = SIW_5880.calc_a_d(FREQ)
AD_6002 = SIW_6002.calc_a_d(FREQ)

first = plt.figure()
plt.subplot(221)
plt.plot(FREQ * 1e-9, AD_5880, "r--")
plt.plot(FREQ * 1e-9, AD_6002, "b--")
plt.grid(visible=True)
plt.ylabel("Dielectric Loss (dB/cm)")
plt.xlabel("Frequency (GHz)")
plt.legend(["Rogers 5880-filled SIW", "Rogers 6002-filled SIW"])
plt.ylim(bottom=0)

# %%   Ohmic Loss
AC_5880 = SIW_5880.calc_a_c(FREQ)
AC_6002 = SIW_6002.calc_a_c(FREQ)
AC_AIR = SIW_AIR.calc_a_c(FREQ)

plt.subplot(222)
plt.plot(FREQ * 1e-9, AC_AIR, "g--")
plt.plot(FREQ * 1e-9, AC_5880, "r--")
plt.plot(FREQ * 1e-9, AC_6002, "b--")
plt.grid(visible=True)
plt.ylabel("Resistive Loss (dB/cm)")
plt.xlabel("Frequency (GHz)")
plt.legend(
    ["Rogers 6002-based AF-SIW", "Rogers 5880-filled SIW", "Rogers 6002-filled SIW"]
)
plt.ylim(bottom=0)

# %%   Roughness Loss
KSR = SIW_5880.calc_ksr(FREQ)
KSR2 = SIW_AIR.calc_ksr(FREQ)

plt.subplot(223)
plt.plot(FREQ * 1e-9, AC_AIR * KSR2, "g--")
plt.plot(FREQ * 1e-9, AC_5880 * KSR, "r--")
plt.plot(FREQ * 1e-9, AC_6002 * KSR, "b--")
plt.grid(visible=True)
plt.ylabel("Roughness Loss (dB/cm)")
plt.xlabel("Frequency (GHz)")
plt.legend(
    ["Rogers 6002-based AF-SIW", "Rogers 5880-filled SIW", "Rogers 6002-filled SIW"]
)
plt.ylim(bottom=0)

#   Total loss
plt.subplot(224)
plt.plot(FREQ * 1e-9, (1 + KSR2) * AC_AIR, "g--")
plt.plot(FREQ * 1e-9, ((1 + KSR) * AC_5880 + AD_5880), "r--")
plt.plot(FREQ * 1e-9, ((1 + KSR) * AC_6002 + AD_6002), "b--")
plt.grid(visible=True)
plt.ylabel("Total Loss (dB/cm)")
plt.xlabel("Frequency (GHz)")
plt.legend(
    ["Rogers 6002-based AF-SIW", "Rogers 5880-filled SIW", "Rogers 6002-filled SIW"]
)
plt.ylim(bottom=0)

# %% calcul of average power handling capability
Tg_Rogers_5880 = 260 + 273.15
Tg_Rogers_6002 = 350 + 273.15

APHC_AF_SIW = SIW_AIR.calc_aphc(FREQ, Tg_Rogers_6002)
APHC_5880_SIW = SIW_5880.calc_aphc(FREQ, Tg_Rogers_5880)
APHC_6002_SIW = SIW_6002.calc_aphc(FREQ, Tg_Rogers_6002)

sec = plt.figure()
plt.semilogy(FREQ * 1e-9, APHC_AF_SIW, "g")
plt.semilogy(FREQ * 1e-9, APHC_5880_SIW, "r")
plt.semilogy(FREQ * 1e-9, APHC_6002_SIW, "b")
plt.grid(visible=True, which="major")
plt.grid(visible=True, which="minor", linestyle="--")
plt.ylabel("APHC (W)")
plt.ylim(1e1, 1e4)
plt.xlabel("Frequency (GHz)")
plt.legend(
    ["Rogers 6002-based AF-SIW", "Rogers 5880-filled SIW", "Rogers 6002-filled SIW"]
)


# %% calcul du peak power handling capability

PPHC_AF_SIW = SIW_AIR.calc_pphc(FREQ, 36e5)
PPHC_5880_SIW = SIW_5880.calc_pphc(FREQ, 360e5)
PPHC_6002_SIW = SIW_6002.calc_pphc(FREQ, 239e5)

third = plt.figure()
plt.semilogy(FREQ * 1e-9, PPHC_AF_SIW * 1e-3, "g")
plt.semilogy(FREQ * 1e-9, PPHC_5880_SIW * 1e-3, "r")
plt.semilogy(FREQ * 1e-9, PPHC_6002_SIW * 1e-3, "b")
plt.grid(visible=True, which="major")
plt.grid(visible=True, which="minor", linestyle="--")
plt.ylabel("PPHC (kW)")
plt.ylim(1e1, 1e4)
plt.xlabel("Frequency (GHz)")
plt.legend(
    ["Rogers 6002-based AF-SIW", "Rogers 5880-filled SIW", "Rogers 6002-filled SIW"]
)

with graph:
    st.pyplot(first)
    c1, c2 = st.columns(2)
    c1.pyplot(sec)
    c2.pyplot(third)
