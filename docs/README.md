# PassiveAutoDesign [![Build Status](https://ci.appveyor.com/api/projects/status/32r7s2skrgm9ubva/branch/master?svg=true)](https://ci.appveyor.com/project/Patarimi/passiveautodesign) [![Coverage Status](https://coveralls.io/repos/github/Patarimi/PassiveAutoDesign/badge.svg?branch=master)](https://coveralls.io/github/Patarimi/PassiveAutoDesign?branch=master)
Python Script for Fast Design of RF-Passive Components. This script is in an early stage of development. Tested on Windows and Linux.

Getting started
----
The library required are scikit-rf, numpy, scipy, yaml and matplotlib (for plotting results). The required versions can be find in _requirements.txt_. Install the library using
```
pip install passive-auto-design
```
or
```
poetry install
```
A demo is given [here](https://share.streamlit.io/patarimi/passiveautodesign/apps/home.py) and the documentation can be found [here](https://patarimi.github.io/PassiveAutoDesign/)

Package Structure
----
The Package is composed of 9 modules:

- The _substrate.py_ file which describes the substrate used (or Back End Of Line).
- The _components_ directory which contains RF-components to be implemented in a susbtrate (Waveguides, Transformers, Coupler...). It also enables rough geometry design/estimation from given rf specifications.
- The _devices_ module which contains RF-devices. It helps defining the rf-specification of the devices from the given higher-level specification.
- The _special.py_ file which contains special functions.
- The _space_mapping.py_ file which help deploy space mapping algorithm.
- The _units_ module which contains pydantic models to ease the usage of physical dimension. It also contains physical constants.
