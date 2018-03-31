'''
Dimensioning FAR25 for:
- takeoff distance
- initial climb
- landing
- missed approach

Based on "Progetto di Velivoli", J. Roskam
'''
from collections import namedtuple
import isa.constants
from math import sqrt

g = 9.81 # m/s^2

def takeoff(acft, apt, rwy, qnh_hPa, T_degC):
    # sTOFL = 37.5 * W/S|TO / (sigma*CLmaxTO*T/W|TO) = 37.5 W^2/(S*sigma*CLmaxTO*T)

    to_flap = acft.takeoffFlaps()
    # Airport density ratio
    qnh_Pa = qnh_hPa * 100.0
    T_K = T_degC + 273.15
    sigma = isa.sigma(qnh_Pa, T_K)

    result = ' \\* TAKEOFF PERFORMANCE ANALYSIS *\\ \n'
    for f in to_flap:
        CLmaxTO =  1.2 #acft.getValue('CLmaxTO')
        S = acft.getValue('S')
        delta = qnh_hPa / 1013.15
        T = acft.Thrust(delta)
        MTOM = acft.getValue('MTOM')

        result += '\nFLAPS {}\n'.format(f)
        result += ' RWY   RTOW (lb)\n'
        result += '---------------\n'
        for r in rwy:
            TORA = r.length_ft
            TOP25 = TORA / 37.5
            W = sqrt( TOP25*S*sigma*CLmaxTO*T )
            if W > MTOM:
                W = MTOM
            result += '{:>3s}    {:>6.0f}\n'.format(r.id,W)

    return result


def climb(acft, apt, rwy, qnh_hPa, T_degC):
    # Preparing dictionary with RTOW for different configurations
    result = {}
    Data = namedtuple('Data', 'W flag')
    to_flap = acft.takeoffFlaps()
    for f in to_flap:
        result[f] = Data(W=1.0e8, flag='None')
    # Maybe flap 0 is not in takeoff setting, but I need it in enroute climb OEI
    if 0 not in to_flap:
        result[0] = Data(W=1.0e8, flag='None')

    # Retrieving main aircraft data
    MTOM = acft.getValue('MTOM')
    DOW = acft.getValue('DOM')
    delta = qnh_hPa/1013.15
    sigma = isa.sigma(qnh_hPa*100, T_degC+273.15)
    rho = sigma * isa.constants.rhoSLUK
    neng = acft.getValue('number_of_engines')
    S = acft.getValue('S')

    # Starting check on different climb OEI
    # print( 'CLIMB PERFORMANCE' )
    # print( 'Conditions: QNH= {:4.0f} hPa TEMP= {:2.1f} degC\n'.format(qnh_hPa, T_degC) )

    # FAR25.111 (OEI)
    # initial climb
    # print(' INITIAL CLIMB ')
    flag = 'INITIAL'
    initial_ramp_angle = {2: 0.012, 3: 0.015, 4: 0.017}
    gear = 0
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax/(1.2*1.2) # @ V2 = 1.2VS1g
        CD = acft.CD(CLTO,f,gear,1)
        E = CLTO/CD
        coeff = neng/(neng-1.0)*( 1./E + initial_ramp_angle[neng] )
        RTOW = acft.Thrust(delta)/coeff
        if RTOW < result[f].W:
            result[f] = Data(acft.checkWeight(RTOW), flag)
        # print( 'f {} RTOW {:6.0f} lb'.format(f,acft.checkWeight(RTOW)) )

    # climb trasition
    # FAR25.121 (OEI)
    # print(' CLIMB TRANSITION ')
    climb_transition_angle = {2: 0, 3: 0.003, 4: 0.005}
    gear = 1
    flag = 'TRANSITION'
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax/(1.1*1.1) # @ VLOF = 1.1VS1g
        CD = acft.CD(CLTO,f,gear,1)
        E = CLTO/CD
        coeff = neng/(neng-1.0)*( 1./E + climb_transition_angle[neng] )
        RTOW = acft.Thrust(delta)/coeff
        if RTOW < result[f].W:
            result[f] = Data(acft.checkWeight(RTOW), flag)
        # print( 'f {} RTOW {:6.0f} lb'.format(f, acft.checkWeight(RTOW)) )


    # second climb segment
    # print(' SECOND CLIMB SEGMENT ')
    second_climb_segment_angle = {2: 0.024, 3: 0.027, 4: 0.03}
    gear = 0
    flag = 'SECOND'
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax/(1.2*1.2) # @ V2 = 1.2VS1g
        CD = acft.CD(CLTO,f,gear)
        E = CLTO/CD
        coeff = neng/(neng-1.0)*( 1./E + second_climb_segment_angle[neng] )
        RTOW = acft.Thrust(delta)/coeff
        if RTOW < result[f].W:
            result[f] = Data(acft.checkWeight(RTOW), flag)
        # print( 'f {} RTOW {:6.0f} lb'.format(f, acft.checkWeight(RTOW)) )

    # enroute climb
    # print(' ENROUTE CLIMB ')
    enroute_climb_angle = {2: 0.012, 3: 0.015, 4: 0.017}
    gear = 0
    f = 0
    flag = 'ENROUTE'
    CLmax = acft.CLmax(f)
    CLTO = CLmax/(1.25*1.25) # @ 1.25*VS1g
    CD = acft.CD(CLTO,f,gear)
    E = CLTO/CD
    coeff = neng/(neng-1.0)*( 1./E + enroute_climb_angle[neng] )
    RTOW = acft.Thrust(delta)/coeff
    if RTOW < result[f].W:
        result[f] = Data(acft.checkWeight(RTOW), flag)

    # print( 'f {} RTOW {:6.0f} lb'.format(f, acft.checkWeight(RTOW)) )

    return result

def landing(acft, apt, rwy, qnh_hPa, T_degC):
    # Preparing dictionary with RTOW for different configurations
    result = {}
    Data = namedtuple('Data', 'W flag')
    land_flap = acft.landingFlaps()
    for f in land_flap:
        result[f] = Data(W=1.0e8, flag='None')

    # Retrieving main aircraft data
    MTOM = acft.getValue('MTOM')
    DOW = acft.getValue('DOM')
    delta = qnh_hPa / 1013.15
    sigma = isa.sigma(qnh_hPa * 100, T_degC + 273.15)
    rho = sigma * isa.constants.rhoSLUK
    neng = acft.getValue('number_of_engines')
    S = acft.getValue('S')

    # FAR25.119 (AEO)
    flag = 'BALKED LANDING AEO'
    initial_ramp_angle = {2: 0.032, 3: 0.032, 4: 0.032}
    gear = 1
    for f in land_flap:
        CLmax = acft.CLmax(f)
        CLLND = CLmax / (1.3 * 1.3)  # @ Vapp = 1.3VS1g
        CD = acft.CD(CLLND, f, gear)
        E = CLLND / CD
        coeff = (1. / E + initial_ramp_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < result[f].W:
            result[f] = Data(acft.checkLandingWeight(RTOW), flag)

    # FAR25.121 (OEI)
    flag = 'BALKED LANDING OEI'
    initial_ramp_angle = {2: 0.021, 3: 0.024, 4: 0.027}
    gear = 1
    for f in land_flap:
        CLmax = acft.CLmax(f)
        CLLND = CLmax / (1.5 * 1.5)  # @ Vapp = 1.5VS1g
        CD = acft.CD(CLLND, f, gear)
        E = CLLND / CD
        coeff = neng / (neng - 1.0) * (1. / E + initial_ramp_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < result[f].W:
            result[f] = Data(acft.checkWeight(RTOW), flag)

    return result