import abc
from scipy.optimize import minimize

class SpaceMap(metaclass=abc.ABCMeta):
    def __init__(self):
        self.__par = {}
        self.__dim = {}
        self.__goal = {}
    
    @property
    def par(self):
        return self.__par
    @par.setter
    def par(self, key_val):
        self.__par.update(key_val)
        
    @property
    def dim(self):
        return self.__dim
    @dim.setter
    def dim(self, key_val):
        self.__dim.update(key_val)
    
    @property
    def goal(self):
        return self.__goal
    @goal.setter
    def goal(self, key_val):
        self.__goal.update(key_val)

    @abc.abstractmethod
    def coarse_model(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def fine_model(self):
        raise NotImplementedError

    def solve(self, maxiter=5):
        for i in range(maxiter):
            #find best solution according to coarse model
            res = minimize(self.__cost_coarse, list(self.dim.values()))
            self.dim = dict(zip(self.dim, res.x))
            #evaluate exact value using fine model
            fine_mod = self.fine_model()
            #alter coarse model paramaters to better match fine model results
            res = minimize(self.__refresh_coarse, list(self.par.values()), args=(fine_mod))
            self.par = dict(zip(self.par, res.x))
        return self.dim
    
    def __cost_coarse(self, d):
        dim = dict(zip(self.dim, d))
        coarse_mod = self.coarse_model(dim, self.par)
        err = 0
        for key, value in coarse_mod.items():
            err += abs((self.goal[key]-value)/(self.goal[key]+value))
        return err
    
    def __refresh_coarse(self, p, fine_mod):
        par = dict(zip(self.par, p))
        coarse_mod = self.coarse_model(self.dim, par)
        err = 0
        for key, value in coarse_mod.items():
            err += abs((fine_mod[key]-value)/(self.goal[key]+value))
        return err
