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
        PLTOM = FAA.FAR25.performance.takeoff(acft, apt, rwy, qnh_hPa, T_degC, unit)
        logger.debug('rwyID  flap  PLTOM ({})'.format(unit))
        for rwy_id, f in sorted(PLTOM.keys()):
            logger.debug('{:3s}      {:2d}   {:6.0f}'.format(rwy_id, f, PLTOM[(rwy_id, f)]))

        # CLIMB
        logger.debug(' //* CLIMB PERFORMANCE ANALYSIS *//')
        PLCLIMB = FAA.FAR25.performance.climb(acft, qnh_hPa, T_degC, unit)
        logger.debug('f    PLCLIMB ({}) FLAG'.format(unit))
        logger.debug('----------------------')
        for f in sorted(PLCLIMB.keys()):
            logger.debug('{:2d} {:6.0f} {}'.format(f, PLCLIMB[f].W, PLCLIMB[f].flag))

        # LAND
        logger.debug('//* LANDING PERFORMANCE ANALYSIS *//')
        PLLM = FAA.FAR25.performance.landing(acft, apt, rwy, qnh_hPa, T_degC, unit)
        logger.debug('f    PLLM ({})     FLAG'.format(unit))
        logger.debug('----------------------')
        for f in sorted(PLLM.keys()):
            logger.debug('{:2d} {:6.0f} {}'.format(f, PLLM[f].W, PLLM[f].flag))

        # Finding minimum takeoff mass allowed
        RTOM = acft.getValue('MTOM')
        for key in PLTOM.keys():
            if RTOM > PLTOM[key]:
                RTOM = PLTOM[key]
        for key in PLCLIMB.keys():
            weight, flag = PLCLIMB[key]
            if RTOM > weight:
                RTOM = weight
        TOM = acft.getValue('MLM')
        for key in PLLM.keys():
            weight, flag = PLLM[key]
            if TOM > weight:
                TOM = weight

        temp_RTOW = []
        temp_RTOW.append(acft.getValue('MZFM') + ofp_fuel['TOF'])
        temp_RTOW.append(acft.getValue('MTOM'))
        temp_RTOW.append(acft.getValue('MLM') + ofp_fuel['DEST'])
        RTOW = min(temp_RTOW)

        logger.info('ZFM LIM  MTOM LIM  MLM LIM')
        logger.info('{:6.0f}    {:6.0f}    {:6.0f}'.format(*temp_RTOW))
        logger.info('MIN: {:6.0f}'.format(RTOW))
    elif acft.getString('certification') == 'FAR23':
        pass




if __name__ == '__main__':
    logger.debug('Building menu')
    import menu.main
    debug = True
    read_ofp = True
    logger.debug('Run type: debug= %s; read_ofp= %s',debug, read_ofp)
    apt = []
    rwy = []

    if debug:
        qnh_hPa = 1013.15
        T_degC = 15.0
        acft = Aircraft.readConfiguration('aircrafts_debug.cfg', 'B738RAM')

        # acft.print()
        if read_ofp:
            # Reading OFP
            file_in = r'C:\home\talpa\fsbroute.log'
            ofp_weight, ofp_route, ofp_fuel, old_ofp = fsb.read(file_in, 'kg')
            fsb.printOFPData()
            airports.database.buildDatabase()
            for key in ofp_route.keys():
                apt_, rwy_ = airports.database.extractAirportData(ofp_route[key])
                apt.append(apt_)
                rwy.append(rwy_)
        else:
            apt = airports.database.airport(id='LIPE', altitude=123.0, magvar=1.5)
            rwy = [airports.database.runway(id='12', hgd_t=116.75, length_ft=9179.0, type='Asphalt'),
                   airports.database.runway(id='30', hgd_t=296.75, length_ft=9179.0, type='Asphalt')]

    else:
        acft, apt, rwy, qnh_hPa, T_degC = menu.main.build()

    for index, airport in enumerate(apt):
        findRegulatedMaximumWeights(acft, airport, rwy[index], ofp_weight, ofp_fuel)



