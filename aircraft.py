import math
import configparser

class Aircraft:
    def __init__(self, config):
        self.config = config
        self._finalizeData()

    @classmethod
    def readConfiguration(cls, xml_file, acft_id):
        config = configparser.ConfigParser(inline_comment_prefixes=(';', '#'))
        config.read(xml_file)
        #print(config.sections())
        #for k in config[acft_id].keys():
        #    print(k)

        acft = cls(config[acft_id])
        return acft

    def getValue(self, svalue):
        '''Returns an aircraft float value from a string variable'''
        return float( self.config[svalue] )

    def getString(self, sstring):
        '''Returns an aircraft string datafrom a string variable'''
        return self.config[sstring].strip('"\'')


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

    def Thrust(self, delta):
        return self.getValue('Tse') * self.getValue('number_of_engines')

    def Power(self, delta):
        return self.getValue('Pse') * self.getValue('number_of_engines')

    def takeoffFlaps(self):
        pass

    def landingFlaps(self):
        pass
