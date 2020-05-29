# -*- coding: utf-8 -*-
"""
Created on Fri May 29 15:26:27 2020

@author: mpoterea
"""

from browser import document, html

document <= html.H2("RF Components Design Helper")

menu_item = ('Transformer Sizing', 'Model Extraction', 'About')
document <= html.UL((html.LI(item, id="select") for item in menu_item), id="menu")

input_list = ("Frequency (GHz):",                    html.INPUT("", id="frequence", type="text"),\
              "Characteristic Impedance (&Omega;):", html.INPUT("", id="z_c", type="text"),\
              "Coupling factor (SI):",               html.INPUT("", id="k", type="text"))
    
div_list = list()
for item in input_list:
    div_list.append(html.DIV(item))
div_list.append(html.BUTTON("Calculate"))

document <= html.DIV(div_list, id="content")
