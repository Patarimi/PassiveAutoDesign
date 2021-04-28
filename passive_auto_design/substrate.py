# -*- coding: utf-8 -*-
"""
Define all the object use to describe the substrate in which the structures are created.
"""
import os
import yaml


class Metal:
    """
        define the metal property of a layer
    """
    def __init__(self, _rho, _roughness=0.0):
        self.rho = _rho
        self.roughness = _roughness


class Dielectric:
    """
        define the dielectric property of a layer
    """
    def __init__(self, _epsilon, _tan_d=0.0, _roughness=0.0):
        self.epsilon = _epsilon
        self.tan_d = _tan_d
        self.roughness = _roughness


class Layer:
    """
        define a layer for a substrate
    """
    def __init__(self, _name, _height, _metal, _dielectric):
        self.name = _name
        self.metal = _metal
        self.width = {'min': 1e-3, 'max': 1e-3}
        self.gap = 1e-3
        self.dielectric = _dielectric
        self.height = _height

    def set_rules(self, _metal_w_min, _metal_w_max, _metal_gap_min):
        """
            Set the technological rules of the layer
            minimal and maximal width, and minimal gap
        """
        self.width = {'min': _metal_w_min, 'max': _metal_w_max}
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
                return index
        raise ValueError(f'No layer find with name: {_layer_name}')

    def dump(self, _path):
        """
            save the substrate as an yaml file
        """
        save_dir = _path.rsplit('/', 1)
        if len(save_dir) < 2:
            raise ValueError('incorrect path')
        if len(save_dir) == 2:
            os.makedirs(save_dir[0], exist_ok=True)
        with open(_path, 'w+') as file:
            yaml.dump(self.sub, file)

    def load(self, _path):
        """
            load a yaml file to configure the substrate
        """
        with open(_path, 'r') as file:
            self.sub = yaml.full_load(file)

# Definition of classical metals


COPPER = Metal(5.8e8, 0.4e-3)

# Definition of classical dielectrics


AIR = Dielectric(1, 0, 0)
D5880 = Dielectric(2.2, 0.0009, 0.4e-3)
D6002 = Dielectric(2.94, 0.0012, 0.4e-3)
SILICON_OXYDE = Dielectric(4.2)
