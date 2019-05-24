# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:42:18 2019

@author: sredois
"""

import numpy as np
import math
import PassiveAutoDesign as pad
import coupler_model as cmod

#Technological parameters
hp=10.29e-6 #distance between substrate primary
hs=5.79e-6 #distance between substrate secondary
tp=3e-6 #primary thickness
ts=3e-6 #secondary thickness
tsi=350e-6 #substrate thickness
dps=1.5e-6 #distance primary secondary
eox=4.382 #permittivity of the dielectric
esi=3. #permittivity of the substrate
rm=17e-9 #metal resistivity (Ohms.m)
rsi=1e3 #substrate resistivity (Ohms.m)
e0=8.8e-12 
mu_m=1.256629e-6 #Copper permeability
mu0=4*np.pi*1e-7 
ediel=4.382

#Geometrical parameters
n=8
freq=40e9
d0=92.7e-6
Lp=0.5*n*(d0)/math.tan((360/n)*math.pi/180);
Ls=Lp
Ws=7.8e-6
Wp=7.8e-6
Nbt=1 #Number of turns
kcap=0.52*(4-1.5*Nbt) #Flipped topology for 1 turn
km=0.9
krac=175e3

#Substrate Branches
Cpox=kcap*cmod.cap_par(ediel,0,hp)
Csox=kcap*(cmod.cap_par(ediel,Ls*Ws,hs)+cmod.cap_frin(ediel,Ls,ts,hs))
Rpsub=3*rsi*Wp/(Lp*tsi)
Rssub=3*rsi*Ws/(Ls*tsi)
Cpsub=esi*e0*rsi/Rpsub
Cssub=esi*e0*rsi/Rssub

#Coupling Element
Cps=kcap*cmod.cap_par(ediel,Ls*Ws,dps)
M=km*cmod.mut_ind(Ls,Ws,ts)

#Resistor
dp=math.sqrt(rm/(np.pi*mu0*mu_m*freq)) #Skin Effect
ds=dp
Rpac=krac*rm*Lp/((1+tp/Wp)*dp*(1-np.exp(-tp/dp)))
Rsac=krac*rm*Lp/((1+ts/Ws)*ds*(1-np.exp(-ts/ds)))
Rpdc=rm*Lp/(Wp*tp)
Rsdc=rm*Ls/(Ws*ts)
Rs=Rsdc+Rsac
Rp=Rpdc+Rpac
L1=cmod.self_ind(Ls,Ws,ts)
k=2*M/L1
