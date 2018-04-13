"""
.. module:: asound
    :platform: Windows
    :synopsis: Computes speed of sound in ISA 1962
"""

from math import sqrt
from .constants import *
from .temperature import temperature


def asound(h_m):
    """
    Speed of sound (m/s) up to 25 km (82021 ft).
    In : h in m
    Out : speed of sound in m/s
    """

    _T = temperature(h_m)
    _asound = sqrt(GAMMA * Rair * _T)

    return _asound
