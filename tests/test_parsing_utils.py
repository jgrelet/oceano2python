import unittest

from oceano2python.core.parsing_utils import build_datetime_from_parts, parse_coordinate_groups


class ParsingUtilsTests(unittest.TestCase):
    def test_parse_coordinate_groups_supports_hemi_first(self):
        value = parse_coordinate_groups(("N", "16", "49,99064"), "N")
        self.assertAlmostEqual(value, 16 + 49.99064 / 60, places=5)

    def test_parse_coordinate_groups_supports_hemi_last(self):
        value = parse_coordinate_groups(("23", "20.5600", "W"), "E")
        self.assertAlmostEqual(value, -(23 + 20.56 / 60), places=5)

    def test_parse_coordinate_groups_supports_signed_decimal(self):
        value = parse_coordinate_groups(("-24.9993",), "E")
        self.assertAlmostEqual(value, -24.9993, places=5)

    def test_build_datetime_from_parts_dmy(self):
        dt = build_datetime_from_parts(("05", "03", "2023"), ("10", "11", "30"), "dmy")
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 5)

    def test_build_datetime_from_parts_ymd(self):
        dt = build_datetime_from_parts(("2023", "03", "05"), ("10", "11", "30"), "ymd")
        self.assertEqual(dt.year, 2023)
        self.assertEqual(dt.month, 3)
        self.assertEqual(dt.day, 5)
