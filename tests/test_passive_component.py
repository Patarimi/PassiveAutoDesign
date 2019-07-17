# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:07:03 2019

@author: mpoterea
"""

import design.passive_component as pac
import design.substrate as sub

class TestCoupler():
    def test_design(self):
        SUB = sub.Substrate('tests\passive_component_tech.yml')
        CPL = pac.Coupler(SUB)
        assert CPL.f_c == 1e9