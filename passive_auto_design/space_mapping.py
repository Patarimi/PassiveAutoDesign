"""
Implementation of an aggressive space mapping algorithm for RF-design
"""
import functools
from scipy.optimize import minimize


def space_map(coarse_model, dim0, fine_model, par0, goal, maxiter=5):
    """
    Optimization function for space mapping algorithm.

    Parameters
    ----------
    coarse_model : fun
        function evaluating the coarse model goals
        for a set of dimensions (dim) and parameters (par)
    dim0 : dict
        initial dimensions of the component
    fine_model : fun
        function evaluating the fine model goals
        for a set of dimensions (dim)
    par0 : dict
        initial parameters of the component coarse model
    goal : dict
        set of goal targeted by the algorithm
    maxiter : int, optional
        maximal number of iteration. The default is 5.

    Returns
    -------
    dim : dict
        final dimension of the component.
    par : dict
        final parameters of the component model.
    fine_mod : dict
        achieved goal.

    """
    dim = dim0
    par = par0
    achieved_goal = goal
    for i in range(maxiter):
        # evaluate exact value using fine model
        achieved_goal = fine_model(dim)
        # alter coarse model parameters to better match fine model results
        res = minimize(
            __refresh_coarse,
            __totuple(par),
            method="L-BFGS-B",
            args=(par0.keys(), dim, coarse_model, achieved_goal),
        )
        par = __todict(par0.keys(), res.x)
        # find best solution according to coarse model
        res = minimize(
            __cost_coarse,
            __totuple(dim),
            method="Powell",
            args=(dim0.keys(), par, coarse_model, goal),
        )
        dim = __todict(dim0.keys(), res.x)
    return dim, par, achieved_goal


def __cost_coarse(dim_values, dim_keys, par, coarse_model, goal):
    _dim = __todict(dim_keys, dim_values)
    coarse_mod = coarse_model(_dim, par)
    return cost_calc(__totuple(coarse_mod), __totuple(goal))


def __refresh_coarse(par_values, par_keys, dim, coarse_model, fine_mod):
    _par = __todict(par_keys, par_values)
    coarse_mod = coarse_model(dim, _par)
    return cost_calc(__totuple(coarse_mod), __totuple(fine_mod))


@functools.lru_cache()
def cost_calc(perf_list, goal_list, weight_list=None):
    """
    return the normalize standard deviation between the perf_list and the goal_list

    Parameters
    ----------
    perf_list : tuple of float
        list of the performances achieved.
    goal_list : tuple of float
        list of the goal to be achieved. If one value is given, the goal is a point. If two, the goal is an interval.
    weight_list : tuple of float, optional
        weightning of the goals. If set to None, all the weight are set to one.

    Returns
    -------
    cost : float
        cost value

    """
    if weight_list is None:
        weight_list = [1] * len(goal_list)
    cost = 0
    for itern, goal in enumerate(goal_list):
        perf = perf_list[itern]
        goal = goal_list[itern]
        if isinstance(goal, tuple):
            err_min = max((perf - goal[0]) / (goal[0] if goal[0] != 0 else 1), 0)
            err_max = max((goal[1] - perf) / (goal[1] if goal[1] != 0 else 1), 0)
            err = err_min + err_max
        else:
            err = (perf - goal) / (goal if goal != 0 else 1)
        cost += weight_list[itern] * err ** 2
    return cost


def __todict(keys, values):
    return dict(zip(keys, values))


def __totuple(dicts):
    return tuple(dicts.values())
