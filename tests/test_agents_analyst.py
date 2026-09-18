import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from agents.analyst import Analyst, AnalystError  # noqa: E402


SUMMARY = {
    "reference_label": "baseline",
    "labels": ["baseline", "replay_01", "replay_02"],
    "runs": [
        {"label": "baseline", "duration_sec": 18.0, "path_length_m": 0.25},
        {"label": "replay_01", "duration_sec": 10.0, "path_length_m": 0.05},
        {"label": "replay_02", "duration_sec": 9.5, "path_length_m": 0.0},
    ],
    "pairwise_rmse_m": [
        [0.0, 0.02, 0.08],
        [0.02, 0.0, 0.06],
        [0.08, 0.06, 0.0],
    ],
    "vs_reference": [
        {"label": "baseline", "rmse_vs_ref_m": 0.0},
        {"label": "replay_01", "rmse_vs_ref_m": 0.02},
        {"label": "replay_02", "rmse_vs_ref_m": 0.08},
    ],
}


class AnalystTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        runs_dir = Path(self.tmp.name)
        (runs_dir / "campaign01" / "analysis").mkdir(parents=True)
        (runs_dir / "campaign01" / "analysis" / "summary.json").write_text(json.dumps(SUMMARY))
        self.analyst = Analyst(runs_dir=runs_dir)

    def tearDown(self):
        self.tmp.cleanup()

    def test_analyze_experiment_flags_runs_above_threshold(self):
        result = self.analyst.analyze_experiment("campaign01", rmse_threshold_m=0.05)

        self.assertEqual(result["num_runs"], 3)
        self.assertEqual([r["label"] for r in result["flagged_runs"]], ["replay_02"])
        self.assertAlmostEqual(result["max_rmse_vs_ref_m"], 0.08)

    def test_compare_runs_reads_pairwise_matrix(self):
        result = self.analyst.compare_runs("campaign01", "replay_01", "replay_02")

        self.assertAlmostEqual(result["rmse_m"], 0.06)
        self.assertEqual(result["duration_sec_a"], 10.0)
        self.assertEqual(result["duration_sec_b"], 9.5)

    def test_missing_run_raises(self):
        with self.assertRaises(AnalystError):
            self.analyst.load_summary("does_not_exist")


if __name__ == "__main__":
    unittest.main()
