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
import passive_auto_design.substrate as sub


@st.cache
def export(substrate):
    return yaml.dump(substrate.sub)

# Definition of the substrate different layers
substrate = sub.Substrate()
st.write(substrate.sub)
with st.form(key="substrate_definition"):
    col = st.columns(4)
    layer_name = col[0].text_input("Layer Name")
    min_w = col[1].number_input("Min. Width (µm)")
    max_w = col[2].number_input("Max. Width (µm)")
    gap = col[3].number_input("Gap between track (µm)")
    submitted = st.form_submit_button("Add layer")

if submitted:
    substrate.add_layer(sub.Layer(layer_name, 3e-6, sub.COPPER, sub.SILICON_OXYDE))
    substrate.sub[substrate.get_index_of(layer_name)].set_rules(min_w, max_w, gap)

st.download_button("Get the layer map", export(substrate), file_name="tech.yml")
