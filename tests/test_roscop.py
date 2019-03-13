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
        """
        Test if filename is correct
        """

        self.assertEqual(self.r.file, self.file)

    def test_entries(self):
        self.assertEqual(len(self.r), 68)

    def test_key(self):
        self.assertEqual(self.r.returnCode('TEMP')['key'], 'TEMP')


if __name__ == '__main__':
    unittest.main()
