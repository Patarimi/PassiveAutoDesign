import streamlit as st
from hydralit import HydraHeadApp
import passive_auto_design.devices.balun as bln
from passive_auto_design.unit import Impedance, SI


class Balun(HydraHeadApp):
    def run(self):
        BALUN_TST = bln.Balun()
        # Design inputs
        with st.form(key="design_input"):
            col1, col2 = st.columns(2)
            BALUN_TST.f_c = (
                col1.number_input("Central Frequency (MHz)", value=60.0e3) * 1e6
            )
            BALUN_TST.k = col2.number_input("Coupling Factor", value=0.8)
            BALUN_TST.z_src = col1.number_input(
                "Source Impedance (Real)", value=100.0
            ) + 1j * col2.number_input("(Imag)", value=-300.0)
            BALUN_TST.z_ld = col1.number_input(
                "Load Impedance (Real)", value=50.0
            ) + 1j * col2.number_input("(Imag)", value=-100.0)
            force_sym = col1.checkbox("enforce symmetrical balun")
            dir_sym = col2.radio("by altering :", ("load", "source"))
            submitted = st.form_submit_button()
        if submitted:
            if force_sym:
                BALUN_TST.enforce_symmetrical(dir_sym)
            st.write("$Z_{load}$=" + Impedance(BALUN_TST.z_ld))
            st.write("$Z_{source}$=" + Impedance(BALUN_TST.z_src))
            Result = BALUN_TST.design()
            res_col = st.columns(2)
            res_col[0].subheader("First Solution")
            res_col[0].write(r"$L_{in}$=" + SI(Result[0][0]) + "H")
            res_col[0].write(r"$L_{out}$=" + SI(Result[1][0]) + "H")

            res_col[1].subheader("Second Solution")
            res_col[1].write(r"$L_{in}$=" + SI(Result[0][1]) + "H")
            res_col[1].write(r"$L_{out}$=" + SI(Result[1][1]) + "H")
