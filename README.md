# PassiveAutoDesign [WIP] [![Build Status](https://ci.appveyor.com/api/projects/status/32r7s2skrgm9ubva/branch/master?svg=true)](https://ci.appveyor.com/project/Patarimi/passiveautodesign) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Patarimi/PassiveAutoDesign.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Patarimi/PassiveAutoDesign/context:python) [![Coverage Status](https://coveralls.io/repos/github/Patarimi/PassiveAutoDesign/badge.svg?branch=master)](https://coveralls.io/github/Patarimi/PassiveAutoDesign?branch=master)
Python Script for Fast Design of RF-Passive Components. This script is in an early stage of development. Tested on Windows and Linux.

Getting started
----
The library required are scikit-rf, numpy, scipy, yaml and matplotlib (for plotting results). The required versions can be find in _requirements.txt_. Install the library using
```
pip install passive-auto-design
```
A demo is given [here](https://share.streamlit.io/patarimi/passiveautodesign/apps/home.py) and the documentation can be found [here](https://passiveautodesign.netlify.app/)

Package Structure
----
The Package is composed of five modules:

- The _substrate.py_ file which describes the substrate used (or Back End Of Line).
- The _components_ directory which contains RF-components to be implemented in a susbtrate (Waveguides, Transformers, Coupler...). It also enables rough geometry design/estimation from given rf specifications.
- The _special.py_ file which contains physical constants and special functions (dB, NmtodBcm, ...)
- The _space_mapping.py_ file which help deploy space mapping algorithm.
- The _unit.py_ file which contains fonction to hlp formatting number to string.
