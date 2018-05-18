"""
Aircraft masses estimation using FAR25 for:
- takeoff distance
- initial climb
- landing
- missed approach

Based on "Progetto di Velivoli Parte I", J. Roskam
"""
import isa.constants
from math import sqrt
from log import logger
from ..FAR25 import Data

LB2KG = 0.453592
module_logger = logger.getChild('FAR25')


def checkUnit(W, unit):
    if unit != 'lb':
        W = W * LB2KG

    return W


def takeoff(acft, apt, rwy, qnh_hPa, T_degC, unit='lb'):
    # sTOFL = 37.5 * W/S|TO / (sigma*CLmaxTO*T/W|TO) = 37.5 W^2/(S*sigma*CLmaxTO*T)
    to_flap = acft.takeoffFlaps()
    # Airport density ratio
    qnh_Pa = qnh_hPa * 100.0
    T_K = T_degC + 273.15
    sigma = isa.sigma(qnh_Pa, T_K)

    weight_vs_rwy_id_flap = {}
    for f in to_flap:
        CLmaxTO = acft.CLmax(f)
        S = acft.getValue('S')
        delta = qnh_hPa / 1013.15
        T = acft.Thrust(delta)
        MTOM = acft.getValue('MTOM')

        for r in rwy:
            TORA = r.length_ft
            TOP25 = TORA / 37.5
            RTOW = sqrt(TOP25 * S * sigma * CLmaxTO * T)
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            weight_vs_rwy_id_flap[(r.id, f)] = RTOW

    module_logger.debug('rwyID  flap  FLTOM ({})'.format(unit))
    for rwy_id, f in sorted(weight_vs_rwy_id_flap.keys()):
        module_logger.debug('{:3s}      {:2d}   {:6.0f}'.format(rwy_id, f, weight_vs_rwy_id_flap[(rwy_id, f)]))

    weight_vs_flap = {}
    for key, weight in weight_vs_rwy_id_flap.items():
        rwy_id , f = key
        if f not in weight_vs_flap.keys():
            weight_vs_flap[f] = Data(W=weight, flag='')
        else:
            if weight < weight_vs_flap[f].W:
                weight_vs_flap[f] = Data(W=weight, flag='')

    max_allowed_weight, flap_max_allowed_weight = findMaxAllowedWeight(weight_vs_flap)
    module_logger.debug('Recommended  maximum weight  {} and flap setting {}'.format(max_allowed_weight, flap_max_allowed_weight))

    return max_allowed_weight, flap_max_allowed_weight


