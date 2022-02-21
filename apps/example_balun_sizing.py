import streamlit as st
from hydralit import HydraHeadApp
import passive_auto_design.devices.balun as bln
from passive_auto_design.unit import SI


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
