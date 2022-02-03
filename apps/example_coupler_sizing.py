import streamlit as st
from hydralit import HydraHeadApp
from numpy import imag
import passive_auto_design.devices.coupler as cpl
from passive_auto_design.unit import SI


class Coupler(HydraHeadApp):
    def run(self):
        # Design inputs
        with st.form(key="design_input"):
            col1, col2 = st.columns(2)
            f_c = col1.number_input(
                "Central Frequency (Hz)", value=1.0e9, min_value=0.0, format="%e"
            )
            k = col2.number_input(
                "Coupling Factor", value=0.707, min_value=0.0, max_value=1.0, step=0.001
            )
            z_c = col1.number_input("Characteristic Impedance (Real)", value=50.0)
            submitted = st.form_submit_button()
        if submitted:
            coupler = cpl.Coupler(f_c, z_c, k)
            st.subheader("Solution")
            st.write(r"$C_{eq}$=" + SI(coupler.c) + "F")
            st.write(r"$L_{eq}$=" + SI(coupler.l) + "H")
