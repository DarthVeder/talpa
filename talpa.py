# Ta.L.P.A. is a TAkeoff and Landing Performance Analyzer
# It allows to find maximum regulated weight for takeoff
# and landing given runways length (TORA, TODA, ASDA, LDA)
# and aircraft main characteristics.

from math import sqrt 
import aircraft_data
import airports
import isa

FAR23 = True
FAR25 = False

# airport = { 'TORA': 500, 'TODA': 2700, 'ASDA': 2500, 'LDA': 2500,\
#            'sigma': 1.0 }


def findTOP23(sTOG):
    a = 0.009
    b = 4.9
    c = -sTOG
    delta = b*b - 4*a*c
    if delta<0:
        print('delta is negative')            
    TOP23 = (-b + sqrt(delta))/(2*a)
    # print(TOP23)
    return TOP23


def landingFAR23(airport):
    sL = airport['LDA']
    

def takeoffFAR23(airport):
    # TORA is limiting.
    sTO = airport['TORA']
    sTOG = sTO/1.66
    TOP23 = findTOP23(sTOG)
    RTOW = sqrt(TOP23*aircraft_data.S*aircraft_data.P*aircraft_data.CLmaxTO)
    print('TORA',RTOW)
    if airport['TODA'] > airport['TORA']:
        # TODA is limiting
        sTO = airport['TODA']
        sTOG = sTO/1.66
        # print(sTOG)
        if sTOG <= airport['TORA']:
            TOP23 = findTOP23(sTOG)
            RTOW = sqrt(TOP23*aircraft_data.S*aircraft_data.P*aircraft_data.CLmaxTO)
            print('TODA',RTOW)

    return RTOW

if __name__ == '__main__':
    airports.database.buildDatabase()
    apt, rwys = airports.extractAirportData('KBOS')

    print(apt)
    for r in rwys:
        # print(r.length_ft)
        r_length = { 'TORA': r.length_ft, 'TODA': r.length_ft, 'ASDA': r.length_ft,
                     'LDA': r.length_ft, 'sigma': 1.0 }
        #RTOW = takeoffFAR23(r_length)
        RTOW = 0
        print( 'RWY {} RTOW {} (lb)'.format(r.id, RTOW) )
    
    # if FAR23:
    #    RTOW = takeoffFAR23(apt)
    #     print('RTOW (lb)',RTOW)
    


    #print( isa.pressure(1000) )
