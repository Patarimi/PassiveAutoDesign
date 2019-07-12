# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: mpoterea
"""

import passive_component as pac
import substrate as sub

class TestCoupler():
    def test_design(self):
        SUB = sub.Substrate('tests/tech.yml')
        CPL = pac.Coupler(SUB)
        assert CPL.f_c == 1e9