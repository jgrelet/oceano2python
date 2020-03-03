import unittest
import toml

'''
Run all test_* in dir test:
> python -m unittest  discover tests -v
> python -m unittest  discover -s tests -p 'test_*.py' -v
'''


class testConfig(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests."""
        self.cfg = toml.load('tests/test.toml')
        
        self.glob = {'author': 'jgrelet IRD March 2019 PIRATA-FR29 cruise',
                     'debug': False, 'echo': True, 'codeRoscop': 'C:\git\python\oceano2python\code_roscop.csv',
                    'ascii': "ascii", 'netcdf': "netcdf", 'odv': "odv"}
        
        self.cruise = {'cycleMesure': 'PIRATA-FR29', 'plateforme': 'THALASSA', 'callsign': 'FNFP', 'institute': 'IRD',
                       'timezone': 'GMT', 'beginDate': '01/03/2019', 'endDate': '04/04/2019', 'pi': 'BOURLES',
                       'creator': 'Jacques.Grelet@ird.fr'}
        
        self.ctd = {'cruisePrefix': 'fr29', 'station': 'Station\\s*:\\s*\\D*(\\d*)', 'stationPrefixLength': 3,
                    'titleSummary': 'CTD profiles processed during PIRATA-FR29 cruise', 'typeInstrument': 'SBE911+',
                    'instrumentNumber': '09P1263', 
                    'header': {'isHeader': '^[*#]', 'isDevice': '^\\*\\s+(Sea-Bird)',
                    'LATITUDE':  'NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)\s+(\w)',
                    'LONGITUDE': 'NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)',
                    'DATETIME': 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)',
                    'DATE': 'Date\s*:\s*(\d+)/(\d+)/(\d+)',
                    'TIME': '[Heure|Hour]\s*:\s*(\d+)[:hH](\d+):(\d+)',
                    'bottomDepth': 'Bottom Depth\\s*:\\s*(\\d*\\.?\\d+?)\\s*\\S*', 'operator': 'Operator\\s*:\\s*(.*)',
                    'type': 'Type\\s*:\\s*(.*)'}
                    }

        self.xbt = {'cruisePrefix': "fr29", 'stationPrefixLength': 3, 'acquisitionSoftware': "WinMK21", 
                    'acquisitionVersion': "2.10.1", 'processingSoftware': "", 'processingVersion': "",
                    'type': "SIPPICAN", 'sn': "01150", 'title_summary': "XBT profiles processed during PIRATA-FR29 cruise",
                    'comment': "Extract from .edf files", 
	                'header': { 'endHeader': 'Depth\s*\(m\)',
	                'TIME': 'Time of Launch\s*[:=]\s*(\d+):(\d+):(\d+)',
	                'DATE': 'Date of Launch\s*[:=]\s*(\d+)/(\d+)/(\d+)',
	                'DATETIME': 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)',
	                'LATITUDE': 'Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)(\w)',
	                'LONGITUDE': 'Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)(\w)'}
                    }
        
        self.splitCtd = {'ETDD': 2, 'PRES': 3, 'DEPTH': 4, 'TEMP': 5, 'PSAL': 18,
                         'DENS': 20, 'SVEL': 22, 'DOX2': 16, 'FLU2': 14, 'FLU3': 15, 'TUR3': 13, 'NAVG': 23}
        
        self.splitCtdAll = {'ETDD': 2, 'PRES': 3, 'DEPTH': 4, 'TE01': 5, 'TE02': 6, 'CND1': 7, 'CND2': 8, 'DOV1': 9, 'DOV2': 10, 'DVT1': 11, 'DVT2': 12,
                            'TUR3': 13, 'FLU2': 14, 'FLU3': 15, 'DO12': 16, 'DO22': 17, 'PSA1': 18, 'PSA2': 19, 'DEN1': 20, 'DEN2': 21, 'SVEL': 22, 'NAVG': 23}
        
        self.splitBtl = {'BOTL': 1, 'month': 2, 'day': 3, 'year': 4, 'PSA1': 5, 'PSA2': 6, 'DO11': 7,
                         'DO12': 8, 'DO21': 9, 'DO22': 10, 'Potemp090C': 11, 'Potemp190C': 12,
                         'ETDD': 13, 'PRES': 14, 'DEPH': 15, 'TE01': 16, 'TE02': 17, 'CND1': 18, 'CND2': 19,
                         'DOV1': 20, 'DOV2': 21, 'DVT1': 22, 'DVT2': 23, 'TUR3': 24, 'FLU2': 25}

    def test_global(self):
        ''' test block [global]'''
        d = self.cfg['global']
        for k in d.keys():
            self.assertEqual(d[k], self.glob[k])

    def test_cruise(self):
        ''' test block [cruise]'''
        d = self.cfg['cruise']
        for k in d.keys():
            self.assertEqual(d[k], self.cruise[k])

    def test_ctd(self):
        ''' test block [ctd]'''
        d = self.cfg['ctd']
        for k in d.keys():
            self.assertEqual(d[k], self.ctd[k])
            
    def test_split_ctd(self):
        """ Test if all value  in block [split.ctd] are correct """
        d = self.cfg['split']['ctd']
        for k in d.keys():
            self.assertEqual(d[k], self.splitCtd[k])

    def test_split_ctdAll(self):
        """ Test if all value  in block [split.ctdall] are correct """
        d = self.cfg['split']['ctdAll']
        for k in d.keys():
            self.assertEqual(d[k], self.splitCtdAll[k])

    def test_split_btl(self):
        """ Test if all value  in block [split.btl] are correct """
        d = self.cfg['split']['btl']
        for k in d.keys():
            self.assertEqual(d[k], self.splitBtl[k])

    def test_split_xbt(self):
        """ Test if all value  in block [xbt] are correct """
        d = self.cfg['xbt']
        for k in d.keys():
            self.assertEqual(d[k], self.xbt[k])
            
if __name__ == '__main__':
    unittest.main()
