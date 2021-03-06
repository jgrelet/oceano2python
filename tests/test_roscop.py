import unittest

from physical_parameter import Roscop

'''
Run test in single file
> python -m unittest -v tests/test_roscop.py

Run all test_ * in dir tests:
> python -m unittest  discover tests - v
> python -m unittest  discover -s tests -p 'test_*.py' -v
'''


class testRoscop(unittest.TestCase):

    def setUp(self):
        """ Test initialisation """

        self.file = 'code_roscop.csv'
        self.r = Roscop(self.file)

    def test_file(self):
        """ Test if filename is correct """

        self.assertEqual(self.r.file, self.file)

    def test_entries(self):
        ''' test the number of entries in csv file '''
        self.assertEqual(len(self.r), 69)

    def test_key_TEMP(self):
        ''' test the standard_name for physical parameter TEMP '''
        self.assertEqual(self.r['TEMP'][
                         'standard_name'], 'sea_water_temperature')
        self.assertEqual(self.r['TEMP'][
                         'units'], 'degree_Celsius')
        self.assertEqual(self.r['TEMP'][
                         'comment'], 'Ocean temperature in Degrees Celsius')

    def test_key_PSAL(self):
        ''' test the standard_name for physical parameter PSAL '''
        self.assertEqual(self.r['PSAL'][
                         'standard_name'], 'sea_water_salinity')
        self.assertEqual(self.r['PSAL'][
                         'conventions'], 'PSU')
        self.assertEqual(self.r['PSAL'][
                         'comment'], 'Ocean practical salinity (PSS-78)')


if __name__ == '__main__':
    unittest.main()
