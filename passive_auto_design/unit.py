"""
Some function to format physical dimensions.
"""

from matplotlib.ticker import EngFormatter
from numpy import real, imag

"""
Format frequency to string.
"""
Frequency = EngFormatter(unit="Hz")

__res = EngFormatter(unit="")


def Impedance(value):
    """
    Format complex impedance to string with engineer format.
    """
    if imag(value) < 0:
        return __res(real(value)) + " - j" + __res(-imag(value)) + r" $\Omega$"
    return __res(real(value)) + " + j" + __res(imag(value)) + r" $\Omega$"


"""
Format number to string in engineer format without unit.
"""
SI = EngFormatter(unit="")
