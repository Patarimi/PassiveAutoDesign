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
        else:
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
        return a real representing the impedance of the port
        """
        return float(self.imp)
    def get_name(self):
        """
        return a string representing the name of the port
        """
        return self.name
class Circuit:
    """
    This class is intended to ease the declaration of spice model
    """
    def __init__(self, _name='Circuit'):
        self.__descriptor = _name+'\n\n'
        self.__indice = {'res':0,
                         'ind':0,
                         'cap':0,
                         'v_src':0,
                         'mut':0}
    def add_res(self, _val, _pos_net, _neg_net='0', _name=''):
        """
        add a resistor between the two net _pos_net and _neg_net
        """
        num = float2engineer(_val)
        if _name == '':
            self.__descriptor += f'R{self.__indice["res"]}\t{_pos_net}\t{_neg_net}\t{num}\n'
            self.__indice['res'] += 1
        else:
            self.__descriptor += f'R{_name}\t{_pos_net}\t{_neg_net}\t{num}\n'
    def add_ind(self, _val, _pos_net, _neg_net='0'):
        """
        add a inductance between the two net _pos_net and _neg_net
        """
        num = float2engineer(_val)
        self.__descriptor += f'L{self.__indice["ind"]}\t{_pos_net}\t{_neg_net}\t{num}\n'
        self.__indice['ind'] += 1
    def add_mut(self, _l1_name, _l2_name, _k=0.99):
        """
        add a coupling factor between two inductors _l1_name and _l2_name
        """
        num = float2engineer(_k)
        self.__descriptor += f'K{self.__indice["mut"]}\t{_l1_name}\t{_l2_name}\t{num}\n'
        self.__indice['mut'] += 1

    def add_cap(self, _val, _pos_net, _neg_net='0'):
        """
        add a inductance between the two net _pos_net and _neg_net
        """
        num = float2engineer(_val)
        self.__descriptor += f'C{self.__indice["cap"]}\t{_pos_net}\t{_neg_net}\t{num}\n'
        self.__indice['cap'] += 1
    def add_v_source(self, _dc_val, _pos_net, _neg_net='0', _ac_mag='1', _ac_phase='0', _name=''):
        """
        add a voltage source between the two net _pos_net and _neg_net
        """
        num = float2engineer(_dc_val)
        if _name == '':
            self.__descriptor += f'V{self.__indice["v_src"]}\t{_pos_net}\t{_neg_net}\tDC\t{num}\t\
AC\t{_ac_mag}\t{_ac_phase}\n'
            self.__indice['v_src'] += 1
        else:
            self.__descriptor += f'V{_name}\t{_pos_net}\t{_neg_net}\tDC\t{num}\t\
AC\t{_ac_mag}\t{_ac_phase}\n'
    def get_cir(self):
        """
        return a string representing the circuit
        """
        return self.__descriptor
def float2engineer(_f, _res=2):
    """
    convert a float number in engineer notation (G, M, k, etc...)
    """
    if _f <= 1e-18:
        return '0'
    pre_fix = ('T', 'G', 'MEG', 'K', '', 'm', 'u', 'n', 'p', 'f')
    for i in range(10):
        power = (12-3*i)
        if _f > 10**(power-0.1):
            return f'{np.round(_f*10**(-power), _res)}'+pre_fix[i]
    return f'{_f*1e-15}f'
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
    cir = Circuit('')
    cir.add_v_source(0, 'MID_SONDE', prt[0].get_term_neg(), 1, 0, _name=prt[0].get_name())
    cir.add_res(prt[0].get_impedance(), prt[0].get_term_pos(), 'MID_SONDE', _name=prt[0].get_name())
    str_out = ""
    for i in range(len(prt)-1):
        cir.add_res(prt[i+1].get_impedance(),
                    prt[i+1].get_term_pos(),
                    prt[i+1].get_term_neg(),
                    prt[i+1].get_name())
        str_out += f' V({prt[i+1].get_term_pos()})'
    return cir.get_cir()+f'\n.AC LIN\t{freq_ctrl[2]}\t\
{float2engineer(freq_ctrl[0])}\t{float2engineer(freq_ctrl[1])}\n\
.PRINT AC V({prt[0].get_term_pos()})\
 I(V{prt[0].get_name()}){str_out}\n\n\
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
