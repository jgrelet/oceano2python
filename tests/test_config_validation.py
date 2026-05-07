import unittest

from config_validation import validate_runtime_config


class ConfigValidationTests(unittest.TestCase):
    def test_validate_runtime_config_accepts_minimal_profile_config(self):
        cfg = {
            "global": {},
            "cruise": {
                "CYCLEMESURE": "TEST",
                "PLATEFORME": "SHIP",
                "INSTITUTE": "IRD",
                "TIMEZONE": "GMT",
                "CREATOR": "test@example.com",
            },
            "ctd": {
                "header": {},
                "split": {"PRES": 1, "TEMP": 2},
            },
        }
        validate_runtime_config(cfg, "CTD", "PROFILE", ["PRES"])

    def test_validate_runtime_config_rejects_missing_split_key(self):
        cfg = {
            "global": {},
            "cruise": {
                "CYCLEMESURE": "TEST",
                "PLATEFORME": "SHIP",
                "INSTITUTE": "IRD",
                "TIMEZONE": "GMT",
                "CREATOR": "test@example.com",
            },
            "ctd": {
                "header": {},
                "split": {"PRES": 1},
            },
        }
        with self.assertRaises(ValueError):
            validate_runtime_config(cfg, "CTD", "PROFILE", ["TEMP"])
