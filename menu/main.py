'''
Menu for choosing talpa options:
1 Select aircraft
    1.1 Lists ...
    ...
    1.n Next
    1.n+1 Previous
    1.n+2 Back
    Selection happens by choosing appropriate aircraft
2 Select Airport
    2.1 Insert ICAO airport
    2.2 Wind Dir (T) / Speed (kt)
    2.3 QNH
    2.4 Compute performances (print file ICAO_acft.dat)
    2.5 Back
3 Exit
'''

import sys
import configparser
import os

sys.path.append('../')
import aircraft
import airports

AIRCRAFT = 1
AIRPORT  = 2
COMPUTE  = 3
EXIT     = 4
main_menu = {AIRCRAFT: 'Select Aircraft', AIRPORT: 'Select Airport', \
             COMPUTE: 'Perform Analysis', EXIT: 'Exit'}

ICAO = 1
QNH = 2
TEMP = 3
BACK = 4
airport_menu = {ICAO: 'Select ICAO', QNH: 'Set QNH', TEMP: 'Set Temperature', \
                BACK: 'Back'}

def checkChoice(uchoice):
    '''Checks that the user choice is a number. Returns the choice number'''
    while not uchoice.isdigit():
        print('Choice MUST be a number')
        uchoice = input('Choice: ')

    return int(uchoice)

def build():
    '''Returns: if aircraft is set, airport is set and performance computation is required,
    it returns the following tupla:
    (acft, apt, rwy, qnh_hPa, T_degC)
    '''
    in_menu = True
    aircraft_is_set = False
    airport_is_set = False
    qnh_hPa = 1013.15
    T_degC = 15.0

    while in_menu:
        for (key, choice) in main_menu.items():
            print( '{} {}'.format(key, choice) )

        uchoice = input('Choice: ')
        # Processing user choice
        uchoice = checkChoice(uchoice)

        # Calling required menu's voice
        if uchoice == AIRPORT:
            (apt, rwy, qnh_hPa, T_degC) = airportMenu()
            airport_is_set = True
        elif uchoice == AIRCRAFT:
            acft_config = aircraftMenu()
            acft = aircraft.Aircraft( acft_config )
            acft.print()
            aircraft_is_set = True
        elif uchoice == COMPUTE:
            if airport_is_set and aircraft_is_set:
                return (acft,apt, rwy, qnh_hPa, T_degC)
            else:
                if not airport_is_set:
                    print('Airport not set')
                if not aircraft_is_set:
                    print('Aircraft not set')
        elif uchoice == EXIT:
            in_menu = False
        else:
            print('Choice not yet implemented')

def airportMenu():
    in_menu = True
    airport_is_set = False
    qnh_hPa = 1013.15
    T_degC = 15.0

    while in_menu:
        for (key, choice) in airport_menu.items():
            print( '{} {}'.format(key, choice) )

        uchoice = input('Choice: ')
        # Processing user choice
        uchoice = checkChoice(uchoice)

        if uchoice == ICAO:
            icao = input('ICAO: ')
            airports.database.buildDatabase()
            apt, rwy = airports.extractAirportData(icao.upper())
            airport_is_set = True
        elif uchoice == QNH:
            qnh_hPa = input('hPa: ')
        elif uchoice == TEMP:
            T_degC = input('degC: ')
        elif uchoice == BACK:
            in_menu = False

    return (apt, rwy, qnh_hPa, T_degC)


def aircraftMenu():
    config = configparser.ConfigParser(inline_comment_prefixes=(';','#'))
    if 'aircrafts' in sys.modules:
        print('Read A')
        config.read( os.path.dirname(sys.modules['aircrafts']) + r'\data\aircrafts.cfg' )
    else:
        print('Read B')
        config.read(r'..\data\aircrafts.cfg')

    in_menu = True
    section = config.sections()
    nrows = 2 # max number of aircraft in each submenu
    nsplit = len(section)//nrows
    i = 0 # index for viewing the complete list of aircrafts

    while in_menu:

            for (n,a) in enumerate(section[nrows*i:nrows*(i+1)]):
                print(n,a)

            uchoice = input('{} Next {} Previous {} Back: '.format(nsplit, nsplit+1, nsplit+2))
            uchoice = checkChoice(uchoice)
            if uchoice == nsplit:
                if i<nsplit:
                    i = i + 1
            elif uchoice == (nsplit+1):
                if i>0:
                    i = i - 1
            elif uchoice == (nsplit+2):
                in_menu = False
            else:
                return config[ section[uchoice] ]
                in_menu = False


if __name__ == '__main__':
    build()