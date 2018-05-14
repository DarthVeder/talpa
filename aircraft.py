from math import pi, pow, ceil, sqrt
import configparser
import re
import isa
from log import logger

module_logger = logger.getChild('aircraft')

class Aircraft:
    def __init__(self, config):
        self.logger = logger.getChild('Aircraft')
        self.logger.info('creating Aircraft')
        self.config = config
        self._finalizeData()

    @classmethod
    def readConfiguration(cls, xml_file, acft_id):
        logger.info('reading Aircraft configuration')
        config = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
        config.read(xml_file)

        acft = cls(config[acft_id])
        logger.info('done reading Aircraft configuration')

        return acft

    def aircraftClass(self):
        self.logger.info('Set Aicraft class ')
        S = self.getValue('S')
        MLM = self.getValue('MLM')
        f_deg = self.landingFlaps()[-1]
        CLLnd = self.CLmax(f_deg)
        rho = isa.densityh(0, 'slug/ft^3')
        kVat = ceil(1.3 * 0.592484 * sqrt((2 * MLM / S) / (CLLnd * rho)))
        acft_class = 'Not set'
        if kVat < 91:
            acft_class = 'A'
        elif 91 <= kVat <= 120:
            acft_class = 'B'
        elif kVat >= 121 and kVat <= 140:
            acft_class = 'C'
        elif 141 <= kVat <= 165:
            acft_class = 'D'
        elif kVat >= 166:
            acft_class = 'E'
        self.logger.debug('class: %s', acft_class)

        self.config['class'] = acft_class

    def getValue(self, svalue):
        """Returns an aircraft float value from a string variable"""
        return float(self.config[svalue])

    def getString(self, sstring):
        """Returns an aircraft string data from a string variable"""
        return self.config[sstring].strip('"\'')

    def _finalizeData(self):
        self.logger.debug('Finalizing data')
        b = self.getValue('b')
        S = self.getValue('S')
        self.config['AR'] = str((b * b) / S)
        self.aircraftClass()
        self.print()

    def print(self):
        self.logger.info('/** AIRCRAFT DATA **/')
        for k in self.config.keys():
            self.logger.info('%s = %s', k, self.config[k])
        self.logger.info('/** DONE **/')

    def Thrust(self, delta, derate=0.0):
        return (1.0 - derate / 100.0) * self.getValue('Tse') * self.getValue('number_of_engines')

    def Power(self, delta):
        return self.getValue('Pse') * self.getValue('number_of_engines')

    def takeoffFlaps(self):
        '''
        'flaps' keyword in aircrafts.cfg must have a 'T' or an 'L' for takeoff and landing flap setting.

        Example in aircraft.cfg:
        flaps = 0, 1, 2, 5T, 10T, 15TL, 25L, 30L, 40L

        '''
        self.logger.debug('Finding takeoff flaps setting(s)')
        sflaps = self.getString('flaps').split(',')
        to_flap = []
        regex = r"\d+"

        for f in sflaps:
            if 'T' in f:
                m = re.search(regex, f)
                to_flap.append(int(f[m.start():m.end()]))

        if len(to_flap) == 0:
            self.logger.critical('Aircraft is missing at least one takeoff flap setting (T)')
            exit(1)
        self.logger.debug('Takeoff flaps: %s', to_flap)

        return to_flap

    def landingFlaps(self):
        '''
        'flaps' keyword in aircrafts.cfg must have a 'T' or an 'L' for takeoff and landing flap setting.

        Example in aircraft.cfg:
        flaps = 0, 1, 2, 5T, 10T, 15TL, 25L, 30L, 40L

        '''
        sflaps = self.getString('flaps').split(',')
        land_flap = []
        regex = r"\d+"

        for f in sflaps:
            if 'L' in f:
                m = re.search(regex, f)
                land_flap.append(int(f[m.start():m.end()]))

        if len(land_flap) == 0:
            print('Aircraft is missing at least one landing flap setting (L)')
            exit(1)
        self.logger.debug('landing flaps: %s', land_flap)

        return land_flap

    def CLmax(self, f_deg):
        dCLdf = self.getValue('dCLdf')
        CLmax = self.getValue('CLmax') + dCLdf * (f_deg / 180.0 * pi)

        return CLmax

    def CD(self, CL, f_deg, gear, ige=0):
        CD0 = self.getValue('CD0')
        AR = self.getValue('AR')
        e = self.getValue('e')
        CDflaps = self.getValue('dCDdf') * (f_deg / 180.0 * pi)
        CDgear = self.getValue('dCDgear') * gear
        k = 1 / (pi * AR * e)
        if ige == 1:
            # Rymer formula 12.61 pag 304 for h/b = 1/2
            k = k * 33.0 * pow(0.5, 1.5) / (1 + 33 * pow(0.5, 1.5))

        return CD0 + CDflaps + CDgear + k * CL * CL

    def checkWeight(self, W):
        MTOM = self.getValue('MTOM')
        if W > MTOM:
            W = MTOM

        return W

    def checkLandingWeight(self, W):
        MLM = self.getValue('MLM')
        if W > MLM:
            W = MLM

        return W
