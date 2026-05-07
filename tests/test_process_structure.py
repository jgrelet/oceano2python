import unittest
from unittest.mock import MagicMock

from oceano2python.metadata.physical_parameter import Roscop
from oceano2python.core.profile import Profile
from oceano2python.core.trajectory import Trajectory


class ProcessStructureTests(unittest.TestCase):
    def setUp(self):
        self.roscop = Roscop("code_roscop.csv")

    def test_profile_process_calls_write_outputs(self):
        profile = Profile([], self.roscop, ["PRES"])
        profile.prepare_processing = MagicMock()
        profile.read_files = MagicMock()
        profile.write_outputs = MagicMock()
        args = MagicMock(files=["dummy"], config="config.toml", keys=["PRES"])
        cfg = {"ctd": {"split": {"PRES": 0}}}

        profile.process(args, cfg, "CTD")

        profile.prepare_processing.assert_called_once_with(args, cfg, "CTD")
        profile.read_files.assert_called_once_with(cfg, "CTD")
        profile.write_outputs.assert_called_once_with(cfg, "CTD")
        profile.close()

    def test_trajectory_process_calls_write_outputs(self):
        trajectory = Trajectory([], self.roscop, ["SSJT"])
        trajectory.prepare_processing = MagicMock()
        trajectory.read_files = MagicMock()
        trajectory.write_outputs = MagicMock()
        args = MagicMock(files=["dummy"], config="config.toml", keys=["SSJT"])
        cfg = {"colcor": {"split": {"SSJT": 0}}, "global": {}}

        trajectory.process(args, cfg, "COLCOR")

        trajectory.prepare_processing.assert_called_once_with(args, cfg, "COLCOR")
        trajectory.read_files.assert_called_once_with(cfg, "COLCOR")
        trajectory.write_outputs.assert_called_once_with(cfg, "COLCOR")
        trajectory.close()
