import unittest
from copy import deepcopy
from types import SimpleNamespace

import toml

from oceano2python.metadata.physical_parameter import Roscop
from oceano2python.core.trajectory import Trajectory


def load_runtime_config():
    cfg = deepcopy(toml.load("config.toml"))
    cfg["global"]["ASCII"] = ""
    cfg["global"]["NETCDF"] = ""
    cfg["global"]["odv"] = ""
    return cfg


class TrajectoryTests(unittest.TestCase):
    def setUp(self):
        self.roscop = Roscop("code_roscop.csv")

    def test_colcor_supports_derived_etdd(self):
        cfg = load_runtime_config()
        keys = ["ETDD", "LATITUDE", "LONGITUDE", "SSJT", "SSTP", "SSPS"]
        file = "data/TSG/COLCOR/20190301-103803-TS_COLCOR.COLCOR"
        args = SimpleNamespace(files=[file], config="config.toml", keys=keys)
        fe = Trajectory([file], self.roscop, keys)

        try:
            fe.process(args, cfg, "COLCOR")
            self.assertGreater(fe.n, 0)
            self.assertIn("ETDD", fe.getlist())
            self.assertGreater(fe["ETDD"][0], 0)
        finally:
            fe.close()

    def test_casino_supports_reserved_dayd_column(self):
        cfg = load_runtime_config()
        keys = ["DAYD", "LATITUDE", "LONGITUDE", "SSJT", "SSTP", "SSPS", "WMSP", "WDIR"]
        file = "data/CASINO/20190301_100430_20190302_000000_AutoSave24h_piratafr29.csv"
        args = SimpleNamespace(files=[file], config="config.toml", keys=keys)
        fe = Trajectory([file], self.roscop, keys)

        try:
            fe.process(args, cfg, "CASINO")
            self.assertGreater(fe.n, 0)
            self.assertIn("DAYD", fe.getlist())
            self.assertGreater(fe["DAYD"][0], 0)
        finally:
            fe.close()

    def test_casino_fr33_supports_iso_datetime_and_dms_positions(self):
        cfg = load_runtime_config()
        cfg.update(toml.load("FR33-config.toml"))
        cfg["global"]["ASCII"] = ""
        cfg["global"]["NETCDF"] = ""
        cfg["global"]["odv"] = ""
        keys = ["LATITUDE", "LONGITUDE", "SSJT", "SSTP", "SSPS"]
        file = "data/CASINO/20230305_101030_20230305_235900_AutoSave24h_piratafr33.csv"
        args = SimpleNamespace(files=[file], config="FR33-config.toml", keys=keys)
        fe = Trajectory([file], self.roscop, keys)

        try:
            fe.process(args, cfg, "CASINO")
            self.assertGreater(fe.n, 0)
            self.assertAlmostEqual(fe["LATITUDE"][0], 16 + 49.99064 / 60, places=5)
            self.assertAlmostEqual(fe["LONGITUDE"][0], -(25 + 6.59372 / 60), places=5)
        finally:
            fe.close()
