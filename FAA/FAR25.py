'''
Dimensioning FAR25 for:
- takeoff distance
- initial climb
- landing
- missed approach

Based on "Progetto di Velivoli", J. Roskam
'''

def takeoffDistance():
    # sTOFL = 37.5 * W/S|TO / (sigma*CLmaxTO*T/W|TO) = 37.5 W^2/(S*sigma*CLmaxTO*T)

    TOP25 = sTOFL / 37.5
    W = sqrt( TOP25*S*sigma*CLmaxTO*T )

    return W
