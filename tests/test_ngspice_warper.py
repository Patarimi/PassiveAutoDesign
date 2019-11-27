# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import passive_auto_design.ngspice_warper as ng
import numpy as np

REF_MODEL = 'Hybrid Coupler\n\n\
L1\t\tIN\t1\t1.000e-09\n\
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

REF_CTRL = '\n\nVIN\tMID_SONDE\t0\tDC\t0\tAC\t1\t0\n\
RIN\tIN\tMID_SONDE\t50.0\nROUT\tOUT\t0\t50.0\n\
RCPL\tCPL\t0\t50.0\n\
RISO\tISO\t0\t50.0\n\n\
.AC LIN\t1\t1.0G\t1.0G\n\
.PRINT AC V(IN) I(VIN) V(OUT) V(CPL) V(ISO)\n\n\
.OPTION ELTOL=1e-12\n.END\n'
S_REF_AC = [[-0.1*1j], [0.5], [0.0], [0.0]]
S_REF_SP = [[-0.1*1j, 0.5, 0.0, 0.0],
            [0.5, -0.1*1j, 0.0, 0.0],
            [0.0, 0.0, -0.1*1j, 0.5],
            [0.0, 0.0, 0.5, -0.1*1j]]
PORTS = (ng.Ports('IN', name='IN'),
         ng.Ports('OUT', name='OUT'),
         ng.Ports('CPL', name='CPL'),
         ng.Ports('ISO', name='ISO'))
FREQ_CTRL = (1e9, 1e9, 1)
def test_ngspice_warper():
    assert ng.generate_ac_simulation(FREQ_CTRL, PORTS) == REF_CTRL
    ng.set_path("../ng_spice/")
    ac_res = ng.run_ac_sim(REF_MODEL,
                           ports=PORTS,
                           freq_ctrl=FREQ_CTRL,
                           _dump_results=True)
    assert (np.round(ac_res, 1) == S_REF_AC).all()
    sp_res = ng.run_sp_sim(REF_MODEL,
                           ports=PORTS,
                           freq_ctrl=FREQ_CTRL)
    assert (np.round(sp_res, 1) == S_REF_SP).all()
    with pytest.raises(FileNotFoundError):
        ng.set_path("foo")
    ng.set_path("../")
    with pytest.raises(FileNotFoundError):
        ng.run_ac_sim(REF_MODEL,
                      ports=[],
                      freq_ctrl=FREQ_CTRL)
    with pytest.raises(ValueError):
        ng.run_sp_sim(REF_MODEL,
                      ports=[],
                      freq_ctrl=FREQ_CTRL)
