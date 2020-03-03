import unittest
from datetime import datetime
import tools


class ToolsTests(unittest.TestCase):
    def test_julian2dt(self):
        """
        Tests a simple of julian day 0, origine 1950
        """
        dt = datetime(year=1950, day=1, month=1)

        self.assertAlmostEqual(0, tools.dt2julian(dt))
        
    def test_dt2julian(self):
        
        dt = tools.julian2dt(0)
        self.assertEqual(dt.year, 1950)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 0)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)