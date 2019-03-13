import unittest

from physicalParameter import Roscop

'''
> python -m unittest -v tests/test_roscop.py
'''


class RoscopTest(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests."""

        self.file = 'code_roscop.csv'
        self.r = Roscop(self.file)

    def test_file(self):
        """ Test if filename is correct """

        self.assertEqual(self.r.file, self.file)

    def test_entries(self):
        ''' test the number of entries in csv file '''
        self.assertEqual(len(self.r), 68)

    def test_key(self):
        ''' test the standard_name for physical parameter TEMP '''
        self.assertEqual(self.r.returnCode('TEMP')[
                         'standard_name'], 'sea_water_temperature')


if __name__ == '__main__':
    unittest.main()
