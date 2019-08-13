# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:53 2019

@author: mpoterea

This Script is given as an example.
It describes how to define a substrate (or Back End Of Line)
and dump it in a .yml file
"""
import passive_auto_design.substrate as sub
#Definition of the substrate different layers
BEOL = sub.Substrate()
BEOL.add_layer(sub.Layer('M_top', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.sub[BEOL.get_index_of('M_top')].set_rules(2e-6, 20e-6, 2.1e-6)
BEOL.add_layer(sub.Layer('Via', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('M_bot', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.sub[BEOL.get_index_of('M_bot')].set_rules(2e-6, 20e-6, 2.1e-6)
BEOL.add_layer(sub.Layer('Inter', 9.54e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.add_layer(sub.Layer('gnd_plane', 3e-6, sub.COPPER, sub.SILICON_OXYDE))
BEOL.dump('./tech.yml')
