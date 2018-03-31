# Ta.L.P.A. is a TAkeoff and Landing Performance Analyzer
# It allows to find maximum regulated weight for takeoff
# and landing given runways length (TORA, TODA, ASDA, LDA)
# and aircraft main characteristics.

from aircraft import Aircraft
import airports.database
import isa
import FAA.FAR25.performance

if __name__ == '__main__':
    import menu.main
    debug = True

    if debug:
        apt = airports.database.airport(id='LIPE', altitude=123.0, magvar=1.5)
        rwy = [airports.database.runway(id='12', hgd_t=116.75, length_ft=9179.0, type='Asphalt'),
               airports.database.runway(id='30', hgd_t=296.75, length_ft=9179.0, type='Asphalt')]
        qnh_hPa = 1013.15
        T_degC = 15.0
        acft = Aircraft.readConfiguration('aircrafts_debug.cfg', 'B738RAM')

        # acft.print()

    else:
        acft, apt, rwy, qnh_hPa, T_degC = menu.main.build()

    # Main Body section
    if acft.getString('certification') == 'FAR25':
        print( 'ICAO = {}\nQNH {} hPa TEMP {} degC\n'.format(apt.id, qnh_hPa, T_degC) )
        # TAKEOFF
        result = FAA.FAR25.performance.takeoff(acft, apt, rwy, qnh_hPa, T_degC)
        print( result )

        # CLIMB
        print( ' \\* CLIMB PERFORMANCE ANALYSIS *\\ \n' )
        RTOW = FAA.FAR25.performance.climb(acft, apt, rwy, qnh_hPa, T_degC)
        print('f    RTOW     FLAG')
        print('------------------')
        for f in sorted( RTOW.keys() ):
            print( '{:2d} {:6.0f} lb {}'.format(f,RTOW[f].W, RTOW[f].flag) )

        # LAND
        print('\n \\* LANDING PERFORMANCE ANALYSIS *\\ \n')
        RTOW = FAA.FAR25.performance.landing(acft, apt, rwy, qnh_hPa, T_degC)
        print('f    RTOW     FLAG')
        print('------------------')
        for f in sorted(RTOW.keys()):
            print('{:2d} {:6.0f} lb {}'.format(f, RTOW[f].W, RTOW[f].flag))
    elif acft.getString('certification') == 'FAR23':
        pass





