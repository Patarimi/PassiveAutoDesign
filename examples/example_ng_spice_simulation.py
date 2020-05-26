"""
This script is given as an example to make simulation using ng_spice_warper.
"""


import matplotlib.pyplot as plt
import passive_auto_design.ngspice_warper as ng
from passive_auto_design.special import dB

# configuration of the simulator
ng.set_path('../ng_spice/')
plt.close('all')

# creation of an empty circuit
CIR = ng.Circuit('Test 1')

Atten = 5
R0 = 50
R1 = R0*(10**(Atten/20)+1)/(10**(Atten/20)-1)
R2 = 0.5*R0*(10**(Atten/10)-1)/(10**(Atten/20))
# Creating a pi attenuator
CIR.add_res(R2, 'IN', 'OUT')
CIR.add_res(R1, 'OUT')
CIR.add_res(R1, 'IN')

#Defining ports
PORTS = (ng.Ports('IN'),
         ng.Ports('OUT'))

Sp = ng.run_sp_sim(CIR.get_cir(), PORTS, (1e9, 30e9, 30))

leg = list()
for i in range(2):
    for j in range(2):
        plt.plot(dB(Sp[i,j]))
        leg.append(f'dB({i+1}, {j+1})')
plt.ylim([-20, 0])
plt.legend(leg)
plt.grid(True)
