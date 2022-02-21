import streamlit as st
from hydralit import HydraHeadApp
from numpy import tan, pi
import passive_auto_design.devices.balun as bln
from passive_auto_design.unit import SI
from passive_auto_design.components.lumped_element import Inductor, Capacitor, Resistor


class Balun(HydraHeadApp):
    def run(self):
        # Design inputs
        col = st.columns([2, 1, 1])
        with col[0].form(key="design_input"):
            st.header("Design Parameters")
            f_c = st.number_input(
                "Central Frequency (Hz)", value=60.0e9, min_value=0.0, format="%e"
            )
            k = st.number_input("Coupling Factor", value=0.8)
            z_src = st.number_input(
                "Source Impedance (Real)", value=100.0
            ) + 1j * st.number_input("(Imag)", value=-300.0)
            z_ld = st.number_input(
                "Load Impedance (Real)", value=50.0
            ) + 1j * st.number_input("(Imag)", value=-100.0)
            force_sym = st.checkbox("enforce symmetrical balun")
            dir_sym = st.radio("by altering :", ("load", "source"))
            st.form_submit_button()

        BALUN_TST = bln.Balun(f_c, z_src, z_ld, k)
        if force_sym:
            X_add = BALUN_TST.enforce_symmetrical(dir_sym)
            if dir_sym == "load":
                result = BALUN_TST.design(XL_add=X_add)
            else:
                result = BALUN_TST.design(XS_add=X_add)
        else:
            result = BALUN_TST.design()
        col[1].subheader("First Solution")
        col[2].subheader("Second Solution")

        for i in (0, 1):
            col[i+1].write(r"$L_{in}$=" + SI(result[0][i]) + "H")
            col[i+1].write(r"$L_{out}$=" + SI(result[1][i]) + "H")
            if force_sym:
                if X_add[i] > 0:
                    message = (
                        "an inductor of " + SI(X_add[i] / (2 * 3.14 * f_c)) + "H"
                    )
                else:
                    message = (
                        "a condensator of "
                        + SI(-1 / (X_add[i] * 2 * 3.14 * f_c))
                        + "F"
                    )
                col[i+1].write(
                    "Please add " + message + " in series with the " + dir_sym + "."
                )

        col = st.columns([2, 1, 1])
        with col[0].form(key="Transformer Parameters"):
            st.header("Transformer Parameters")
            sol = st.radio(label="Choose the solution", options=("First solution", "Second solution"))
            sel = 0 if sol == "First solution" else 1
            n_turn = st.number_input(label="Turn number (first inductor)", min_value=1, step=1),\
                     st.number_input(label="Turn number (second inductor)", min_value=1, step=1)
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
            dist = (
                    st.number_input(label="Distance between inductor (µm)", value=0.15)
                    * 1e-6
            )
            r_square = st.number_input(label=r"Square Resistance (mOhm)", value=5.)*1e-3
            st.form_submit_button(label="Compute")

        width = width_min
        l_t = Inductor(n_turn=n_turn[0], width=width, gap=gap), Inductor(n_turn=n_turn[1], width=width, gap=gap)
        for i in range(4):
            l_t[0].set_x_with_y("d_i", "ind", result[0][sel])
            l_t[1].par["d_i"]  = l_t[0].par["d_i"]
            l_t[1].set_x_with_y("width", "ind", result[1][sel])

            res = list((0,1))
            cap = list((0,1))
            for k in (0, 1):
                d_i = l_t[k].par["d_i"]
                gap = l_t[k].par["gap"]
                w = l_t[k].par["width"]
                area = n_turn[k] * d_i * w
                cap[k] = Capacitor(area, dist, eps_r).par["cap"]
                length = 8*tan(pi/8)*n_turn[k]*(d_i+w/2 + (n_turn[k]-1)*(w+gap))
                res[k] = Resistor(w, length, r_square).par["res"]
            col[1].write(cap)
            col[2].write(res)
            BALUN_TST = bln.Balun(f_c, z_src / (z_src + 1j * 2 * pi *cap[0]), z_ld / (z_ld + 1j * 2 * pi *cap[1]), k)
            result = BALUN_TST.design(r_serie=res)

        col[1].header("First Inductor")
        col[2].header("Second Inductor")
        for k in (0, 1):
            col[k+1].write("New Inductance found: "+str(l_t[k]))
            col[k+1].write("Cap Para: "+SI(cap[k])+"F")
            col[k+1].write("Res Para: "+SI(res[k])+r"$\Omega$")
            col[k+1].write(r"$n_{turn}$= " + str(n_turn[k]))
            for key in {"width", "gap", "d_i"}:
                col[k+1].write(f"{key}: {SI(l_t[k].par[key])}m")