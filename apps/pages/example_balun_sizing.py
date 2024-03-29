import streamlit as st
from numpy import pi
import passive_auto_design.devices.balun as bln
from passive_auto_design.units.unit import SI, Impedance
from passive_auto_design.components.inductor import Inductor
from passive_auto_design.components.transformer import Transformer

# Design inputs
conf, geom, param = st.tabs(["Design Inputs", "Geometry Configuration", "Solutions"])
with conf.form(key="design_input"):
    f_c = st.number_input(
        "Central Frequency (Hz)", value=60.0e9, min_value=0.0, format="%e"
    )
    k = st.number_input("Coupling Factor", value=0.8)
    z_src = st.number_input(
        "Source Impedance (Real)", value=100.0
    ) + 1j * st.number_input("(Imag)", value=-300.0)
    z_ld = st.number_input("Load Impedance (Real)", value=50.0) + 1j * st.number_input(
        "(Imag)", value=-100.0
    )
    force_sym = st.checkbox("enforce symmetrical balun")
    dir_sym = st.radio("by altering :", ("load", "source"))
    st.form_submit_button()

balun = bln.Balun(f_c, z_src, z_ld, k)
if force_sym:
    x_add = balun.enforce_symmetrical(dir_sym)
    if dir_sym == "load":
        result = balun.design(XL_add=x_add)
    else:
        result = balun.design(XS_add=x_add)
else:
    result = balun.design()

col = geom.columns(2)
col[0].subheader("First Solution")
col[1].subheader("Second Solution")

for i in (0, 1):
    col[i].write(r"$L_{in}$=" + SI(result[0][i]) + "H")
    col[i].write(r"$L_{out}$=" + SI(result[1][i]) + "H")
    if force_sym:
        if x_add[i] > 0:
            message = "an inductor of " + SI(x_add[i] / (2 * 3.14 * f_c)) + "H"
        else:
            message = "a capacitor of " + SI(-1 / (x_add[i] * 2 * 3.14 * f_c)) + "F"
        col[i].write("Please add " + message + " in series with the " + dir_sym + ".")

with geom.form(key="Transformer Parameters"):
    st.header("Transformer Parameters")
    sol = st.radio(
        label="Choose the solution",
        options=("First solution", "Second solution"),
    )
    sel = 0 if sol == "First solution" else 1
    cform = st.columns(2)
    cform[0].subheader("First Inductor")
    l_t = list((0, 1))
    for i in (0, 1):
        if i == 1:
            cform[1].subheader("Second Inductor")
        n_turn = cform[i].number_input(
            label="Turn number", min_value=1, step=1, key=f"nt{i}"
        )
        width = cform[i].number_input(
            label="Width (µm)",
            value=3.0,
            min_value=0.0,
            step=0.01,
            key=f"width{i}",
        )
        gap = cform[i].number_input(
            label="Gap (µm)", value=1.5, min_value=0.0, step=0.01, key=f"gap{i}"
        )
        l_t[i] = Inductor(n_turn=n_turn, width=width * 1e-6, gap=gap * 1e-6)
    st.header("Model Parameters")
    eps_r = st.number_input(label="Permittivity", value=4.0, min_value=0.0)
    dist = st.number_input(label="Height between inductor (µm)", value=0.15)
    dist_g = st.number_input(label="Height to the ground plane (µm)", value=0.15)
    r_square = st.number_input(label=r"Square Resistance (mOhm)", value=5.0)
    transfo = Transformer(
        l_t[0], l_t[1], r_square * 1e-3, eps_r, dist * 1e-6, dist_g * 1e-6
    )
    st.form_submit_button(label="Compute")

transfo.set_model_with_dim({"lp": result[0][sel]}, "lp.d_i")
transfo.set_model_with_dim({"ls": result[1][sel]}, "ls.d_i")
cap = transfo.model["cm"] / 2
geom = (transfo.model["rp"], transfo.model["rs"])
new_z_ld = z_ld / (1 + z_ld * 1j * 2 * pi * cap * f_c) + geom[1]
new_z_src = z_src / (1 + z_src * 1j * 2 * pi * cap * f_c) + geom[0]
balun = bln.Balun(f_c, new_z_src, new_z_ld, k)
balun.design(r_serie=geom)

col = param.columns(2)
col[0].write(r"New $Z_{load}$: " + Impedance(new_z_ld))
col[1].write(r"New $Z_{source}$: " + Impedance(new_z_src))
col[0].header("First Inductor")
col[1].header("Second Inductor")
for k in (0, 1):
    side = "lp" if k == 0 else "ls"
    col[k].write("New Inductance found: " + SI(transfo.model[side]) + "H")
    col[k].write("Cap Para: " + SI(cap) + "F")
    col[k].write("Res Para: " + SI(geom[k]) + r"$\Omega$")
    col[k].write(r"$n_{turn}$= " + str(transfo.dim[side + ".n_turn"]))
    for key in {"width", "gap", "d_i"}:
        col[k].write(f"${key}$: {SI(transfo.dim[side+'.'+key])}m")
