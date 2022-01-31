"""
    Space_mapping module implementation example

"""
import streamlit as st
from hydralit import HydraHeadApp
from passive_auto_design.space_mapping import space_map
from passive_auto_design.special import eps0
import passive_auto_design.components.lumped_element as lp


class SpaceMap(HydraHeadApp):
    def run(self):
        st.header("Space mapping example : Optimisation of a capacitor parasitic resistor")

        st.write("Definition of the goal (or target)")
        with st.echo():
            goal = {"C": 800e-12, "R": (0, 1)}

        st.write("List of the parameters use by the component model.")
        with st.echo():
            par0 = {"rho/h": 1e-6, "eps/d": 3}

        st.write("List of the dimensions of the component.")
        with st.echo():
            dim0 = {"l": 1e-3, "w": 1e-6}

        st.write("Definition of the coarse model.")
        with st.echo():
            def coarse_model(dim, par):
                cap = lp.Capacitor(area=dim["w"] * dim["l"], dist=1, eps_r=par["eps/d"])
                res = lp.Resistor(section=dim["w"], length=dim["l"], rho=par["rho/h"])
                achieved = {
                    "C": cap.par["cap"],
                    "R": res.par["res"],
                }
                return achieved # should contain all the keys of the goal

        st.write("Definition of the fine model.")
        with st.echo():
            def fine_model(dim):
                achieved = {
                    "C": eps0 * 5 * dim["w"] * dim["l"],
                    "R": 0.2 * dim["l"] / dim["w"],
                }
                return achieved # should contain all the keys of the goal

        with st.echo():
            dim_f, par_f, goal_f = space_map(coarse_model, dim0, fine_model, par0, goal)

        st.write("Final value of the capacitor.")
        st.json(dim_f)
