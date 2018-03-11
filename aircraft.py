import math
import configparser

class Aircraft:
    def __init__(self, config):
        self.config = config
        self._finalizeData()

    def getValue(self, svalue):
        '''Returns an aircraft float value from a string variable'''
        return float( self.config[svalue] )

    def selectAircraft(self):
        self._finalizeData()

    def _finalizeData(self):
        b = self.getValue('b')
        S = self.getValue('S')
        self.AR = (b * b) / S

    def print(self):
        print('Aircraft data:')
        for k in self.config.keys():
            print( '{}={}'.format(k,self.config[k]) )

        print( [int(x) for x in self.config['flaps'].split(',') ] )

    def Thrust(self, h_ft):
        return self.getValue('Tse') * self.getValue('number_of_engines')

    def Power(self, h_ft):
        return self.getValue('Pse') * self.getValue('number_of_engines')
