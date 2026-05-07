import tempfile
import unittest

import numpy as np

import netcdf


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
