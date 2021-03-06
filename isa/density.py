from math import pow, exp
from .constants import *


def densityh(h_m, unit='kg/m^3'):
    """
    Density (kg/m^3) up to 25 km (82021 ft).
    In : h in m
    Out : density in kg/m^3 or UK unit slug/ft^3
    """

    h_ft = h_m/0.3048
    sigma = 1.0
    if h_m <= hBL1_m:
        sigma = pow(1.0 - 6.8755856e-6*h_ft, 4.255863)
    elif h_m <= hBL2_m:
        sigma = 0.297069 * exp(-4.80614e-5*(h_ft-36089.0))

    if unit == 'kg/m^3':
        return sigma*rhoSL
    elif unit == 'slug/ft^3':
        return sigma*rhoSLUK

    
def sigma(p_Pa, T_K):
    """
    Sigma [1] returns density/densitySL from equation of state.
    In : p [P]a, T [K]
    Out : sigma [1]
    """
    rho_SI = p_Pa / (Rair*T_K)

    return rho_SI/rhoSL


def density(delta, teta, unit):
    sigma = delta/teta
    if unit == 'kg/m^3':
        return sigma*rhoSL
    elif unit == 'slug/ft^3':
        return sigma*rhoSLUK
