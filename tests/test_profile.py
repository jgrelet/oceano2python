import unittest
from copy import deepcopy
from types import SimpleNamespace

import toml

from physical_parameter import Roscop
from profile import Profile


def load_runtime_config():
    cfg = deepcopy(toml.load("config.toml"))
    cfg["global"]["ASCII"] = ""
    cfg["global"]["NETCDF"] = ""
    cfg["global"]["odv"] = ""
    return cfg


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.roscop = Roscop("code_roscop.csv")

    def _run_profile(self, device, file, keys):
        cfg = load_runtime_config()
        args = SimpleNamespace(files=[file], config="config.toml", keys=keys)
        fe = Profile([file], self.roscop, keys)
        try:
            fe.process(args, cfg, device)
            return fe
        except Exception:
            fe.close()
            raise

    def test_ctd_profile(self):
        keys = ["PRES", "DEPTH", "ETDD", "TEMP", "PSAL", "DOX2", "DENS", "SVEL", "FLU2", "FLU3", "TUR3", "NAVG"]
        fe = self._run_profile("CTD", "data/CTD/cnv/dfr29001.cnv", keys)
        try:
            self.assertEqual(fe.n, 1)
            self.assertEqual(fe["PROFILE"][0], 1)
            self.assertAlmostEqual(fe["LATITUDE"][0], 12 + 29.57 / 60, places=5)
            self.assertAlmostEqual(fe["LONGITUDE"][0], -(23 + 20.56 / 60), places=5)
            self.assertGreater(fe["PRES"][0][0], 0)
        finally:
            fe.close()

    def test_btl_profile(self):
        keys = ["BOTL", "ETDD", "PRES", "DEPTH", "TE01", "TE02", "PSA1", "PSA2", "DO11", "DO12", "DO21", "DO22", "FLU2"]
        fe = self._run_profile("BTL", "data/CTD/btl/fr29001.btl", keys)
        try:
            self.assertEqual(fe.n, 1)
            self.assertEqual(fe["PROFILE"][0], 1)
            self.assertGreater(fe["BOTL"][0][0], 0)
            self.assertGreater(fe["PRES"][0][0], 0)
        finally:
            fe.close()

    def test_xbt_profile(self):
        keys = ["DEPTH", "TEMP", "SVEL"]
        fe = self._run_profile("XBT", "data/XBT/T7_00001.EDF", keys)
        try:
            self.assertEqual(fe.n, 1)
            self.assertEqual(fe["PROFILE"][0], 1)
            self.assertGreaterEqual(fe["DEPTH"][0][0], 0)
            self.assertGreater(fe["TEMP"][0][0], 0)
        finally:
            fe.close()

    def test_rbr_profile(self):
        keys = ["PRES", "DEPTH", "TEMP", "PSAL", "DENS", "SVEL", "FLU2"]
        fe = self._run_profile("RBR", "data/RBR/fr2900201.txt", keys)
        try:
            self.assertEqual(fe.n, 1)
            self.assertEqual(fe["PROFILE"][0], 201)
            self.assertAlmostEqual(fe["LATITUDE"][0], -(8 + 50.7585 / 60), places=5)
            self.assertAlmostEqual(fe["LONGITUDE"][0], -(34 + 43.6905 / 60), places=5)
            self.assertGreater(fe["PRES"][0][0], 0)
        finally:
            fe.close()

    def test_ladcp_profile(self):
        keys = ["DEPTH", "EWCT", "NSCT"]
        fe = self._run_profile("LADCP", "data/LADCP/fr29001.lad", keys)
        try:
            self.assertEqual(fe.n, 1)
            self.assertEqual(fe["PROFILE"][0], 1)
            self.assertGreater(fe["DEPTH"][0][0], 0)
            self.assertAlmostEqual(fe["LATITUDE"][0], 12 + 29.9460 / 60, places=5)
            self.assertAlmostEqual(fe["LONGITUDE"][0], -(23 + 20.7120 / 60), places=5)
        finally:
            fe.close()
