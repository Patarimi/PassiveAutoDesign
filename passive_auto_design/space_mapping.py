"""
    Implementation of an aggressive space mapping algorithm for RF-design
"""
from scipy.optimize import minimize

def space_map(coarse_model, dim0, fine_model, par0, goal, maxiter=5):
    dim = dim0
    par = par0
    fine_mod = goal
    for i in range(maxiter):
        #evaluate exact value using fine model
        fine_mod = fine_model(dim)
        #alter coarse model paramaters to better match fine model results
        res = minimize(__refresh_coarse, __tolist(par), method='L-BFGS-B',
                       args=(par0.keys(), dim, coarse_model, fine_mod))
        par = __todict(par0.keys(), res.x)
        #find best solution according to coarse model
        res = minimize(__cost_coarse, __tolist(dim), method='Powell',
                       args=(dim0.keys(), par, coarse_model, goal))
        dim = __todict(dim0.keys(), res.x)
    return (dim, par, fine_mod)

def __cost_coarse(dim_values, dim_keys, par, coarse_model, goal):
    _dim = __todict(dim_keys, dim_values)
    coarse_mod = coarse_model(_dim, par)
    return cost_calc(coarse_mod, goal)

def __refresh_coarse(par_values, par_keys, dim, coarse_model, fine_mod):
    _par = __todict(par_keys, par_values)
    coarse_mod = coarse_model(dim, _par)
    return cost_calc(coarse_mod, fine_mod)

def cost_calc(perf_list, goal_list, weight_list=None):
    if weight_list is None:
        weight_list = [1]*len(goal_list.values())
    cost = 0
    for itern, keys in enumerate(goal_list.keys()):
        perf = perf_list[keys]
        goal = goal_list[keys]
        if type(goal) is tuple:
            err_min = max((perf-goal[0])/(goal[0] if goal[0]!=0 else 1), 0)
            err_max = max((goal[1]-perf)/(goal[1] if goal[1]!=0 else 1), 0)
            err = err_min + err_max
        else:
            err = (perf-goal)/(goal if goal!=0 else 1)
        cost += weight_list[itern]*err**2
    return cost

def __todict(keys, values):
    return dict(zip(keys, values))

def __tolist(dicts):
    return list(dicts.values())
