from math import pow
from .constants import *

def temperature(h_m):
    """
    ISA Temperature (K) up to 25 km (82021 ft).
    In : h in m
    Out : height in m
    """

    h_ft = h_m/0.3048
    _T = TSL
    if h_m <= hBL1_m:
        _T = (1.0 - 6.8755856e-6*h_ft) * TSL
    elif h_m<= hBL2_m:
        _T = 216.65

    return _T
