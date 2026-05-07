import tempfile
import unittest

import numpy as np
from netCDF4 import Dataset

from oceano2python.writers import netcdf


class FakeTrajectory:
    def __init__(self):
        self._data = {
            "ID": np.array([1]),
            "DAYD": np.array([25261.5]),
            "LATITUDE": np.array([12.5]),
            "LONGITUDE": np.array([-23.5]),
            "SSJT": np.array([25.1]),
        }
        self.roscop = {
            "DAYD": {"types": "float64", "_FillValue": -9999.0, "units": "days since 1950-01-01 00:00:00"},
            "LATITUDE": {"types": "float64", "_FillValue": -9999.0, "units": "degree_north"},
            "LONGITUDE": {"types": "float64", "_FillValue": -9999.0, "units": "degree_east"},
            "SSJT": {"types": "float64", "_FillValue": -9999.0, "units": "degree_Celsius"},
        }
        self.n = 1

    def getlist(self):
        return self._data.keys()

    def __getitem__(self, key):
        return self._data[key]


class FakeProfile:
    variables_1D = ["PROFILE", "TIME", "LATITUDE", "LONGITUDE", "BATH"]

    def __init__(self):
        self._data = {
            "PROFILE": np.array([1]),
            "TIME": np.array([25261.5]),
            "LATITUDE": np.array([12.5]),
            "LONGITUDE": np.array([-23.5]),
            "BATH": np.array([1500.0]),
            "TEMP": np.array([[25.1, 24.8]]),
        }
        self.roscop = {
            "PROFILE": {"types": "int32", "_FillValue": -9999, "format": "%05d"},
            "TIME": {"types": "float64", "_FillValue": -9999.0, "units": "days since 1950-01-01 00:00:00"},
            "LATITUDE": {"types": "float32", "_FillValue": -9999.0, "units": "degree_north"},
            "LONGITUDE": {"types": "float32", "_FillValue": -9999.0, "units": "degree_east"},
            "BATH": {"types": "float32", "_FillValue": -9999.0, "units": "m"},
            "TEMP": {"types": "float32", "_FillValue": -9999.0, "units": "degree_Celsius"},
        }
        self.n = 1
        self.m = 2

    def getlist(self):
        return self._data.keys()

    def __getitem__(self, key):
        return self._data[key]


class NetcdfTests(unittest.TestCase):
    def test_write_trajectory_does_not_mutate_roscop_metadata(self):
        fe = FakeTrajectory()
        cfg = {
            "global": {
                "NETCDF": "",
                "title": "Oceano test",
                "institution": "IRD",
                "source": "unit-test",
                "comment": "metadata",
                "references": "local",
            },
            "cruise": {
                "CYCLEMESURE": "OCEANO-TESTS",
                "BEGINDATE": "01/03/2019",
                "ENDDATE": "04/04/2019",
                "TIMEZONE": "GMT",
                "INSTITUTE": "IRD",
                "PI": "ThePI",
            },
            "colcor": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg["global"]["NETCDF"] = tmpdir
            netcdf.writeTrajectory(cfg, "COLCOR", fe)

        self.assertIn("types", fe.roscop["DAYD"])
        self.assertIn("_FillValue", fe.roscop["DAYD"])

    def test_write_profile_uses_explicit_dimensions_and_preserves_metadata(self):
        fe = FakeProfile()
        cfg = {
            "global": {
                "NETCDF": "",
                "title": "Oceano test",
                "institution": "IRD",
                "source": "unit-test",
                "comment": "metadata",
                "references": "local",
            },
            "cruise": {
                "CYCLEMESURE": "OCEANO-TESTS",
                "BEGINDATE": "01/03/2019",
                "ENDDATE": "04/04/2019",
                "TIMEZONE": "GMT",
                "INSTITUTE": "IRD",
                "PI": "ThePI",
            },
            "ctd": {
                "typeInstrument": "SBE911+",
                "instrumentNumber": "09P1263",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg["global"]["NETCDF"] = tmpdir
            netcdf.writeProfile(cfg, "CTD", fe)
            path = f"{tmpdir}/OS_OCEANO-TESTS_CTD.nc"
            with Dataset(path) as ds:
                self.assertEqual(ds.variables["PROFILE"].dimensions, ("time",))
                self.assertEqual(ds.variables["TIME"].dimensions, ("time",))
                self.assertEqual(ds.variables["LATITUDE"].dimensions, ("latitude",))
                self.assertEqual(ds.variables["LONGITUDE"].dimensions, ("longitude",))
                self.assertEqual(ds.variables["BATH"].dimensions, ("time",))

        self.assertIn("types", fe.roscop["BATH"])
        self.assertIn("_FillValue", fe.roscop["BATH"])
