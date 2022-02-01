from matplotlib.ticker import EngFormatter
from numpy import real, imag

Frequency = EngFormatter(unit="Hz")

__res = EngFormatter(unit="")


def Impedance(value):
    if imag(value) < 0:
        return __res(real(value)) + " - j" + __res(-imag(value)) + r" $\Omega$"
    return __res(real(value)) + " + j" + __res(imag(value)) + r" $\Omega$"

SI = EngFormatter(unit="")
