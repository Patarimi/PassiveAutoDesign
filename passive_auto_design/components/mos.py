# CSM Model

import numpy as np
import matplotlib.pyplot as plt

# constants
q = 1.602176634e-19  # C
k = 1.380649e-23  # J/K
eps0 = 8.8541878128e-12  # F/m

Temp = 300  # K
N = 1e17  # atoms/cm3
t_ox = 5e-9  # m
mu_Cox = 3.45e-4  # A/V²
U_t = k * Temp / q  # V


def gamma(c_ox: float, N_atom: float):
    """
    body effect parameter
    """
    eps_si = 11.5 * eps0
    return 50 * np.sqrt(2 * q * eps_si * N_atom) / c_ox


def f_psi(psi: float, V_g: float):
    """
    function that link bulk potential and drain current
    """
    ga = gamma(mu_Cox, N)
    return (
        -0.5 * psi ** 2
        - (2 / 3) * ga * (psi ** 1.5)
        + (V_g + U_t) * psi
        + ga * U_t * (psi ** 0.5)
    )


def I_d(width: float, length: float, psi_ss, psi_sd, v_g):
    """
    drain current
    """
    beta = mu_Cox * width / length
    return beta * (f_psi(psi_sd, v_g) - f_psi(psi_ss, v_g))


def phi_b(N: float, n_i: float):
    """
    bulk potential
    """
    return U_t * np.log(N / n_i)


def V_non_eq(psi_s: float, V_g: float):
    """
    non-equilibrium voltage
    """
    ga = gamma(mu_Cox, N)
    n_i = 1e15
    phib = phi_b(N, n_i)
    return -U_t * np.log((((V_g - psi_s) / ga) ** 2 - psi_s) / U_t) + psi_s - 2 * phib


VG = np.arange(1.5, 3.1, 0.5)
psi_s = np.logspace(-11, 0, 101)

for vg in VG:
    ga = gamma(mu_Cox, N)
    psi_max = (np.sqrt(0.25 * ga ** 2 + vg) - ga / 2) ** 2
    print(f"$\gamma$: {ga}, $\psi_Smax$: {psi_max}")
    psi_swp = psi_max - psi_s
    plt.plot(V_non_eq(psi_swp, vg), psi_swp, label=f"VG={vg} V")
plt.legend()
plt.xlabel("V (B)")
plt.ylabel(r"$\psi_S$ (B)")
plt.grid()


plt.figure()
VD = np.arange(0, 2, 0.1)
VG = np.arange(0.5, 2.1, 0.25)
width = 65e-9
length = 10e-6
for vg in VG:
    plt.plot(VD, I_d(width, length, VD, 0, vg), label=f"VG={vg} V")
plt.legend()
plt.grid()
