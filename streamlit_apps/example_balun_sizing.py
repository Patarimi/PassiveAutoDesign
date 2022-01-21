import streamlit as st
import passive_auto_design.devices.balun as bln

MODEL_MAP_PATH = "./tests/default.map"

# Creation of an impedance transformer
BALUN_TST = bln.Balun(modelmapfile=MODEL_MAP_PATH)

# Design inputs
BALUN_TST.f_c = st.number_input("f_c (Hz)", value=18.e9)
BALUN_TST.z_src = st.number_input("Z_src (Real)", value=50.) + 1j * st.number_input("Z_src (Imag)", value=.1)
BALUN_TST.z_ld = st.number_input("Z_load (Real)", value=2.) + 1j * st.number_input("Z_load (Imag)", value=-11.)

# force symmetrical balun by altering load
if st.checkbox("enforce symmetrical balun"):
    BALUN_TST.enforce_symmetrical("load")
st.text(BALUN_TST.z_ld)
st.text(BALUN_TST.z_src)
RES2 = BALUN_TST.design()
st.write(BALUN_TST.print(RES2))

# Inductance of the primary and secondary inductors
LS_SYNTH = BALUN_TST.transfo.model["ls"]
LL_SYNTH = BALUN_TST.transfo.model["lp"]
