'''
Read an FSBUILD operative flight plan (ofp) stored in fsbroute.log and extracts departure, arrival and weights for the
flight.

Usage:

import fsbuild

ofp_weight, ofp_route, old_ofp = fsbuild.read(file)
'''

from log import logger

module_logger = logger.getChild('FSBUILD')

ofp_weight = {'PAYLOAD': -1, 'ZFW': -1, 'TOGWT': -1, 'LDGWT': -1}
ofp_fuel = {'TAXI': 0.0}
ofp_route = {}
ofp_new_data = {}

def read(file_in, unit='lb'):
    C_FACTOR = 1.0
    if unit == 'kg':
        C_FACTOR = 1.0/0.453592
    old_ofp = []
    module_logger.info('Reading OFP FSBUILD with unit {}'.format(unit))

    with open(file_in, 'r') as f:
        line_value_tom = False
        for line in f:
            # Storing old file data
            old_ofp.append(line)
            line = line.split()
            try:
                # Finding TOM and LAND Weights
                if not line_value_tom and 'TOGWT' in line:
                    next_line = f.readline().split()
                    ofp_weight['TOGWT'] = C_FACTOR * float(next_line[7])
                    ofp_weight['LDGWT'] = C_FACTOR * float(next_line[8])
                    line_value_tom = True
                for word in ['IFR', 'PAYLOAD', 'ZFW']:
                    if word in line:
                        idx_word = line.index(word)
                        if word == 'IFR':
                            trip_str = line[idx_word+1]
                            dep = trip_str.split('/')[0].split('-')[0]
                            arr = trip_str.split('/')[1].split('-')[0]
                            ofp_route['DEP'] = dep
                            ofp_route['ARR'] = arr
                        else:
                            ofp_weight[word] = C_FACTOR * float(line[idx_word+1])
                for word in ['TAXI', 'DEST', 'RESV', 'ALTN', 'HOLD', 'EXTRA']:
                    if word in line:
                        idx_word = line.index(word)
                        if word == 'DEST':
                            ofp_fuel[word] = C_FACTOR * float(line[idx_word+2])
                        else:
                            ofp_fuel[word] = C_FACTOR * float(line[idx_word+1])
            except ValueError:
                continue

    # Computing  tof fuel:
    tof = 0.0
    for key in ofp_fuel.keys():
        tof += ofp_fuel[key]
    ofp_fuel['TOF'] = tof - ofp_fuel['TAXI']

    return ofp_weight, ofp_route, ofp_fuel, old_ofp

    
def printOFPData():
    for k in ofp_weight.keys():
        print('{} : {}'.format(k, ofp_weight[k]))
    for k in ofp_route.keys():
        print('{} : {}'.format(k, ofp_route[k]))
    for k in ofp_fuel.keys():
        print('{} : {}'.format(k, ofp_fuel[k]))
    

def printToFile(file_out, text_to_print):
    string = ''.join([str(x) for x in text_to_print])
    with open(file_out, 'w') as f:
        f.write(string)

if __name__ == '__main__':
    file_in = r'C:\home\talpa\fsbroute.log'
    weight, route, fuel, old_text = read(file_in, 'kg')
    printOFPData()

    file_out = r'C:\home\talpa\fsbrouteNEW.log'
    printToFile(file_out, old_text)
