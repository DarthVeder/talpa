"""
Ta.L.P.A. is a TAkeoff and Landing Performance Analyzer
It allows to find maximum regulated weights for takeoff
and landing given runways length (TORA, TODA, ASDA, LDA);
aircraft main characteristics and weather.
"""

from log import logger
from aircraft import Aircraft
import airports.database
import inout.fsbuild.read as fsb
import FAA.FAR25.performance

unit = 'lb'

def findRegulatedMaximumWeights(acft, apt, rwy, ofp_weight = None, ofp_fuel = None):
    # Main Body section
    if acft.getString('certification') == 'FAR25':
        logger.debug('//* TAKEOFF PERFORMANCE ANALYSIS *//')
        logger.debug('ICAO = {} QNH {} hPa TEMP {} degC'.format(apt.id, qnh_hPa, T_degC))
        # TAKEOFF
        logger.debug(' //* TAKEOFF ANALYSIS *//')
        FLTOM, TO_flap_setting = FAA.FAR25.performance.takeoff(acft, apt, rwy, qnh_hPa, T_degC, unit)

        # CLIMB
        logger.debug(' //* CLIMB PERFORMANCE ANALYSIS *//')
        WAT, CLB_flap_setting = FAA.FAR25.performance.climb(acft, qnh_hPa, T_degC, unit)

        # LAND
        logger.debug('//* LANDING PERFORMANCE ANALYSIS *//')
        PLLM, LND_flap_setting = FAA.FAR25.performance.landing(acft, apt, rwy, qnh_hPa, T_degC, unit)

        # Finding minimum takeoff mass allowed
        PLTOM = acft.getValue('MTOM')
        if PLTOM > FLTOM:
            PLTOM = FLTOM
        if PLTOM > WAT:
            PLTOM = WAT

        MLM = acft.getValue('MLM')
        if MLM > PLLM:
                MLM = PLLM

        max_weights = []
        max_weights.append(acft.getValue('MZFM') + ofp_fuel['TOF'])
        max_weights.append(PLTOM)
        max_weights.append(MLM + ofp_fuel['DEST'])
        RTOW = min(max_weights)

        logger.info('MAX ZFM  MAX TOM  MAX LM')
        logger.info('{:6.0f}    {:6.0f}    {:6.0f}'.format(*max_weights))
        logger.info('MIN: {:6.0f}'.format(RTOW))
    elif acft.getString('certification') == 'FAR23':
        logger.error('FAR23 not yet implemented')
        exit(1)




if __name__ == '__main__':
    logger.debug('Building menu')
    import menu.main
    debug = True
    logger.debug('Run type: debug = %s', debug)
    apt = []
    rwy = []

    if debug:
        qnh_hPa = 1013.15
        T_degC = 15.0
        acft = Aircraft.readConfiguration('aircrafts_debug.cfg', 'B738RAM')
        # Reading OFP
        file_in = 'fsbroute.log'
        ofp_weight, ofp_route, ofp_fuel, old_ofp = fsb.read(file_in, 'kg')
        fsb.printOFPData()
        airports.database.buildDatabase()
        for key in ofp_route.keys():
            apt_, rwy_ = airports.database.extractAirportData(ofp_route[key])
            apt.append(apt_)
            rwy.append(rwy_)
    else:
        acft, apt, rwy, qnh_hPa, T_degC = menu.main.build()

    for index, airport in enumerate(apt):
        findRegulatedMaximumWeights(acft, airport, rwy[index], ofp_weight, ofp_fuel)



