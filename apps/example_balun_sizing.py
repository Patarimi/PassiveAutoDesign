import streamlit as st
import passive_auto_design.devices.balun as bln
from hydralit import HydraHeadApp


class Balun(HydraHeadApp):
    def run(self):
        uploaded_file = st.file_uploader("Substrate File")
        if uploaded_file is not None:
            # Creation of an impedance transformer
            BALUN_TST = bln.Balun(modelmapfile=uploaded_file)
        else:
            BALUN_TST = bln.Balun(modelmapfile="./tests/default.map")

        # Design inputs
        with st.form(key="design_input"):
            BALUN_TST.f_c = st.number_input("f_c (Hz)", value=18.0e9)
            col1, col2 = st.columns(2)
            BALUN_TST.z_src = col1.number_input(
                "Z_src (Real)", value=50.0
            ) + 1j * col2.number_input("Z_src (Imag)", value=-0.1)
            BALUN_TST.z_ld = col1.number_input(
                "Z_load (Real)", value=2.0
            ) + 1j * col2.number_input("Z_load (Imag)", value=-11.0)

            # force symmetrical balun by altering load
            if st.checkbox("enforce symmetrical balun"):
                BALUN_TST.enforce_symmetrical("load")
            submitted = st.form_submit_button()

            if submitted:
                st.text(BALUN_TST.z_ld)
                st.text(BALUN_TST.z_src)
                RES2 = BALUN_TST.design()
                st.text(BALUN_TST.print(RES2))

                # Inductance of the primary and secondary inductors
                BALUN_TST.transfo.model["ls"]
                BALUN_TST.transfo.model["lp"]
