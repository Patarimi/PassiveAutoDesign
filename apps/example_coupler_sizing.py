import numpy as np
import streamlit as st
from hydralit import HydraHeadApp
import matplotlib.pyplot as plt
import passive_auto_design.devices.coupler as cpl
from passive_auto_design.unit import SI
from passive_auto_design.special import dB, gamma
from passive_auto_design.components.lumped_element import Inductor


class Coupler(HydraHeadApp):
    def run(self):
        # Design inputs
        col1, col2 = st.columns(2)
        with col1.form(key="design_input"):
            st.header("Input Parameters")
            f_c = st.number_input(
                "Central Frequency (Hz)", value=1.0e9, min_value=0.0, format="%e"
            )
            k = st.number_input(
                "Coupling Factor", value=0.707, min_value=0.0, max_value=1.0, step=0.001
            )
            z_c = st.number_input("Characteristic Impedance (Real)", value=50.0)
            submitted = st.form_submit_button(label="Compute")
        coupler = cpl.Coupler(f_c, z_c, k)
        if submitted:
            col1.subheader("Solution")
            col1.write(r"$C_{eq}$=" + SI(coupler.c) + "F")
            col1.write(r"$L_{eq}$=" + SI(coupler.l) + "H")
            f_log = np.round(np.log10(f_c), 1)
            freq = np.logspace(f_log - 2, f_log + 2)

            z_eff = coupler.l * (2 * np.pi * freq * np.sqrt(1 - k ** 2))

            fig, ax = plt.subplots()
            ax.semilogx(freq, dB(gamma(z_eff, z_c)), label="Return Loss")
            ax.semilogx(freq, dB(1-gamma(z_eff, z_c)**2), label="Transmission")
            ax.legend()
            col2.pyplot(fig, dpi=300)

        with col1.form(key="Transformer Parameters"):
            st.header("Transformer Parameters")
            n_turn = st.number_input(label="turn number", min_value=1, step=1)
            width = st.number_input(label="width (µm)", value=3., min_value=0., step=0.01)
            gap = st.number_input(label="gap (µm)", value=1.5, min_value=0., step=0.01)
            submit2 = st.form_submit_button(label="Compute")

        if submit2:
            l1 = Inductor(n_turn=n_turn, width=width*1e-6, gap=gap*1e-6)
            l1.set_x_with_y("d_i", "ind", coupler.l)

            col1.write(l1.par)
