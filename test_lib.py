# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import ngspice_warper as ng
import os

if os.name == 'nt':
    REF_MODEL = 'Hybrid Coupler\n\n\
VIN\t\t3\t0\tDC\t0\tAC\t1\n\
RIN\t\t3\tIN\t50\nROUT\tOUT\t0\t50\n\
RCPL\tCPL\t0\t50\n\
RISO\tISO\t0\t50\n\nL1\t\tIN\t1\t1.000e-09\n\
R1\t\t1\tOUT\t5.000e-01\n\
L2\t\tCPL\t2\t1.000e-09\n\
R2\t\t2\tISO\t5.000e-01\nK\t\t\
L1\tL2\t0.9\n\
CG1\t\tIN\t0\t2.500e-16\n\
CG2\t\tOUT\t0\t2.500e-16\n\
CG3\t\tISO\t0\t2.500e-16\n\
CG4\t\tCPL\t0\t2.500e-16\n\
CM1\t\tIN\tCPL\t5.000e-16\n\
CM2\t\tISO\tOUT\t5.000e-16\n\n'
    REF_CTRL = '.AC LIN\t1\t1.000e+09\t1.000e+09\n\
.PRINT AC V(IN) I(VIN) V(OUT) V(CPL) V(ISO)\n\n\
.OPTION ELTOL=1e-12\n.END\n'
    def test_ngspice_warper():
        assert ng.generate_ac_simulation(1e9, 1e9, 1) == REF_CTRL
        S = ng.get_results(bytes(REF_MODEL+REF_CTRL, encoding='UTF-8'))
        assert (S == [-0.011917  -0.06115071j, 0.4940414 -0.030811j, 0.00345157+0.02766141j, -0.0034515 -0.0275043j]).all

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