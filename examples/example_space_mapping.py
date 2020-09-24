import passive_auto_design.space_mapping as sm

class Capacitor(sm.SpaceMap):
    def coarse_model(self, dim, par):
        model = {
            "C":par["eps"]*dim["w"]*dim["l"]/dim["d"],
            "R":par["rho.h"]*dim["w"]/dim["l"],
            }
        return model

    def fine_model(self):
        dim = self.dim
        model = {
            "C":5*dim["w"]*dim["l"]/dim["d"],
            "R":0.2*dim["w"]/dim["l"],
            }
        return model

cap = Capacitor()
cap.goal = {
    "C":800e-12,
    "R":0.1,
    }
cap.par = {
    "rho.h":1e-6,
    "eps":3,
    }
cap.dim = {
    "l":1e-3,
    "w":1e-6,
    "d":1e-6,
    }

print(cap.solve(2))
    