# PassiveAutoDesign [WIP] [![Build Status](https://ci.appveyor.com/api/projects/status/32r7s2skrgm9ubva/branch/master?svg=true)](https://ci.appveyor.com/project/Patarimi/passiveautodesign) [![Requirements Status](https://requires.io/github/Patarimi/PassiveAutoDesign/requirements.svg?branch=master)](https://requires.io/github/Patarimi/PassiveAutoDesign/requirements/?branch=master) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Patarimi/PassiveAutoDesign.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Patarimi/PassiveAutoDesign/context:python)
Python Script for Fast Design of RF-Passive Components.\
This script is in an early stage of development. For now, it only works with Windows OS.

Getting started
----
The library required numpy, scipy, yaml and matplotlib (for plotting results). The required versions can be find in _requirements.txt_.\
Install the library using
```
pip install passive-auto-design
```
Then install [ngspice](http://ngspice.sourceforge.net/download.html).\
Examples are given in the _examples_ directory.\
A demo is given [here](rf-design-helper-web.herokuapp.com/)

Package Structure
----
The Package is composed of five modules:

- The _substrate.py_ file which describes the substrate used (or Back End Of Line).
- The _structure_ directory which contains RF-structures to be implemented in a susbtrate (SIW, AF-SIW, Transformers, ...).
- The _passive_component_ which contains RF-components (such as hybrid coupler, impedance transformers, and (soon ?) filters). It also enables rough geometry design/estimation from given rf specifications.
- _ng_spice_warper.py_ which eased the use of the ng-spice program.
- _special.py_ which contains physical constants and special functions (dB, NmtodBcm, ...)
