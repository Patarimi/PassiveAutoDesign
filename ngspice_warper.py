# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:30:07 2019

@author: mpoterea
"""

from subprocess import Popen, PIPE
import numpy as np

PATH = "C:/Users/mpoterea/Documents/PassiveAutoDesign/"
FILE_NAME = "cache/model_ind.cir"
EXE_NAME = "tierce_parts/Spice64/bin/ngspice_con.exe"

def generate_model_transfo(l_c, c_g, c_m, k_ind, f_targ):
    """
        Generate a equivalent circuit of a transformer with the given values
    """
    return bytes(f'Hybrid Coupler\n\n\
VIN		3	0	DC	0	AC	1\n\
RIN		3	IN	50\n\
ROUT	OUT	0	50\n\
RCPL	CPL	0	50\n\
RISO	ISO	0	50\n\n\
L1		IN	1	{l_c:.3e}\n\
R1		1	OUT	0.1u\n\
L2		CPL	2	{l_c:.3e}\n\
R2		2	ISO	0.1u\n\
K		L1	L2	{k_ind:.3n}\n\
CG1		IN	0	{c_g:.3e}\n\
CG2		OUT	0	{c_g:.3e}\n\
CG3		ISO	0	{c_g:.3e}\n\
CG4		CPL	0	{c_g:.3e}\n\
CM1		IN	CPL	{c_m:.3e}\n\
CM2		ISO	OUT	{c_m:.3e}\n\n\
.AC LIN	1	{f_targ:.3e}	{f_targ:.3e}\n\
.PRINT AC V(IN) I(VIN) V(OUT) V(CPL)\n\n\
.OPTION ELTOL=1e-12\n\
.END\n', encoding='UTF-8')

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
    p = Popen([PATH+EXE_NAME, '-b'], stdin=PIPE, stdout=PIPE)
    ret,_ = p.communicate(input=spice_bytes)
    table = ret.decode().splitlines()
    data = list()
    for line in table:
        if len(line) == 0:
            continue
        if line[0] == '0':
            data.append(convert(line))
    if len(data) == 0:
        print(table)
        return -1
    s_11 = -data[0]-50*data[1]
    s_21 = data[2]
    s_31 = data[3]
    z_c = 50*(1-s_11)/(s_11+1)
    ihsr = dB(s_21-1j*s_31)-dB(s_21+1j*s_31)
    return z_c, ihsr

def dB(cmplx):
    """
        Return the decibel value of the given imaginary number.
    """
    return 20*np.log10(np.abs(cmplx))
