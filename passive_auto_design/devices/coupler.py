# -*- coding: utf-8 -*-
"""

"""
from numpy import pi, sqrt
from ..unit import SI


class Coupler:
    """
    Create a coupler object
    """

    def __init__(self, _fc=1e9, _zc=50, _k=0.707):
        self.f_c = _fc
        self.z_c = _zc
        self.k = _k
        self.l = self.z_c / (2 * pi * self.f_c * sqrt(1 - self.k ** 2))
        self.c = self.l / self.z_c ** 2

    def print(self):
        """
        Print a summary of the solution l and c
        """
        message = f"L: {SI(self.l)}H\tC: {SI(self.c)}F"
        return message
