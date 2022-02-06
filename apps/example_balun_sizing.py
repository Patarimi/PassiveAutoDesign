import streamlit as st
from hydralit import HydraHeadApp
import passive_auto_design.devices.balun as bln
from passive_auto_design.unit import SI


class Balun(HydraHeadApp):
    def run(self):
        # Design inputs
        with st.form(key="design_input"):
            col1, col2 = st.columns(2)
            f_c = col1.number_input(
                "Central Frequency (Hz)", value=60.0e9, min_value=0.0, format="%e"
            )
            k = col2.number_input("Coupling Factor", value=0.8)
            z_src = col1.number_input(
                "Source Impedance (Real)", value=100.0
            ) + 1j * col2.number_input("(Imag)", value=-300.0)
            z_ld = col1.number_input(
                "Load Impedance (Real)", value=50.0
            ) + 1j * col2.number_input("(Imag)", value=-100.0)
            force_sym = col1.checkbox("enforce symmetrical balun")
            dir_sym = col2.radio("by altering :", ("load", "source"))
            submitted = st.form_submit_button()
        if submitted:
            BALUN_TST = bln.Balun(f_c, z_src, z_ld, k)
            if force_sym:
                X_add = BALUN_TST.enforce_symmetrical(dir_sym)
                if dir_sym == "load":
                    result = BALUN_TST.design(XL_add=X_add)
                else:
                    result = BALUN_TST.design(XS_add=X_add)
            else:
                result = BALUN_TST.design()
            res_col = st.columns(2)
            res_col[0].subheader("First Solution")
            res_col[1].subheader("Second Solution")

            for i in (0, 1):
                res_col[i].write(r"$L_{in}$=" + SI(result[0][i]) + "H")
                res_col[i].write(r"$L_{out}$=" + SI(result[1][i]) + "H")
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
                    res_col[i].write(
                        "Please add " + message + " in series with the " + dir_sym + "."
                    )
