from numpy import sqrt, pi

"""
Constants
"""

# µ0 : vacuum permeability
u0 = 4 * pi * 1e-7  # H/m
# c0 : light speed in vacuum
c0 = 299792458  # m/s
# ε0 : vacuum permittivity
eps0 = 8.8541878128e-12  # F/m
# vacuum impedance
eta0 = sqrt(u0 / eps0)  # Ohm

Nm_to_dBcm = 8.686 / 100
