# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: Patarimi

This Script is given as an example.
It describes how to define a substrate (or Back End Of Line)
and dump it in a .yml file
"""
import yaml
import streamlit as st
from hydralit import HydraHeadApp
import passive_auto_design.substrate as sub


class Substrate(HydraHeadApp):
    def run(self):
        # Definition of the substrate different layers
        BEOL = sub.Substrate()
        with st.form(key="substrate_definition"):
            st.text_input("Layer Name")
            st.number_input("Min. Width")
            st.number_input("Max. Width")
            submitted = st.form_submit_button("Add layer")

        BEOL.add_layer(sub.Layer("M_top", 3e-6, sub.COPPER, sub.SILICON_OXYDE))
        BEOL.sub[BEOL.get_index_of("M_top")].set_rules(2e-6, 20e-6, 2.1e-6)
        BEOL.add_layer(sub.Layer("Via", 3e-6, sub.COPPER, sub.SILICON_OXYDE))
        BEOL.add_layer(sub.Layer("M_bot", 3e-6, sub.COPPER, sub.SILICON_OXYDE))
        BEOL.sub[BEOL.get_index_of("M_bot")].set_rules(2e-6, 20e-6, 2.1e-6)
        BEOL.add_layer(sub.Layer("Inter", 9.54e-6, sub.COPPER, sub.SILICON_OXYDE))
        BEOL.add_layer(sub.Layer("gnd_plane", 3e-6, sub.COPPER, sub.SILICON_OXYDE))

        st.download_button("Get the layer map", export(BEOL), file_name="tech.yml")


@st.cache
def export(BEOL):
    return yaml.dump(BEOL.sub)
