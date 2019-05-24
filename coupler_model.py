# -*- coding: utf-8 -*-
"""
Created on Thu May 23 10:02:06 2019

@author: sredois
"""

import numpy as np
import math
import PassiveAutoDesign as pad



def self_ind(length,width,thick):
    """
        Calculate the self inductance 
    """
    GMD=0.2235*(width+thick)
    res = (0.42*4*1e-7)*length*(math.log(2*length/GMD)+(GMD/length)-1)
    return res

def mut_ind(length,width,thick):
    L1=self_ind(length,width,thick);
    L2=L1
    dps=1.5e-6
    
    Lm=0
    N_face5=20
    N_face6=20
    P=[[0,width],[complex(0,thick),complex(width,thick)]]
    Q=[[complex(0,thick+dps),complex(width,thick+dps)],[complex(0,thick+thick+dps),complex(width,thick+thick+dps)]]
    for i in range(1,9):
        leq=length/8
        for v6 in range(0,2):              
            for h6 in range(0,2):             
                for v5 in range(0,2):        
                    for h5 in range(0,2):  
                        dx=np.real(P[v6][h6])-np.real(Q[v5][h5])
                        dy=np.imag(P[v6][h6])-np.imag(Q[v5][h5])
                        A=(dx**2)*(dy**2)
                        L=self_ind(leq, abs(dx), abs(dy));
                        Lm=Lm+((-1)**(v6+h6+v5+h5))*A*L/(4*width*width*thick*thick);
    return Lm

def cap_par(ediel,A,d):        # Parallel Capacitance     
    res=8.8e-12*ediel*A/d
    return res

def cap_frin(ediel,length,thick,d): # Fringe Capacitance
    res=(2*np.pi*8.8e-12*ediel*length)/(math.log(1+(2*d/thick)+math.sqrt((2*d/thick)*((2*d/thick)+2))))
    return res

