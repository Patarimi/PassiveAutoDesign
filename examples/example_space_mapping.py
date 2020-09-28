"""
    Space_mapping module implementation example

"""
from passive_auto_design.space_mapping import space_map

#definition of the goal (or target)
goal={"C":800e-12, "R":(0, 1)}

#list of the parameters use by the component model
par0={"rho/h":1e-6, "eps/d":3}

#list of the dimensions of the component
dim0={"l":1e-3, "w":1e-6,}

def coarse_model(dim, par):
    """
    Definition of the coarse model.

    Returns
        dict
            should contain all the keys of the goal
    """
    import passive_auto_design.components.lumped_element as lp
    
    cap = lp.Capacitor(area=dim["w"]*dim["l"], dist=1, eps_r=par["eps/d"])
    res = lp.Resistor(section=dim["w"], length=dim["l"], rho=par["rho/h"])
    achieved = {
        "C":cap.par["cap"],
        "R":res.par["res"],
        }
    return achieved

def fine_model(dim):
    """
    Definition of the fine model.

    Returns
        dict
            should contain all the keys of the goal
    """
    from passive_auto_design.special import eps0

    achieved = {
        "C":eps0*5*dim["w"]*dim["l"],
        "R":0.2*dim["l"]/dim["w"],
        }
    return achieved

dimf, parf, goalf = space_map(coarse_model, dim0, fine_model, par0, goal)