def findTOP23(sTOG):
    a = 0.009
    b = 4.9
    c = -sTOG
    delta = b * b - 4 * a * c
    if delta < 0:
        print('delta is negative')
    TOP23 = (-b + sqrt(delta)) / (2 * a)
    # print(TOP23)
    return TOP23


def landingFAR23(airport):
    sL = airport['LDA']


def takeoffFAR23(airport):
    # TORA is limiting.
    sTO = airport['TORA']
    sTOG = sTO / 1.66
    TOP23 = findTOP23(sTOG)
    RTOW = sqrt(TOP23 * aircraft.S * aircraft.P * aircraft.CLmaxTO)
    print('TORA', RTOW)
    if airport['TODA'] > airport['TORA']:
        # TODA is limiting
        sTO = airport['TODA']
        sTOG = sTO / 1.66
        # print(sTOG)
        if sTOG <= airport['TORA']:
            TOP23 = findTOP23(sTOG)
            RTOW = sqrt(TOP23 * aircraft.S * aircraft.P * aircraft.CLmaxTO)
            print('TODA', RTOW)

    return RTOW
