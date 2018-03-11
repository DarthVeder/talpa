from math import pow, exp
from .constants import *

def pressure(h_m):
    """
    Perssure (Pa) up to 25 km (82021 ft).
    In : h in m
    Out : pressure in Pa
    """

    h_ft = h_m/0.3048
    delta = 1.0
    if h_m <= hBL1_m:
        delta = pow( 1.0 - 6.8755856e-6*h_ft, 5.255863)
    elif h_m<= hBL2_m:
        delta = 0.223358 * exp(-4.80614e-5*(h_ft-36089.0))

    return delta*pSL

    
