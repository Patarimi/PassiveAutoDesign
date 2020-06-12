# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 16:10:47 2019

@author: mpoterea
"""
import numpy as np
import yaml
import skrf as rf
from passive_auto_design.special import u0
import passive_auto_design.structure.lumped_element as lmp

class Transformer:
    """
        Create a transformator object with the specified geometry _primary & _secondary
        (which are dict defined as :
            {'di':_di,'n_turn':_n_turn, 'width':_width, 'gap':_gap, 'height':height})
        and calculate the associated electrical model
    """
    def __init__(self, primary, secondary, freq=1e9, modelmapfile=None):
        self.prim = primary
        self.second = secondary
        if isinstance(freq, float):
            self.freq = np.array([freq,])
        else:
            self.freq = freq
        if modelmapfile is None:
            modelmapfile = 'tests/default.map'
        with open(modelmapfile, 'r') as file:
            self.modelmap = yaml.full_load(file)
        self.model = {'k':0.9}
        self.set_primary(primary)
        self.set_secondary(secondary)
        self.circuit = self.__makecircuit()
    def set_primary(self, _primary):
        """
            modify the top inductor and refresh the related model parameters
        """
        self.prim = _primary
        self.model.update({
            'lp': self.l_geo(True),
            'rp': self.r_geo(True, 17e-9),
            'cg': self.cc_geo(False),
            'cm': self.cc_geo(True),
            })
        try:
            self.circuit = self.__makecircuit()
        except KeyError:
            pass
    def set_secondary(self, _secondary):
        """
            modify the bottom inductor and refresh the related model parameters
        """
        self.second = _secondary
        self.model.update({
            'ls': self.l_geo(False),
            'rs': self.r_geo(False, 17e-9),
            'cg': self.cc_geo(False),
            'cm': self.cc_geo(True),
            })
        try:
            self.circuit = self.__makecircuit()
        except KeyError:
            pass
    def l_geo(self, _of_primary=True):
        """
            return the value of the distributed inductance of the described transformer
            if _of_primary, return the value of the top inductor
            else, return the value of the bottom inductor
        """
        k_1 = float(self.modelmap["mu_r"])   #constante1 empirique pour inductance
        k_2 = float(self.modelmap["dens"])   #constante2 empirique pour inductance
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        outer_diam = geo['di']+2*geo['n_turn']*geo['width']+2*(geo['n_turn']-1)*geo['gap']
        rho = (geo['di']+outer_diam)/2
        density = (outer_diam-geo['di'])/(outer_diam+geo['di'])
        return k_1*u0*geo['n_turn']**2*rho/(1+k_2*density)
    def cc_geo(self, _mutual=True):
        """
            return the value of the distributed capacitance of the described transformer
            if _mutual, return the capacitance between primary and secondary
            else, return the capacitance to the ground plane
        """
        if _mutual:
            dist = float(self.modelmap["d1"])
        else:
            dist = float(self.modelmap["d2"])
        n_t = self.prim['n_turn']
        eps_r = float(self.modelmap["eps_r"])
        area = (n_t-1)*self.prim['di']*self.prim['width']
        cap = lmp.Capacitor(area, dist, eps_r)
        return cap.par["cap"]
    def r_geo(self, _of_primary=True, rho=17e-10):
        """
            return the value of the resistance of the described transformer
        """
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        n_t = geo['n_turn']
        l_tot = 8*np.tan(np.pi/8)*n_t*(geo['di']+geo['width']+(n_t-1)*(geo['width']+geo['gap']))
        r_dc = rho*l_tot/geo['width']
        return r_dc

    def __makecircuit(self):
        freq = rf.Frequency.from_f(self.freq, unit='Hz')
        media = rf.DefinedGammaZ0(frequency=freq, Z0=50)

        port1 = rf.Circuit.Port(freq, "port1")
        port2 = rf.Circuit.Port(freq, "port2")
        port3 = rf.Circuit.Port(freq, "port3")
        port4 = rf.Circuit.Port(freq, "port4")

        transfo_ideal = mutual_ind(self.model["lp"], self.model["ls"], self.model["k"], freq)
        res_p = media.resistor(self.model["rp"], name='rp')
        res_s = media.resistor(self.model["rs"], name='rs')

        connections = [
            [(port1, 0), (transfo_ideal, 0)],
            [(res_p, 0), (transfo_ideal, 1)],
            #[(port2, 0), (res_p, 1)],
            [(port3, 0), (transfo_ideal, 2)],
            [(res_s, 0), (transfo_ideal, 3)],
            #[(port4, 0), (res_s, 3)],
            ]
        cir = rf.Circuit(connections)
        return cir

def mutual_ind(l_1, l_2, k_mut, freq, z_0=50):
    """
        Create a transformateur with a primary of l_1, and secondary of l_2
        and a coupling factor of k_mut
    """
    for f_t in freq.f:
        w_t = 2 * np.pi * f_t
        y_1 = 1/(1j*w_t*l_1*(1-k_mut**2))
        y_2 = 1/(1j*w_t*l_2*(1-k_mut**2))
        y_m = k_mut/(1j*w_t*np.sqrt(l_1*l_2)*(1-k_mut**2))
        yparam = np.array([[[y_1, -y_m, y_m, -y_1],
                            [-y_m, y_2, -y_2, y_m],
                            [y_m, -y_2, y_2, -y_m],
                            [-y_1, y_m, -y_m, y_1]]])
        try:
            yparams = np.vstack((yparams, yparam))
        except NameError:  # Only needed for first iteration.
            yparams = np.copy(yparam)
    yparams+=1e-10

    ntwk = rf.Network(frequency=freq, s=rf.y2s(yparams), z0=z_0, name='coupled inductors')
    return ntwk
