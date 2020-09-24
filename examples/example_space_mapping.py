import space_map as sm

class Capacitor(sm.SpaceMap):
    def coarse_model(self, d, p):
        model = {
            "C":p["eps"]*d["w"]*d["l"]/d["d"],
            "R":p["rho.h"]*d["w"]/d["l"],
            }
        return model

    def fine_model(self):
        d = self.dim
        model = {
            "C":5*d["w"]*d["l"]/d["d"],
            "R":0.2*d["w"]/d["l"],
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
    