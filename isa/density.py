from math import pow, exp
from .constants import *

def density(h_m):
    """
    Density (kg/m^3) up to 25 km (82021 ft).
    In : h in m
    Out : density in kg/m^3
    """

    h_ft = h_m/0.3048
    sigma = 1.0
    if h_m <= hBL1_m:
        sigma = pow( 1.0 - 6.8755856e-6*h_ft, 4.255863)
    elif h_m<= hBL2_m:
        sigma = 0.297069 * exp(-4.80614e-5*(h_ft-36089.0))

    return sigma*rhoSL

    
def density(p_Pa, T_K):
    rho_SI = p_Pa / (Rair*T_K)

    return rho_SI