def climb(acft, qnh_hPa, T_degC, unit='lb'):
    # Preparing dictionary with RTOW for different configurations
    weight_vs_flap = {}
    to_flap = acft.takeoffFlaps()
    for f in to_flap:
        weight_vs_flap[f] = Data(W=acft.getValue('MTOM'), flag='NO LIM')
    # Maybe flap 0 is not in takeoff setting, but I need it in enroute climb OEI
    if 0 not in to_flap:
        weight_vs_flap[0] = Data(W=acft.getValue('MTOM'), flag='NO LIM')

    # Retrieving main aircraft data
    delta = qnh_hPa / 1013.15
    sigma = isa.sigma(qnh_hPa * 100, T_degC + 273.15)
    neng = acft.getValue('number_of_engines')

    # Starting check on different climb OEI
    # FAR25.111 (OEI)
    # initial climb
    initial_ramp_angle = {2: 0.012, 3: 0.015, 4: 0.017}
    gear = 0
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax / (1.2 * 1.2)  # @ V2 = 1.2VS1g
        CD = acft.CD(CLTO, f, gear, 1)
        E = CLTO / CD
        coeff = neng / (neng - 1.0) * (1. / E + initial_ramp_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = 'INITIAL'
            weight_vs_flap[f] = Data(RTOW, flag)

    # climb transition
    # FAR25.121 (OEI)
    climb_transition_angle = {2: 0, 3: 0.003, 4: 0.005}
    gear = 1
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax / (1.1 * 1.1)  # @ VLOF = 1.1VS1g
        CD = acft.CD(CLTO, f, gear, 1)
        E = CLTO / CD
        coeff = neng / (neng - 1.0) * (1. / E + climb_transition_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = 'TRANSITION'
            weight_vs_flap[f] = Data(RTOW, flag)

    # second climb segment
    second_climb_segment_angle = {2: 0.024, 3: 0.027, 4: 0.03}
    gear = 0
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax / (1.2 * 1.2)  # @ V2 = 1.2VS1g
        CD = acft.CD(CLTO, f, gear)
        E = CLTO / CD
        coeff = neng / (neng - 1.0) * (1. / E + second_climb_segment_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = 'SECOND'
            weight_vs_flap[f] = Data(RTOW, flag)

    # enroute climb
    enroute_climb_angle = {2: 0.012, 3: 0.015, 4: 0.017}
    gear = 0
    f = 0
    CLmax = acft.CLmax(f)
    CLTO = CLmax / (1.25 * 1.25)  # @ 1.25*VS1g
    CD = acft.CD(CLTO, f, gear)
    E = CLTO / CD
    coeff = neng / (neng - 1.0) * (1. / E + enroute_climb_angle[neng])
    RTOW = acft.Thrust(delta) / coeff
    if RTOW < weight_vs_flap[f].W:
        RTOW = acft.checkWeight(RTOW)
        RTOW = checkUnit(RTOW, unit)
        flag = 'ENROUTE'
        weight_vs_flap[f] = Data(RTOW, flag)

    # SID 3.3% OEI climb gradient
    sid_climb_angle = {2: 0.033, 3: 0.033, 4: 0.033}
    gear = 0
    for f in to_flap:
        CLmax = acft.CLmax(f)
        CLTO = CLmax / (1.2 * 1.2)  # @ V2 = 1.2VS1g
        CD = acft.CD(CLTO, f, gear)
        E = CLTO / CD
        coeff = neng / (neng - 1.0) * (1.0 / E + sid_climb_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = '3.3% SID'
            weight_vs_flap[f] = Data(RTOW, flag)

    module_logger.debug('f    WAT ({}) FLAG'.format(unit))
    module_logger.debug('----------------------')
    for f in sorted(weight_vs_flap.keys()):
        module_logger.debug('{:2d} {:6.0f} {}'.format(f, weight_vs_flap[f].W, weight_vs_flap[f].flag))

    max_allowed_weight, flap_max_allowed_weight = findMaxAllowedWeight(weight_vs_flap)

    return max_allowed_weight, flap_max_allowed_weight

def landing(acft, apt, rwy, qnh_hPa, T_degC, unit='lb'):
    # Preparing dictionary with RTOW for different configurations
    weight_vs_flap = {}
    land_flap = acft.landingFlaps()
    for f in land_flap:
        weight_vs_flap[f] = Data(W=1.0e8, flag='None')

    # Retrieving main aircraft data
    delta = qnh_hPa / 1013.15
    sigma = isa.sigma(qnh_hPa * 100, T_degC + 273.15)
    neng = acft.getValue('number_of_engines')

    # FAR25.119 (AEO)
    initial_ramp_angle = {2: 0.032, 3: 0.032, 4: 0.032}
    gear = 1
    for f in land_flap:
        CLmax = acft.CLmax(f)
        CLLND = CLmax / (1.3 * 1.3)  # @ Vapp = 1.3VS1g
        CD = acft.CD(CLLND, f, gear)
        E = CLLND / CD
        coeff = (1. / E + initial_ramp_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = 'BALKED LANDING AEO'
            weight_vs_flap[f] = Data(RTOW, flag)

    # FAR25.121 (OEI)
    initial_ramp_angle = {2: 0.021, 3: 0.024, 4: 0.027}
    gear = 1
    for f in land_flap:
        CLmax = acft.CLmax(f)
        CLLND = CLmax / (1.5 * 1.5)  # @ Vapp = 1.5VS1g
        CD = acft.CD(CLLND, f, gear)
        E = CLLND / CD
        coeff = neng / (neng - 1.0) * (1. / E + initial_ramp_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = 'BALKED LANDING OEI'
            weight_vs_flap[f] = Data(RTOW, flag)

    # MISSED APPROACH IFR GRADIENT (AEI)
    initial_ramp_angle = {2: 0.025, 3: 0.025, 4: 0.025}
    gear = 1
    for f in land_flap:
        CLmax = acft.CLmax(f)
        CLLND = CLmax / (1.3 * 1.3)  # @ Vapp = 1.3VS1g
        CD = acft.CD(CLLND, f, gear)
        E = CLLND / CD
        coeff = (1. / E + initial_ramp_angle[neng])
        RTOW = acft.Thrust(delta) / coeff
        if RTOW < weight_vs_flap[f].W:
            RTOW = acft.checkWeight(RTOW)
            RTOW = checkUnit(RTOW, unit)
            flag = 'IFR MISSED APPROACH AEO'
            weight_vs_flap[f] = Data(RTOW, flag)

    module_logger.debug('f    PLLM ({})     FLAG'.format(unit))
    module_logger.debug('----------------------')
    for f in sorted(weight_vs_flap.keys()):
        module_logger.debug('{:2d} {:6.0f} {}'.format(f, weight_vs_flap[f].W, weight_vs_flap[f].flag))

    max_allowed_weight, flap_max_allowed_weight = findMaxAllowedWeight(weight_vs_flap)

    return max_allowed_weight, flap_max_allowed_weight


def findMaxAllowedWeight(weight_vs_flap):
    max_allowed_weight = 0.0
    flap_max_allowed_weight = 0
    for f in weight_vs_flap.keys():
        if weight_vs_flap[f].W > max_allowed_weight:
            max_allowed_weight = weight_vs_flap[f].W
            flap_max_allowed_weight = f

    return max_allowed_weight, flap_max_allowed_weight
