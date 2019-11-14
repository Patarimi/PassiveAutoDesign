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

class Ports:
    """
    class for ports declaration in sp and ac simulation
    """
    def __init__(self, term_pos, term_neg='0', impedance='50', name=''):
        self.t_plus = term_pos
        self.t_minus = term_neg
        self.imp = impedance
        if name == '':
            self.name = term_pos+"_"+term_neg
        self.name = name
    def get_term_pos(self):
        """
        return a string representing the name of the positive terminal
        """
        return self.t_plus
    def get_term_neg(self):
        """
        return a string representing the name of the negative terminal
        """
        return self.t_minus
    def get_impedance(self):
        """
        return a string representing the impedance of the port
        """
        return self.imp
    def get_name(self):
        """
        return a string representing the name of the port
        """
        return self.name

def set_path(_path):
    """
    set the path (absolute or relative) to the ng_spice directory
    """
    global PATH
    if os.path.exists(_path):
        PATH = _path
    else:
        raise FileNotFoundError(_path+': not reachable')

def generate_ac_simulation(freq_ctrl, ports_list):
    """
        generate an AC simulation with
        n_step linear steps between f_start and f_stop
        and for each ports of the ports_list
    """
    prt = ports_list
    str_in = 'V'+prt[0].get_name()+'\t\t3\t'+prt[0].get_term_neg()+'\tDC\t0\tAC\t1\n'\
    +'R'+prt[0].get_name()+'\t\t3\t'+prt[0].get_term_pos()+'\t'+prt[0].get_impedance()+'\n'
    str_out = ""
    for i in range(len(prt)-1):
        str_in += 'R'+prt[i+1].get_name()+'\t'\
        +prt[i+1].get_term_pos()+'\t'\
        +prt[i+1].get_term_neg()+'\t'\
        +prt[i+1].get_impedance()+'\n'
        str_out += f' V({prt[i+1].get_name()})'
    return str_in+f'\n.AC LIN	{freq_ctrl[2]}	{freq_ctrl[0]:.3e}	{freq_ctrl[1]:.3e}\n\
.PRINT AC V({prt[0].get_name()}) I(V{prt[0].get_name()}){str_out}\n\n\
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

def run_ac_sim(spice_circuit, ports, freq_ctrl=(1e9, 10e9, 10), _dump_results=False):
    """
        run an ac simulation and return gains and input reflection coefficient.
    """
    try:
        pipe = Popen([PATH+EXE_NAME, '-b'], stdin=PIPE, stdout=PIPE, bufsize=-1)
        spice_b = bytes(spice_circuit+generate_ac_simulation(freq_ctrl, ports), encoding='UTF-8')
        ret, _ = pipe.communicate(input=spice_b)
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

def run_sp_sim(spice_bytes, ports, freq_ctrl=(1e9, 10e9, 10), _dump_results=False):
    """
        run a sp simulation and return all gains and reflection coefficients.
    """
    global DUMP_NAME
    nb_ports = len(ports)-1
    if nb_ports == -1:
        raise ValueError('Port name not set.\nPlease use set_ports')
    sparam = list()
    for i in range(nb_ports+1):
        #put the simulated port in the beginning of the list
        port_tmp = (ports[i],)+ports[0:i]+ports[i+1:]
        DUMP_NAME = DUMP_NAME[:12]+'_'+ports[0].get_name()+DUMP_NAME[-4:]
        out = run_ac_sim(spice_bytes, port_tmp, freq_ctrl, _dump_results)
        #put the first result at the right place
        out = np.insert(out[1:], i, out[0])
        sparam.append(out)
    return sparam
