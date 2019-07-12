# PassiveAutoDesign [WIP] [![Build Status](https://travis-ci.org/Patarimi/PassiveAutoDesign.svg?branch=master)](https://travis-ci.org/Patarimi/PassiveAutoDesign)
Python Script for Fast Design of RF-Passive Components.\
This script is in an early stage of development. For now, it only works with Windows OS.

Getting started
---
The library required numpy, scipy and matplotlib (for plotting results). The required versions can be find in _requirements.txt_.\
Examples are given in the _examples_ directory.

Library Architecture
---

The _substrate.py_ file describes the substrate used (or Back End Of Line).\
The _structure.py_ file describes the rf-structure implemented in a susbtrate (SIW, AF-SIW, Transformers).\
The _passive_component.py_ describes the rf-component (hybrid coupler, impedance transformers, and (soon ?) filters). It also enables rough geometry design/estimation from given rf specifications.
