import sys
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
