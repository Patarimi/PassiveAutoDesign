# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: mpoterea
"""
import pytest
import passive_auto_design.ngspice_warper as ng
import numpy as np

REF_MODEL = 'Hybrid Coupler\n\n\
L1\t\tIN\tOUT\t1.0n\n\n\
L2\t\tCPL\tISO\t1.0n\n\
K\t\tL1\tL2\t0.9\n\
CG1\t\tIN\t0\t0.25f\n\
CG2\t\tOUT\t0\t0.25f\n\
CG3\t\tISO\t0\t0.25f\n\
CG4\t\tCPL\t0\t0.25f\n\
CM1\t\tIN\tCPL\t0.5f\n\
CM2\t\tISO\tOUT\t0.5f\n\n'

REF_CTRL = '\n\nVIN\tMID_SONDE\t0\tDC\t0\tAC\t1\t0.0\n\
RIN\tIN\tMID_SONDE\t50.0\nROUT_0\tOUT\t0\t50.0\n\
RCPL\tCPL\t0\t50.0\n\
RISO\tISO\t0\t50.0\n\n\
.AC LIN\t1\t1.0G\t1.0G\n\
.PRINT AC V(IN) I(VIN) V(OUT) V(CPL) V(ISO)\n\n\
.OPTION ELTOL=1e-12\n.END\n'
S_REF_AC = [0.1*1j, 1-0.1*1j, 0.1*1j, -0.1*1j]
S_REF_SP = [[0.1*1j,   1-0.1*1j,   0.1*1j,  -0.1*1j],
            [1-0.1*1j,   0.1*1j,  -0.1*1j,   0.1*1j],
            [0.1*1j,    -0.1*1j,   0.1*1j, 1-0.1*1j],
            [-0.1*1j,    0.1*1j, 1-0.1*1j,   0.1*1j]]
PORTS = (ng.Ports('IN', name='IN'),
         ng.Ports('OUT'),
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
    assert (np.round(ac_res[:,0], 1) == S_REF_AC).all()
    sp_res = ng.run_sp_sim(REF_MODEL,
                           ports=PORTS,
                           freq_ctrl=FREQ_CTRL)
    assert (np.round(sp_res[:,:,0], 1) == S_REF_SP).all()
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

def test_circuit():
    cir = ng.Circuit('foo')
    cir.add_v_source(0, 'in')

def test_other():
    assert ng.float2engineer(1e-16) == '0.1f'
