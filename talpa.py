# Ta.L.P.A. is a TAkeoff and Landing Performance Analyzer
# It allows to find maximum regulated weight for takeoff
# and landing given runways length (TORA, TODA, ASDA, LDA)
# and aircraft main characteristics.


import aircraft
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
        T_degC = 35.0
        acft = aircraft.Aircraft.readConfiguration('aircrafts_debug.cfg', 'B738RAM')

    else:
        acft, apt, rwy, qnh_hPa, T_degC = menu.main.build()

    # Main Body section
    if acft.getString('type') == 'jet':
        print( 'ICAO = {}\nQNH {} hPa TEMP {} degC'.format(apt.id, qnh_hPa, T_degC) )
        # TAKEOFF
        result = FAA.FAR25.performance.takeoff(acft, apt, rwy, qnh_hPa, T_degC)
        print( result )

        # CLIMB
        RTOW = FAA.FAR25.performance.climb(acft, apt, rwy, qnh_hPa, T_degC)
        print('f    RTOW     FLAG')
        for f in sorted( RTOW.keys() ):
            print( '{:2d} {:6.0f} lb {}'.format(f,RTOW[f].W, RTOW[f].flag) )

        # LAND
        RTOW = FAA.FAR25.performance.landing(acft, apt, rwy, qnh_hPa, T_degC)
        print('f    RTOW     FLAG')
        for f in sorted(RTOW.keys()):
            print('{:2d} {:6.0f} lb {}'.format(f, RTOW[f].W, RTOW[f].flag))
    elif acft.getString('type') == 'turboprop':
        pass
    elif acft.getString('type') == 'propeller':
        pass




