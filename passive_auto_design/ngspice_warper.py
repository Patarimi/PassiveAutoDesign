# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:30:07 2019

@author: mpoterea
"""
from subprocess import Popen, PIPE
import numpy as np
import os

dump_name = './tests/dump.res'
exe_name = "ngspice_con.exe"
path = "/"

def set_path(_path):
    """
    set the path (absolute or relative) to the ng_spice directory
    """
    global path
    if os.path.exists(_path):
        path = _path
    else:
        raise FileNotFoundError(_path+': not reachable')
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

def get_results(spice_bytes, _dump_results=False):
    """
        run the simulation and return gain and reflection coefficient (s-parameters simulation)
    """
    try:
        pipe = Popen([path+exe_name, '-b'], stdin=PIPE, stdout=PIPE)
    except FileNotFoundError:
        raise EnvironmentError('ngspice is not installed !')
    except:
        raise
    ret, _ = pipe.communicate(input=spice_bytes)
    table = ret.decode().splitlines()
    if _dump_results:
        with open(dump_name, 'w') as file:
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
    _s = np.array((-data[0]-50*data[1],
                   data[2],
                   data[3],
                   data[4]))
    return _s
