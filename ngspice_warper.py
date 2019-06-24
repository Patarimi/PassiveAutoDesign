# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:30:07 2019

@author: mpoterea
"""

from subprocess import Popen, PIPE
import numpy as np

PATH = "C:/Users/mpoterea/Documents/PassiveAutoDesign/"
FILE_NAME = "cache/model_ind.cir"
EXE_NAME = "tierce_parts/ngspice_con.exe"

def generate_ac_simulation(f_start, f_stop, n_step):
    """
        generate an AC simulation with n_step linear steps between f_start and f_stop
    """
    return f'.AC LIN	{n_step}	{f_start:.3e}	{f_stop:.3e}\n\
.PRINT AC V(IN) I(VIN) V(OUT) V(CPL) V(ISO)\n\n\
.OPTION ELTOL=1e-12\n\
.END\n'

def convert(t_bytes):
    """
        Convert binary result of ngspice simulator to float table
    """
    res = t_bytes.split('\t')
    ret = list()
    for t_b in res:
        try:
            ret.append(float(t_b.strip(',')))
        except ValueError:
            pass
    return complex(ret[2], ret[3])

def get_results(spice_bytes):
    """
        run the simulation and return the Z_c and IHSR
    """
    pipe = Popen([PATH+EXE_NAME, '-b'], stdin=PIPE, stdout=PIPE)
    ret, _ = pipe.communicate(input=spice_bytes)
    table = ret.decode().splitlines()
    data = list()
    for line in table:
        if len(line) == 0:
            continue
        if line[0] == '0':
            data.append(convert(line))
    if len(data) == 0:
        print(table)
        return -1, -1
        raise ValueError(table)
    data = np.array(data)
    S = np.array((-data[0]-50*data[1],
                  data[2],
                  data[3],
                  data[4]))
    return S
if __name__ == '__main__':
    #test fonctions
    REF_MODEL = 'Hybrid Coupler\n\nVIN\t\t3\t0\tDC\t0\tAC\t1\nRIN\t\t3\tIN\t50\nROUT\tOUT\t0\t50\nRCPL\tCPL\t0\t50\nRISO\tISO\t0\t50\n\nL1\t\tIN\t1\t1.000e-09\nR1\t\t1\tOUT\t5.000e-01\nL2\t\tCPL\t2\t1.000e-09\nR2\t\t2\tISO\t5.000e-01\nK\t\tL1\tL2\t0.9\nCG1\t\tIN\t0\t2.500e-16\nCG2\t\tOUT\t0\t2.500e-16\nCG3\t\tISO\t0\t2.500e-16\nCG4\t\tCPL\t0\t2.500e-16\nCM1\t\tIN\tCPL\t5.000e-16\nCM2\t\tISO\tOUT\t5.000e-16\n\n'
    S_CTRL = generate_ac_simulation(1e9, 1e9, 1)
    REF_CTRL = '.AC LIN\t1\t1.000e+09\t1.000e+09\n.PRINT AC V(IN) I(VIN) V(OUT) V(CPL) V(ISO)\n\n.OPTION ELTOL=1e-12\n.END\n'
    if S_CTRL != REF_CTRL:
        raise ValueError
    S = get_results(bytes(REF_MODEL+S_CTRL, encoding='UTF-8'))
    IRL = -10*np.log10(np.abs(S[0]))
    if IRL < 12:
        raise ValueError(f'IRL = {IRL}')
    IHSR = -10*np.log10(np.abs(S[1]+1j*S[2]))
    if IHSR < 3:
        raise ValueError(f'ihsr = {IHSR}')