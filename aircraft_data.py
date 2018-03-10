import math
import configparser
# Aircraft data B738 from FSX

# Required data
DOM = 85710 # lb
MTOM = 146300 # lb
CLmax = 1.694
CD0 = 0.03515
dCLdf = 0.9
dCDdf = 0.09277
dCDgear = 0.04003
flaps = [0, 1, 2, 5, 10, 15, 25, 30, 40] # deg
S = 1344.0 # ft^2
b = 117.42 # ft
e = 0.75
aircraft_type = 'jet'

Pse = 3270*25520/(17.6*550.0) # HP/engine
Tse = 24200
number_of_engines = 2

# Derive data. DO NOT EDIT
CLmaxTO = CLmax + dCLdf*15/180.0*math.pi
CLmaxL = CLmax + dCLdf*30/180.0*math.pi
CLTO = CLmaxTO/1.21
AR = (b*b)/S
if aircraft_type == 'turboprop':
    P = Pse * number_of_engines
elif aircraft_type == 'jet':
    T = Tse * number_of_engines



class Aircraft:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('aircrafts.cfg')

    def selectAircraft(self):
        self._finalizeData()

    def _finalizeData(self):
        self.AR = (self.b * self.b) / self.S

    def print(self):
        print('Aircraft data:')
