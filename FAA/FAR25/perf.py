'''
Dimensioning FAR25 for:
- takeoff distance
- initial climb
- landing
- missed approach

Based on "Progetto di Velivoli", J. Roskam
'''
import sys
import aircraft
import airports
import isa
import math

def takeoff(acft, apt, rwy, qnh_hPa, T_degC):
    # sTOFL = 37.5 * W/S|TO / (sigma*CLmaxTO*T/W|TO) = 37.5 W^2/(S*sigma*CLmaxTO*T)

    sigma = isa.density(qnh_hPa*100.0, T_degC + 273.15)
    CLmaxTO =  1.2 #acft.getValue('CLmaxTO')
    S = acft.getValue('S')
    delta = qnh_hPa / 1013.15
    T = acft.Thrust(delta)
    MTOM = acft.getValue('MTOM')

    print('RWY   RTOM (lb)')
    for r in rwy:
        TORA = r.length_ft
        TOP25 = TORA / 37.5
        W = math.sqrt( TOP25*S*sigma*CLmaxTO*T )
        if W > MTOM:
            W = MTOM
        print( '{} {}'.format(r.id,W) )

    return W


def climb():
    pass

def landing():
    pass