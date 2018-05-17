import unittest
from aircraft import Aircraft
import inout.fsbuild.read as fsb

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.qnh_hPa = 1013.15
        self.T_degC = 15.0
        self.acft = Aircraft.readConfiguration('aircrafts.cfg', 'B738RAM')
        file_in = 'fsbroute.log'
        self.ofp_weight, self.ofp_route, self.ofp_fuel, self.old_ofp = fsb.read(file_in, 'kg')
        # apt = airports.database.airport(id='LIPE', altitude=123.0, magvar=1.5)
        # rwy = [airports.database.runway(id='12', hgd_t=116.75, length_ft=9179.0, type='Asphalt'),
        #       airports.database.runway(id='30', hgd_t=296.75, length_ft=9179.0, type='Asphalt')]


    def test_aspectratio(self):
        self.assertTrue( abs(self.acft.getValue('AR') - 10.258524107142858) <= 1.0e-6)

    def test_fsbuild_ofp_fuel(self):
        self.assertEqual(2159/0.453592, self.ofp_fuel['HOLD'], 'OFP HOLD FUEL (LB)')
        self.assertEqual(1133/0.453592, self.ofp_fuel['ALTN'], 'OFP ALTN FUEL (LB)')
        self.assertEqual(9934/0.453592, self.ofp_fuel['DEST'], 'OFP DEST FUEL (LB)')

if __name__ == '__main__':
    unittest.main()
