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
                     'debug': False, 'echo': True,
                     # 'codeRoscop': 'C:\git\python\oceano2python\code_roscop.csv',
                     'codeRoscop': '/home/jgrelet/git/oceano2python/code_roscop.csv',
                     'ascii': "ascii",
                     'netcdf': "netcdf",
                     'odv': "odv"}

        self.cruise = {'cycleMesure': 'PIRATA-FR29',
                       'plateforme': 'THALASSA',
                       'callsign': 'FNFP',
                       'institute': 'IRD',
                       'timezone': 'GMT',
                       'beginDate': '01/03/2019',
                       'endDate': '04/04/2019',
                       'pi': 'BOURLES',
                       'creator': 'Jacques.Grelet@ird.fr'}

        self.ctd = {'cruisePrefix': 'fr29',
                    'station': 'Station\s*:\s*\D*(\d*)',
                    'stationPrefixLength': 3,
                    'titleSummary': 'CTD profiles processed during PIRATA-FR29 cruise',
                    'typeInstrument': 'SBE911+',
                    'instrumentNumber': '09P1263'}

        self.ctdHeader = {'isHeader': '^[*#]',
                          'LATITUDE':  'NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)\s+(\w)',
                          'LONGITUDE': 'NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)',
                          'DATETIME': 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)',
                          'DATE': 'Date\s*:\s*(\d+)/(\d+)/(\d+)',
                          'TIME': '[Heure|Hour]\s*:\s*(\d+)[:hH](\d+):(\d+)',
                          'BATH': 'Bottom Depth\s*:\s*(\d*\.?\d+?)\s*\S*',
                          'operator': 'Operator\s*:\s*(.*)',
                          'type': 'Type\s*:\s*(.*)'}

        self.xbt = {'cruisePrefix': "fr29",
                    'stationPrefixLength': 3,
                    'typeInstrument': "SIPPICAN+",
                    'instrumentNumber': "N/A",
                    'acquisitionSoftware': "WinMK21",
                    'acquisitionVersion': "2.10.1",
                    'processingSoftware': "", 'processingVersion': "",
                    'type': "SIPPICAN",
                    'sn': "01150",
                    'title_summary': "XBT profiles processed during PIRATA-FR29 cruise",
                    'comment': "Extract from .edf files"}

        self.xbtHeader = {'endHeader': 'Depth\s*\(m\)',
                          'TIME': 'Time of Launch\s*[:=]\s*(\d+):(\d+):(\d+)',
                          'DATE': 'Date of Launch\s*[:=]\s*(\d+)/(\d+)/(\d+)',
                          'DATETIME': 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)',
                          'LATITUDE': 'Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)(\w)',
                          'LONGITUDE': 'Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)(\w)'}

        self.splitCtd = {'ETDD': 1, 'PRES': 2, 'DEPTH': 3, 'TEMP': 4, 'PSAL': 17,
                         'DENS': 19, 'SVEL': 21, 'DOX2': 15, 'FLU2': 13, 'FLU3': 14, 'TUR3': 12, 'NAVG': 23}

        self.splitCtdAll = {'ETDD': 1, 'PRES': 2, 'DEPTH': 3, 'TE01': 4, 'TE02': 5, 'CND1': 6, 'CND2': 7, 'DOV1': 8, 'DOV2': 9, 'DVT1': 10, 'DVT2': 11,
                            'TUR3': 12, 'FLU2': 13, 'FLU3': 14, 'DO12': 15, 'DO22': 16, 'PSA1': 17, 'PSA2': 18, 'DEN1': 19, 'DEN2': 20, 'SVEL': 21, 'NAVG': 23}

        self.splitBtl = {'BOTL': 1, 'month': 2, 'day': 3, 'year': 4, 'PSA1': 5, 'PSA2': 6, 'DO11': 7,
                         'DO12': 8, 'DO21': 9, 'DO22': 10, 'Potemp090C': 11, 'Potemp190C': 12,
                         'ETDD': 13, 'PRES': 14, 'DEPH': 15, 'TE01': 16, 'TE02': 17, 'CND1': 18, 'CND2': 19,
                         'DOV1': 20, 'DOV2': 21, 'DVT1': 22, 'DVT2': 23, 'TUR3': 24, 'FLU2': 25}

        self.splitXbt = {'DEPTH': 0, 'TEMP': 1, 'SVEL': 2}

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
            # problem with nested table
            if k == 'header':
                break
            self.assertEqual(d[k], self.ctd[k])

    def test_ctd_header(self):
        ''' test block [ctd.header]'''
        d = self.cfg['ctd']['header']
        for k in d.keys():
            self.assertEqual(d[k], self.ctdHeader[k])

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

    def test_xbt(self):
        """ Test if all value  in block [xbt] are correct """
        d = self.cfg['xbt']
        for k in d.keys():
            # problem with nested table
            if k == 'header':
                break
            self.assertEqual(d[k], self.xbt[k])

    def test_xbt_header(self):
        ''' test block [xbt.header]'''
        d = self.cfg['xbt']['header']
        for k in d.keys():
            self.assertEqual(d[k], self.xbtHeader[k])

    def test_split_xbt(self):
        """ Test if all value  in block [split.xbt] are correct """
        d = self.cfg['split']['xbt']
        for k in d.keys():
            self.assertEqual(d[k], self.splitXbt[k])


if __name__ == '__main__':
    unittest.main()
