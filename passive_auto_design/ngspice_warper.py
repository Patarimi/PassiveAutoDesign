# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:30:07 2019

@author: mpoterea
"""
from subprocess import Popen, PIPE
import os
import numpy as np

if os.name != 'nt':
    raise EnvironmentError('ngspice_warper Only Supported on Windows (nt) Operating System')

DUMP_NAME = './tests/dump.res'
EXE_NAME = "ngspice_con.exe"
PATH = "/"

def set_path(_path):
    """
    set the path (absolute or relative) to the ng_spice directory
    """
    global PATH
    if os.path.exists(_path):
        PATH = _path
    else:
        raise FileNotFoundError(_path+': not reachable')

def generate_ac_simulation(freq_ctrl, port):
    """
        generate an AC simulation with n_step linear steps between f_start and f_stop
    """
    str_in = f'V{port[0]}\t\t3\t0\tDC\t0\tAC\t1\n\
R{port[0]}\t\t3\t{port[0]}\t50\n'
    str_out = ""
    for i in range(len(port)-1):
        str_in += f'R{port[i+1]}\t{port[i+1]}\t0\t50\n'
        str_out += f' V({port[i+1]})'
    return str_in+f'\n.AC LIN	{freq_ctrl[2]}	{freq_ctrl[0]:.3e}	{freq_ctrl[1]:.3e}\n\
.PRINT AC V({port[0]}) I(V{port[0]}){str_out}\n\n\
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

def run_ac_sim(spice_circuit, freq_ctrl=(1e9, 10e9, 10), ports=['1', '2'], _dump_results=False):
    """
        run an ac simulation and return gains and input reflection coefficient.
    """
    try:
        pipe = Popen([PATH+EXE_NAME, '-b'], stdin=PIPE, stdout=PIPE, bufsize=-1)
        spice_bytes = bytes(spice_circuit+generate_ac_simulation(freq_ctrl, ports), encoding='UTF-8')
        ret, _ = pipe.communicate(input=spice_bytes)
    except FileNotFoundError:
        raise FileNotFoundError('ngspice not found at: '+PATH+EXE_NAME+'\n\
Please set the correct folder using set_path')
    table = ret.decode().splitlines()
    if _dump_results:
        with open(DUMP_NAME, 'w') as file:
            for line in table:
                file.write(line+'\n')
    data = list()
    param = list()
    new_param = False
    for line in table:
        if len(line) == 0:
            new_param = False
            continue
        if line[0] == '0':
            new_param = True
            if len(param) != 0:
                data.append(param)
                param = list()
        if new_param:
            param.append(convert(line))
    if len(param) != 0: # getting the last parameter !!
        data.append(param)
    data = np.array(data)
    _s = np.insert(data[2:], 0, (-data[0]-50*data[1]), axis=0)
    return _s

def run_sp_sim(spice_bytes, freq_ctrl=(1e9, 10e9, 10), ports=['1', '2'], _dump_results=False):
    """
        run a sp simulation and return all gains and reflection coefficients.
    """
    global DUMP_NAME
    nb_ports = len(ports)-1
    if nb_ports == -1:
        raise ValueError('Port name not set.\nPlease use set_ports')
    sparam = list()
    for i in range(nb_ports+1):
        DUMP_NAME = DUMP_NAME[:12]+'_'+ports[0]+DUMP_NAME[-4:]
        out = run_ac_sim(spice_bytes, freq_ctrl, ports, _dump_results)
        #print(np.round(out, 3))
        out = np.insert(out[1:], i, out[0], axis=0)
        sparam.append(out)
    #put the simulated port in the end of the list
        ports = ports[1:]+[ports[0]]
    return np.array(sparam)
