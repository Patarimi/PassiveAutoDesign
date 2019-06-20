# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 15:35:05 2019

@author: mpoterea
"""
import yaml

class Metal:
    """
        define the metal property of a layer
    """
    def __init__(self, _rho, _rougthness=0):
        self.rho = _rho
        self.rougthness = _rougthness
class Dielectric:
    """
        define the dielectric property of a layer
    """
    def __init__(self, _epsilon, _tand=0, _rougthness=0):
        self.epsilon = _epsilon
        self.tand = _tand
        self.rougthness = _rougthness
class Layer:
    """
        define a layer for a substrate
    """
    def __init__(self, _name, _height, _metal, _dielectric):
        self.name = _name
        self.metal = _metal
        self.width = {'min':1e-3, 'max':1e-3}
        self.gap = 1e-3
        self.dielectric = _dielectric
        self.height = _height
    def set_rules(self, _metal_w_min, _metal_w_max, _metal_gap_min):
        """
            Set the technological rules of the layer
            minimal and maximal width, and minimal gap
        """
        self.width = {'min':_metal_w_min, 'max':_metal_w_max}
        self.gap = _metal_gap_min
class Substrate:
    """
        contain all informations about a substrate
    """
    def __init__(self, _path=''):
        if _path != '':
            self.load(_path)
        else:
            self.sub = list()
    def add_layer(self, _layer):
        """
            add a layer on top of the last layer
        """
        self.sub.append(_layer)
    def get_index_of(self, _layer_name):
        """
            return the index of the first layer with the _layer_name name
        """
        index = -1
        for layer in self.sub:
            index = index+1
            if layer.name == _layer_name:
                break
        if index == -1:
            raise ValueError(f'No layer find with name: {_layer_name}')
        return index
    def dump(self, _path):
        """
            save the subtrate as an yaml file
        """
        with open(_path, 'w') as file:
            yaml.dump(self.sub, file)
    def load(self, _path):
        """
            load a yaml file to configure the substrate
        """
        with open(_path, 'r') as file:
            self.sub = yaml.full_load(file)

#Definition of classical metals
COPPER = Metal(5.8e8, 0.4e-3)
#Definition of classical dielectrics
AIR = Dielectric(1, 0, 0)
D5880 = Dielectric(2.2, 0.0009, 0.4e-3)
D6002 = Dielectric(2.94, 0.0012, 0.4e-3)
SILICON_OXYDE = Dielectric(4.2)
# unity test section
if __name__ == '__main__':
    SUB = Substrate()
    M_LYR = Layer('m_bott', 0.1e-3, COPPER, AIR)
    M_LYR.set_rules(0.508e-3, 10e-3, 0.508e-3)
    D_LYR = Layer('core', 0.8e-3, COPPER, D5880)
    D_LYR.set_rules(0.508e-3, 10e-3, 0.508e-3)
    SUB.add_layer(M_LYR)
    SUB.add_layer(D_LYR)
    SUB.add_layer(M_LYR)
    SUB.dump('cache/tech.yml')
    SUB.load('cache/tech.yml')
