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
        self.cfg = toml.load('config.toml')

        self.glob = {'author': 'jgrelet IRD March 2019 PIRATA-FR29 cruise',
                     'debug': False, 'echo': True,
                     'codeRoscop': 'code_roscop.csv',
                     'roscopSeparator': ',',
                     'ASCII': "ascii",
                     'NETCDF': "netcdf",
                     'odv': "odv",
                     'title':'',
                     'history':'',
                     'institution':'IRD',
                    'source':'',
                    'comment':'',
                    'references':''}

        self.cruise = {'CYCLEMESURE': 'PIRATA-FR29',
                       'PLATEFORME': 'THALASSA',
                       'callsign': 'FNFP',
                       'INSTITUTE': 'IRD',
                       'TIMEZONE': 'GMT',
                       'BEGINDATE': '01/03/2019',
                       'ENDDATE': '04/04/2019',
                       'PI': 'BOURLES',
                       'CREATOR': 'Jacques.Grelet@ird.fr'}

        self.ctd = {'cruisePrefix': 'fr29',
                    'stationPrefixLength': 3,
                    'titleSummary': 'CTD profiles processed during PIRATA-FR29 cruise',
                    'typeInstrument': 'SBE911+',
                    'instrumentNumber': '09P1263',
                    'dateTimeFormat': "%d/%b/%Y %H:%M:%S",
                    'julianOrigin': 1}

        self.ctdHeader = {'isHeader': '^[*#]+\s+',
                          'endHeader': '^[*]END[*]',
                          'station': 'Station\s*:\s*\D*(\d*)',
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
                    'comment': "Extract from .edf files",
                    'dateTimeFormat': "%d/%m/%Y %H:%M:%S"}

        self.xbtHeader = {'endHeader': '^Depth\s*\(m\)',
                          'station': 'Sequence\s*#\s*:\s*(\d*)',
                          'TIME': 'Time of Launch\s*[:=]\s*(\d+):(\d+):(\d+)',
                          'DATE': 'Date of Launch\s*[:=]\s*(\d+)/(\d+)/(\d+)',
                          'DATETIME': 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)',
                          'LATITUDE': 'Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)(\w)',
                          'LONGITUDE': 'Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)(\w)'}

        self.splitCtd = {'ETDD': 1, 'PRES': 2, 'DEPTH': 3, 'TEMP': 4, 'PSAL': 17,
                         'DENS': 19, 'SVEL': 21, 'DOX2': 15, 'FLU2': 13, 'FLU3': 14, 'TUR3': 12, 'NAVG': 23}

        self.splitCtdAll = {'ETDD': 1, 'PRES': 2, 'DEPTH': 3, 'TE01': 4, 'TE02': 5, 'CND1': 6, 'CND2': 7, 'DOV1': 8, 'DOV2': 9, 'DVT1': 10, 'DVT2': 11,
                            'TUR3': 12, 'FLU2': 13, 'FLU3': 14, 'DO12': 15, 'DO22': 16, 'PSA1': 17, 'PSA2': 18, 'DEN1': 19, 'DEN2': 20, 'SVEL': 21, 'NAVG': 23}

        self.splitBtl = {'BOTL': 0, 'PSA1': 4, 'PSA2': 5, 'DO11': 6,
                         'DO12': 7, 'DO21': 8, 'DO22': 9, 'Potemp090C': 10, 'Potemp190C': 11,
                         'ETDD': 12, 'PRES': 13, 'DEPTH': 14, 'TE01': 15, 'TE02': 16, 'CND1': 17, 
                         'CND2': 18, 'DOV1': 19, 'DOV2': 20, 'DVT1': 21, 'DVT2': 22, 'TUR3': 23, 
                         'FLU2': 24}

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
        d = self.cfg['ctd']['split']
        for k in d.keys():
            self.assertEqual(d[k], self.splitCtd[k])

    def test_split_ctdAll(self):
        """ Test if all value  in block [split.ctdall] are correct """
        d = self.cfg['ctdAll']['split']
        for k in d.keys():
            self.assertEqual(d[k], self.splitCtdAll[k])

    def test_split_btl(self):
        """ Test if all value  in block [split.btl] are correct """
        d = self.cfg['btl']['split']
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
