import unittest
from unittest.mock import MagicMock

from physical_parameter import Roscop
from profile import Profile
from trajectory import Trajectory


class ProcessStructureTests(unittest.TestCase):
    def setUp(self):
        self.roscop = Roscop("code_roscop.csv")

    def test_profile_process_calls_write_outputs(self):
        profile = Profile([], self.roscop, ["PRES"])
        profile.create_tables = MagicMock()
        profile.set_regex = MagicMock()
        profile.read_files = MagicMock()
        profile.write_outputs = MagicMock()
        args = MagicMock(files=["dummy"], config="config.toml", keys=["PRES"])
        cfg = {"ctd": {"split": {"PRES": 0}}}

        profile.process(args, cfg, "CTD")

        profile.create_tables.assert_called_once()
        profile.set_regex.assert_called_once_with(cfg, "CTD", "header")
        profile.read_files.assert_called_once_with(cfg, "CTD")
        profile.write_outputs.assert_called_once_with(cfg, "CTD")
        profile.close()

    def test_trajectory_process_calls_write_outputs(self):
        trajectory = Trajectory([], self.roscop, ["SSJT"])
        trajectory.create_tables = MagicMock()
        trajectory.set_regex = MagicMock()
        trajectory.read_files = MagicMock()
        trajectory.write_outputs = MagicMock()
        args = MagicMock(files=["dummy"], config="config.toml", keys=["SSJT"])
        cfg = {"colcor": {"split": {"SSJT": 0}}, "global": {}}

        trajectory.process(args, cfg, "COLCOR")

        trajectory.create_tables.assert_called_once()
        trajectory.set_regex.assert_called_once_with(cfg, "COLCOR", "header")
        trajectory.read_files.assert_called_once_with(cfg, "COLCOR")
        trajectory.write_outputs.assert_called_once_with(cfg, "COLCOR")
        trajectory.close()
