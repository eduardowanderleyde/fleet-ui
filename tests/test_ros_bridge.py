import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from ros_bridge import RosBridge  # noqa: E402


class RosBridgeCommandTests(unittest.TestCase):
    def setUp(self):
        self.bridge = RosBridge(str(ROOT / "fleet_ws"))

    def test_record_command_uses_single_robot_and_points(self):
        cmd = self.bridge.build_experiment_cmd({
            "command": "record",
            "robot": "default",
            "route": "rota_a",
            "collect": True,
            "topics": ["scan", "odom"],
            "initial_pose": [0, 0, 0],
            "points": [[1, 2, 0], [3, 4, 1.57]],
        })

        self.assertIn("record", cmd)
        self.assertIn("--single-robot", cmd)
        self.assertIn("--route", cmd)
        self.assertIn("rota_a", cmd)
        self.assertIn("--topics", cmd)
        self.assertIn("scan", cmd)
        self.assertIn("odom", cmd)
        self.assertIn("--points=1,2,0;3,4,1.57", cmd)

    def test_replay_command_keeps_robot_and_return_to_start(self):
        cmd = self.bridge.build_experiment_cmd({
            "command": "replay",
            "robot": "tb1",
            "route": "rota_b",
            "collect": False,
            "return_to_start": [0.1, -0.2, 0.3],
        })

        self.assertIn("replay", cmd)
        self.assertIn("--robot", cmd)
        self.assertIn("tb1", cmd)
        self.assertIn("--skip-collection", cmd)
        self.assertIn("--return-to-start=0.1,-0.2,0.3", cmd)

    def test_invalid_discovery_subnet_returns_error(self):
        result = self.bridge.discover_robots("999.bad")

        self.assertEqual(result["found"], [])
        self.assertIn("Subnet inválida", result["error"])

    def test_analyze_bags_builds_expected_command(self):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="ok", stderr="")

        with patch("ros_bridge.subprocess.run", side_effect=fake_run):
            ok, out = self.bridge.analyze_bags(
                ["collections/default/baseline", "collections/default/replay_01"],
                ["baseline", "replay_01"],
                "fleet_ws/runs/rota_a_abc123/analysis",
            )

        self.assertTrue(ok)
        self.assertEqual(out, "ok")
        shell_cmd = captured["cmd"][-1]  # ["bash", "-c", <shell_cmd>]
        self.assertIn("analyze_runs.py", shell_cmd)
        self.assertIn("collections/default/baseline", shell_cmd)
        self.assertIn("collections/default/replay_01", shell_cmd)
        self.assertIn("--output-dir fleet_ws/runs/rota_a_abc123/analysis", shell_cmd)
        self.assertIn("--labels baseline replay_01", shell_cmd)

    def test_analyze_bags_reports_failure_on_nonzero_exit(self):
        def fake_run(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="boom")

        with patch("ros_bridge.subprocess.run", side_effect=fake_run):
            ok, out = self.bridge.analyze_bags(["b1"], ["baseline"], "out")

        self.assertFalse(ok)
        self.assertIn("boom", out)


if __name__ == "__main__":
    unittest.main()
