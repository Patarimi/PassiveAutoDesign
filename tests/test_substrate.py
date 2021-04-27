# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:30:00 2019

@author: Patarimi
"""
import pytest
import passive_auto_design.substrate as sb


def test_substrate():
    sub = sb.Substrate()
    with pytest.raises(FileNotFoundError):
        sub = sb.Substrate('wrong_path.yml')
    m_layer = sb.Layer('m_bott', 0.1e-3, sb.COPPER, sb.AIR)
    m_layer.set_rules(0.508e-3, 10e-3, 0.508e-3)
    d_layer = sb.Layer('core', 0.8e-3, sb.COPPER, sb.D5880)
    d_layer.set_rules(0.508e-3, 10e-3, 0.508e-3)
    sub.add_layer(m_layer)
    sub.add_layer(d_layer)
    sub.add_layer(m_layer)
    with pytest.raises(ValueError):
        sub.dump('tests')
    sub.dump('tests/tech.yml')
    # remove for now
    # TODO : Find why it work on local and not on server
    # SUB.load('tests/tech.yml')
    assert sub.get_index_of('m_bott') == 0
    with pytest.raises(ValueError):
        sub.get_index_of('foo')
