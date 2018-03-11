# Ta.L.P.A. is a TAkeoff and Landing Performance Analyzer
# It allows to find maximum regulated weight for takeoff
# and landing given runways length (TORA, TODA, ASDA, LDA)
# and aircraft main characteristics.

from math import sqrt 
import aircraft
import airports
import isa
import FAA

if __name__ == '__main__':
    import menu.main

    acft, apt, rwy, qnh_hPa, T_degC = menu.main.build()




    # airports.database.buildDatabase()
    # apt, rwys = airports.extractAirportData('KBOS')
    #
    # print(apt)
    # for r in rwys:
    #     # print(r.length_ft)
    #     r_length = { 'TORA': r.length_ft, 'TODA': r.length_ft, 'ASDA': r.length_ft,
    #                  'LDA': r.length_ft, 'sigma': 1.0 }
    #     #RTOW = takeoffFAR23(r_length)
    #     RTOW = 0
    #     print( 'RWY {} RTOW {} (lb)'.format(r.id, RTOW) )
    #
    # # if FAR23:
    # #    RTOW = takeoffFAR23(apt)
    # #     print('RTOW (lb)',RTOW)
    #
    #
    #
    # #print( isa.pressure(1000) )
