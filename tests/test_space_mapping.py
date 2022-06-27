from pytest import raises
from numpy import inf, array, round
import skrf as rf
from passive_auto_design.space_mapping import space_map
from passive_auto_design.units.constants import eps0
import passive_auto_design.components.lumped_element as lp

# definition of the goal (or target)
goal = {"C": 800e-12, "R": (0, 1)}

# list of the parameters use by the component model with initial value
par0 = {"rho/h": 1e-6, "eps/d": 3}

# list of the dimensions of the component
dim0 = {"l": 1e-3, "w": 1e-6}


def coarse_model(dim, par):
    """
    Definition of the coarse model.

    Returns
        dict
            should contain all the keys of the goal
    """

    cap = lp.Capacitor(area=dim["w"] * dim["l"], dist=1, eps_r=par["eps/d"])
    res = lp.Resistor(section=dim["w"], length=dim["l"], rho=par["rho/h"])
    achieved = {
        "C": cap.model["cap"],
        "R": res.model["res"],
    }
    return achieved


def fine_model(dim):
    """
    Definition of the fine model.

    Returns
        dict
            should contain all the keys of the goal
    """

    achieved = {
        "C": eps0 * 5 * dim["w"] * dim["l"],
        "R": 0.2 * dim["l"] / dim["w"],
    }
    return achieved


def test_std_dev():
    dim_f, par_f, goal_f = space_map(coarse_model, dim0, fine_model, par0, goal)
    assert round(par_f["rho/h"], 3) == 0.2
    assert round(par_f["eps/d"], 3) == 5
    assert round(goal_f["C"] * 1e12, 3) == 800
    assert goal_f["R"] < 1
