# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import substrate as sb
def test_substrate():
    SUB = sb.Substrate()
    M_LYR = sb.Layer('m_bott', 0.1e-3, sb.COPPER, sb.AIR)
    M_LYR.set_rules(0.508e-3, 10e-3, 0.508e-3)
    D_LYR = sb.Layer('core', 0.8e-3, sb.COPPER, sb.D5880)
    D_LYR.set_rules(0.508e-3, 10e-3, 0.508e-3)
    SUB.add_layer(M_LYR)
    SUB.add_layer(D_LYR)
    SUB.add_layer(M_LYR)
    SUB.dump('cache/tech.yml')
    SUB.load('cache/tech.yml')
    assert SUB.get_index_of('m_bott') == 0