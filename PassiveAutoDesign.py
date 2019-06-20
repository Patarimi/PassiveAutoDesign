# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:12:17 2019

@author: mpoterea
"""
import numpy as np
from scipy.optimize import dual_annealing
import ngspice_warper as ng

class Coupler:
    """
        Create a coupler object
    """
    def __init__(self, _substrate, _fc=1e9, _zc=50, _k=0.9):
        esp_r = _substrate.sub[1].dielectric.epsilon
        h_int = _substrate.sub[1].height
        h_sub = _substrate.sub[3].height
        self.f_c = _fc
        self.z_c = _zc
        self.k = _k
        self.bounds = np.array([(_substrate.sub[0].width['min'], _substrate.sub[0].width['max']),
                                (1, 4),
                                (_substrate.sub[0].width['max'], 20*_substrate.sub[0].width['max']),
                                (_substrate.sub[0].gap, 1.01*_substrate.sub[0].gap)])
        geo = {'di':20, 'n_turn':1, 'width':2e-6, 'gap':2e-6}
        self.transfo = Transformer(geo, geo, esp_r, h_int, h_sub)
    def cost(self, sol):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        geo = {'di':sol[2], 'n_turn':np.round(sol[1]), 'width':sol[0], 'gap':sol[3]}
        self.transfo.set_primary(geo)
        self.transfo.set_secondary(geo)
        b_model = bytes(self.transfo.generate_spice_model(self.k), encoding='UTF-8')
        b_simulation = bytes(ng.generate_ac_simulation(self.f_c, self.f_c, 1), encoding='UTF-8')
        z_eff, ihsr = ng.get_results(b_model+b_simulation)
        if ihsr > 26.7:
            return std_dev(np.array([z_eff]), np.array([self.z_c]))
        return std_dev(np.array([z_eff, ihsr]), np.array([self.z_c, 26.7]))
    def design(self, f_targ, z_targ):
        """
            design an hybrid coupleur with the targeted specifications (f_targ, z_targ)
            return an optimization results (res)
        """
        self.f_c = f_targ
        self.z_c = z_targ
        res = dual_annealing(self.cost, self.bounds, maxiter=200)
        return res
    def print(self, res):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(self.bounds)*1e6
        print(f'Solution funds with remaining error of: {res.fun:.2e}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'best point  :\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
class Balun:
    """
        Create a balun object
    """
    def __init__(self, _substrate, _fc=1e9, _z_source=50, _z_load=50, _k=0.9):
        eps_r = _substrate.sub[1].dielectric.epsilon
        h_int = _substrate.sub[1].height
        h_sub = _substrate.sub[3].height
        self.f_c = _fc
        self.z_src = _z_source
        self.z_ld = _z_load
        self.k = _k
        self.bounds = np.array([(_substrate.sub[0].width['min'], _substrate.sub[0].width['max']),
                                (1, 4),
                                (_substrate.sub[0].width['max'], 20*_substrate.sub[0].width['max']),
                                (_substrate.sub[0].gap, 1.01*_substrate.sub[0].gap),
                                (_substrate.sub[2].width['min'], _substrate.sub[2].width['max']),
                                (1, 4),
                                (_substrate.sub[2].width['max'], 20*_substrate.sub[2].width['max']),
                                (_substrate.sub[2].gap, 1.01*_substrate.sub[2].gap)])
        geo = {'di':20, 'n_turn':1, 'width':2e-6, 'gap':2e-6}
        self.transfo = Transformer(geo, geo, eps_r, h_int, h_sub)
    def cost(self, sol):
        """
            return the cost (standard deviation)
            between the proposed solution and the targeted specifications
        """
        self.transfo.set_primary({'di':sol[2], 'n_turn':np.round(sol[1]), 'width':sol[0], 'gap':sol[3]})
        self.transfo.set_secondary({'di':sol[6], 'n_turn':np.round(sol[5]), 'width':sol[4], 'gap':sol[7]})
        l_source = self.transfo.model['ls']
        l_load = self.transfo.model['lp']
        k = self.k
        alpha = (1-k**2)/k**2
        n_turn = k*np.sqrt(l_source/l_load)
        z_l = 1j*l_source*(k**2)*2*np.pi*self.f_c
        zs_r = alpha*z_l + z_l*(n_turn**2)*self.z_ld/(z_l+self.z_ld*(n_turn**2))
        zl_r = ((np.conj(self.z_src)+alpha*z_l)*z_l/(np.conj(self.z_src)+z_l+alpha*z_l))/n_turn**2
        return std_dev(zs_r, self.z_src) + std_dev(zl_r, self.z_ld)
    def design(self, _f_targ, _zl_targ, _zs_targ):
        """
            design an impedance transformer
            with the targeted specifications (f_targ, zl_targ, zs_targ)
            return an optimization results (res)
        """
        self.f_c = _f_targ
        self.z_src = _zs_targ
        self.z_ld = _zl_targ
        res = dual_annealing(self.cost, self.bounds, maxiter=500)
        return res
    def print(self, res):
        """
            print a summary of the solution (res)
            with a comparison to the boundaries
        """
        sol = res.x*1e6
        bds = np.array(self.bounds)*1e6
        print(f'Solution funds with remaining error of: {res.fun:.2e}')
        print('Termination message of algorithm: '+str(res.message))
        print(f'\t\tW (µm)\tn\tdi (µm)\tG (µm)')
        print(f'lower bound :\t{(bds[0])[0]:.2g}\t{(self.bounds[1])[0]:.2g}\t\
{(bds[2])[0]:.3g}\t{(bds[3])[0]:.2g}')
        print(f'primary dim.:\t{sol[0]:.2g}\t{res.x[1]:.0g}\t{sol[2]:.3g}\t{sol[3]:.2g}')
        print(f'secondary dim.:\t{sol[4]:.2g}\t{res.x[5]:.0g}\t{sol[6]:.3g}\t{sol[7]:.2g}')
        print(f'upper bound :\t{(bds[0])[1]:.2g}\t{(self.bounds[1])[1]:.2g}\t\
{(bds[2])[1]:.3g}\t{(bds[3])[1]:.2g}')
class Transformer:
    """
        Create a transformator object with the specified geometry
        _primary and _secondary={'di':_di, 'n_turn':_n_turn, 'width':_width, 'gap':_gap}
        and calculated the associated electrical model
    """
    def __init__(self, _primary, _secondary, _eps_r=4.2, _dist=9, _dist_sub=1e9, _height_prim=4e-6, _height_sec=4e-6):
        self.prim = _primary
        self.second = _secondary
        self.dist = _dist
        self.dist_sub = _dist_sub
        self.eps_r = _eps_r
        self.height_prim = _height_prim
        self.height_sec = _height_sec
        self.model = {'lp':self.l_geo(True),
                      'rp':self.r_geo(True, 17e-9),
                      'ls':self.l_geo(False),
                      'rs':self.r_geo(False, 17e-9),
                      'cg':self.cc_geo(False),
                      'cm':self.cc_geo(True),
                      }
    def set_primary(self, _primary):
        """
            modify the top inductor and refresh the related model parameters
        """
        self.prim = _primary
        self.model['lp'] = self.l_geo(True)
        self.model['rp'] = self.r_geo(True, 17e-9)
        self.model['cg'] = self.cc_geo(False)
        self.model['cm'] = self.cc_geo(True)
    def set_secondary(self, _secondary):
        """
            modify the bottom inductor and refresh the related model parameters
        """
        self.second = _secondary
        self.model['ls'] = self.l_geo(False)
        self.model['rs'] = self.r_geo(False, 17e-9)
        self.model['cg'] = self.cc_geo(False)
        self.model['cm'] = self.cc_geo(True)
    def l_geo(self, _of_primary=True):
        """
            return the value of the distributed inductance of the described transformer
            if _of_primary, return the value of the top inductor
            else, return the value of the bottom inductor
        """
        k_1 = 2.25   #constante1 empirique pour inductance
        k_2 = 3.55   #constante2 empirique pour inductance
        if _of_primary:
            geo = self.prim
        else:
            geo = self.second
        outer_diam = geo['di']+2*geo['n_turn']*geo['width']+2*(geo['n_turn']-1)*geo['gap']
        rho = (geo['di']+outer_diam)/2
        density = (outer_diam-geo['di'])/(outer_diam+geo['di'])
        return k_1*4*np.pi*1e-7*geo['n_turn']**2*rho/(1+k_2*density)
    def cc_geo(self, _mutual=True):
        """
            return the value of the distributed capacitance of the described transformer
            if _mutual, return the capacitance between primary and secondary
            else, return the capacitance to the ground plane
        """
        if _mutual:
            dist = self.dist
        else:
            dist = self.dist_sub
        c_1 = 6.86344013   #constante1 empirique pour capacité
        c_2 = 5.24903708   #constante2 empirique pour capacité
        eps_0 = 8.85418782e-12
        n_t = self.prim['n_turn']
        return self.prim['width']*eps_0*self.eps_r*(c_1+c_2*(n_t-1))*self.prim['di']/dist
    def r_geo(self, _of_primary=True, rho=17e-10):
        """
            return the value of the resistance of the described transformer
        """
        c_1 = 6.86344013   #constante1 empirique pour capacité
        c_2 = 5.24903708   #constante2 empirique pour capacité
        if _of_primary:
            geo = self.prim
            height = self.height_prim
        else:
            geo = self.second
            height = self.height_sec
        return rho*(c_1+c_2*(geo['n_turn']-1))*geo['di']/(geo['width']*height)
    def generate_spice_model(self, k_ind):
        """
            Generate a equivalent circuit of a transformer with the given values
        """
        return f'Hybrid Coupler\n\n\
VIN		3	0	DC	0	AC	1\n\
RIN		3	IN	50\n\
ROUT	OUT	0	50\n\
RCPL	CPL	0	50\n\
RISO	ISO	0	50\n\n\
L1		IN	1	{self.model["lp"]:.3e}\n\
R1		1	OUT	{self.model["rp"]:.3e}\n\
L2		CPL	2	{self.model["ls"]:.3e}\n\
R2		2	ISO	{self.model["rs"]:.3e}\n\
K		L1	L2	{k_ind:.3n}\n\
CG1		IN	0	{self.model["cg"]/4:.3e}\n\
CG2		OUT	0	{self.model["cg"]/4:.3e}\n\
CG3		ISO	0	{self.model["cg"]/4:.3e}\n\
CG4		CPL	0	{self.model["cg"]/4:.3e}\n\
CM1		IN	CPL	{self.model["cm"]/2:.3e}\n\
CM2		ISO	OUT	{self.model["cm"]/2:.3e}\n\n'
# Other functions
def std_dev(mesured, targeted):
    """
        return the standard deviation bewteen an array_like of results and their references.
    """
    m_l = mesured.size
    if m_l == targeted.size:
        std_d = np.zeros((m_l, 1))
        for t_i in range(m_l):
            std_d[t_i] = np.abs((mesured[t_i]-targeted[t_i])/(mesured[t_i]+targeted[t_i]))**2
        return np.sqrt(np.sum(std_d))
    return 100
