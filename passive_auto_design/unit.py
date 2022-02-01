from matplotlib.ticker import EngFormatter
from numpy import real, imag

Frequency = EngFormatter(unit="Hz")

__res = EngFormatter(unit="")


def Impedance(value):
    return __res(real(value)) + " " + __res(imag(value)) + "j $\Omega$"


SI = EngFormatter(unit="")
