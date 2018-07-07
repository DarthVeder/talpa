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
import unit


def nicePrint(apt, rwy, rwy_vs_weight_lb_flap):
    ofp_perf_data = 'AIRPORT: {}  ALT {:5.0f} FT\n'.format(apt.id, apt.altitude)
    ofp_perf_data = ofp_perf_data + 'RWY    LENGTH FT      MAX WEIGHT {}  FLAP\n'.format(unit.get().upper())
    ofp_perf_data = ofp_perf_data + '-----------------------------------------\n'

    logger.info('AIRPORT: {}  ALT {:5.0f} FT'.format(apt.id, apt.altitude))
    logger.info('RWY    LENGTH FT      MAX WEIGHT {}  FLAP'.format(unit.get().upper()))
    logger.info('-----------------------------------------')
    for r in rwy:
        weight_lb, flap = rwy_vs_weight_lb_flap[r.id]
        weight = unit.check(weight_lb)
        logger.info('{:3s}    {:5.0f}          {:6.0f}         {:2.0f}'.format(r.id, r.length_ft, weight, flap))
        ofp_perf_data = ofp_perf_data + '{:3s}    {:5.0f}          {:6.0f}         {:2.0f}\n'.format(r.id, r.length_ft, weight, flap)

    return ofp_perf_data


def findRegulatedMaximumWeights(acft, apt, rwy, ofp_weight = None, ofp_fuel = None):
    # Main Body section
    if acft.getString('certification') == 'FAR25':
        logger.debug('//* TAKEOFF PERFORMANCE ANALYSIS *//')
        logger.debug('ICAO = {} QNH {} hPa TEMP {} degC'.format(apt.id, qnh_hPa, T_degC))
        # TAKEOFF
        logger.debug(' //* TAKEOFF ANALYSIS *//')
        rwy_vs_weight_lb_flap, flag_takeoff = FAA.FAR25.performance.takeoff(acft, apt, rwy, qnh_hPa, T_degC)
        ofp_perf_data = nicePrint(apt, rwy, rwy_vs_weight_lb_flap)

        # CLIMB
        logger.debug(' //* CLIMB PERFORMANCE ANALYSIS *//')
        climb_weight, climb_flap_setting, climb_flag = FAA.FAR25.performance.climb(acft, qnh_hPa, T_degC)
        logger.info('{:6.0f} {} {}'.format(climb_weight, climb_flap_setting, climb_flag))

        # LAND
        logger.debug('//* LANDING PERFORMANCE ANALYSIS *//')
        land_weight, land_flap_setting, land_flag = FAA.FAR25.performance.landing(acft, apt, rwy, qnh_hPa, T_degC)
        logger.info('{:6.0f} {:2.0f} {}'.format(land_weight, land_flap_setting, land_flag))

        # Finding minimum takeoff mass allowed
        # PLTOM = acft.getValue('MTOM')
        # if PLTOM > FLTOM:
        #     PLTOM = FLTOM
        # if PLTOM > WAT:
        #     PLTOM = WAT
        #
        # MLM = acft.getValue('MLM')
        # if MLM > PLLM:
        #         MLM = PLLM
        #
        # max_weights = []
        # max_weights.append(acft.getValue('MZFM') + ofp_fuel['TOF'])
        # max_weights.append(PLTOM)
        # max_weights.append(MLM + ofp_fuel['DEST'])
        # RTOW = min(max_weights)
        #
        # logger.info('MAX ZFM  MAX TOM  MAX LM')
        # logger.info('{:6.0f}    {:6.0f}    {:6.0f}'.format(*max_weights))
        # logger.info('MIN: {:6.0f}'.format(RTOW))
    elif acft.getString('certification') == 'FAR23':
        logger.error('FAR23 not yet implemented')
        exit(1)


if __name__ == '__main__':
    ui_unit = 'lb'
    logger.info('Setting unit to {}'.format(ui_unit))
    unit.set(ui_unit)
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
        fsbuild_unit = 'kg'
        ofp_weight, ofp_route, ofp_fuel, full_ofp = fsb.read(file_in, fsbuild_unit)
        # fsb.printOFPData()
        airports.database.buildDatabase()
        for key in ofp_route.keys():
            apt_, rwy_ = airports.database.extractAirportData(ofp_route[key])
            apt.append(apt_)
            rwy.append(rwy_)
    else:
        acft, apt, rwy, qnh_hPa, T_degC = menu.main.build()

    for index, airport in enumerate(apt):
        findRegulatedMaximumWeights(acft, airport, rwy[index], ofp_weight, ofp_fuel)

    for e in full_ofp:
        if 'M/H' in e:
            print('---------------------------------\n')
            print(e)
        else:
            print(e)



