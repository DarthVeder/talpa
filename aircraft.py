from math import pi, pow
import configparser
import re

class Aircraft:
    def __init__(self, config):
        self.config = config
        self._finalizeData()

    @classmethod
    def readConfiguration(cls, xml_file, acft_id):
        config = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
        config.read(xml_file)

        acft = cls(config[acft_id])
        return acft

    def getValue(self, svalue):
        '''Returns an aircraft float value from a string variable'''
        return float( self.config[svalue] )

    def getString(self, sstring):
        '''Returns an aircraft string data from a string variable'''
        return self.config[sstring].strip('"\'')


    # def selectAircraft(self):
    #     self._finalizeData()

    def _finalizeData(self):
        b = self.getValue('b')
        S = self.getValue('S')
        self.AR = (b * b) / S

    def print(self):
        print('Aircraft data:')
        for k in self.config.keys():
            print( '{}={}'.format(k,self.config[k]) )

        print( 'Takeoff Flaps setting(s) {}'.format([x for x in self.takeoffFlaps() ]) )
        print( 'Landing Flaps setting(s) {}'.format([x for x in self.landingFlaps() ]) )

    def Thrust(self, delta, derate=0.0):
        return (1.0-derate/100.0) *self.getValue('Tse') * self.getValue('number_of_engines')

    def Power(self, delta):
        return self.getValue('Pse') * self.getValue('number_of_engines')

    def takeoffFlaps(self):
        sflaps = self.getString('flaps').split(',')
        to_flap = []
        regex = r"\d+"

        for f in sflaps:
            if 'T' in f:
                m = re.search(regex,f)
                to_flap.append( int(f[m.start():m.end()]) )

        if len(to_flap) == 0:
            print('Aircraft is missing at least one takeoff flap setting (T)')
            exit(1)

        return to_flap

    def landingFlaps(self):
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

        return land_flap

    def CLmax(self, f_deg):
        dCLdf = self.getValue('dCLdf')
        CLmax = self.getValue('CLmax') + dCLdf * (f_deg/180.0*pi)

        return CLmax

    def CD(self, CL, f_deg, gear, ige=0):
        CD0 = self.getValue('CD0')
        CDflaps = self.getValue('dCDdf') * (f_deg/180.0*pi)
        CDgear = self.getValue('dCDgear') * gear
        k = 1 / (pi*self.AR*self.getValue('e'))
        if ige == 1:
            # Rymer formula 12.61 pag 304 for h/b = 1/2
            k = k * 33.0 * pow(0.5,1.5) / ( 1 + 33*pow(0.5,1.5) )

        return CD0+CDflaps+CDgear+k*CL*CL

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