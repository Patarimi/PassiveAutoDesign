import numpy as np
import streamlit as st
from hydralit import HydraHeadApp
import matplotlib.pyplot as plt
import passive_auto_design.devices.coupler as cpl
from passive_auto_design.unit import SI
from passive_auto_design.special import dB, gamma
from passive_auto_design.components.lumped_element import Inductor, Capacitor
from passive_auto_design.components.transformer import Transformer


class Coupler(HydraHeadApp):
    def run(self):
        # Design inputs
        col1, col2 = st.columns(2)
        with col1.form(key="design_input"):
            st.header("Design Parameters")
            f_c = st.number_input(
                "Central Frequency (Hz)", value=1.0e9, min_value=0.0, format="%e"
            )
            k = st.number_input(
                "Coupling Factor", value=0.707, min_value=0.0, max_value=1.0, step=0.001
            )
            z_c = st.number_input("Characteristic Impedance (Real)", value=50.0)
            st.form_submit_button(label="Compute")
        coupler = cpl.Coupler(f_c, z_c, k)
        col1.subheader("Solution")
        col1.write(r"$C_{eq}$=" + SI(coupler.c) + "F")
        col1.write(r"$L_{eq}$=" + SI(coupler.l) + "H")
        f_log = np.round(np.log10(f_c), 1)
        freq = np.logspace(f_log - 2, f_log + 2)

        z_eff = coupler.l * (2 * np.pi * freq * np.sqrt(1 - k ** 2))

        fig, ax = plt.subplots()
        ax.semilogx(freq, dB(gamma(z_eff, z_c)), label="Return Loss")
        ax.semilogx(freq, dB(1 - gamma(z_eff, z_c) ** 2), label="Transmission")
        ax.grid(True)
        col2.pyplot(fig, dpi=300)

        col1, col2 = st.columns(2)
        with col1.form(key="Transformer Parameters"):
            st.header("Transformer Parameters")
            n_turn = st.number_input(label="Turn number", min_value=1, step=1)
            width_min = (
                st.number_input(label="Width (µm)", value=3.0, min_value=0.0, step=0.01)
                * 1e-6
            )
            gap = (
                st.number_input(label="Gap (µm)", value=1.5, min_value=0.0, step=0.01)
                * 1e-6
            )
            st.header("Model Parameters")
            eps_r = st.number_input(label="Permittivity", value=4.0, min_value=0.0)
            dist = st.number_input(label="Distance between inductor (µm)", value=1.5)
            dist_g = st.number_input(label="Distance to the ground plane (µm)", value=3)
            st.form_submit_button(label="Compute")

        width = width_min
        l1 = Inductor(n_turn=n_turn, width=width, gap=gap)
        transfo = Transformer(
            l1, l1, rho=0, eps_r=eps_r, h_mut=dist * 1e-6, h_gnd=dist_g * 1e-6
        )
        for i in range(4):
            transfo.set_model_with_dim({"lp": coupler.l}, "lp.d_i")
            d_i = transfo.dim["lp.d_i"]
            ratio = transfo.model["cm"]/transfo.model["cg"]
            width = transfo.dim["lp.width"]
            transfo.set_model_with_dim({"cm": ratio*coupler.c/(1+ratio),
                                        "cg": coupler.c/(1+ratio)},
                                       "lp.width")
            delta = np.abs(width - transfo.dim["lp.width"]) / width
            l1 = Inductor(n_turn=n_turn, width=transfo.dim["lp.width"], gap=gap, d_i=d_i)
            transfo = Transformer(
                l1, l1, rho=0, eps_r=eps_r, h_mut=dist * 1e-6, h_gnd=dist_g * 1e-6
            )
            if delta < 0.001:
                break
        col2.header("Geometrical Sizing")
        col2.write(r"$l_{find}$ = " + str(l1))
        col2.write(r"$c_{mut}$ = " + str(transfo.model["cm"]))
        col2.write(r"$c_{gnd}$ = "+str(transfo.model["cg"]))
        col2.write(r"$n_{turn}$= " + str(n_turn))
        for key in {"width", "gap", "d_i"}:
            col2.write(f"{key}: {SI(transfo.dim['lp.'+key])}m")
