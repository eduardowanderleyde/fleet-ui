import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "fleet_ws" / "scripts"))

from analyze_runs import _resample_pair, _resample_xy_by_time  # noqa: E402


class AnalyzeRunsResamplingTests(unittest.TestCase):
    def test_time_resampling_interpolates_to_fixed_normalised_grid(self):
        t = np.array([0.0, 2.0, 4.0], dtype=np.float64)
        xy = np.array([[0.0, 0.0], [2.0, 0.0], [4.0, 0.0]], dtype=np.float64)

        out = _resample_xy_by_time(t, xy, samples=5)

        np.testing.assert_allclose(
            out,
            np.array([
                [0.0, 0.0],
                [1.0, 0.0],
                [2.0, 0.0],
                [3.0, 0.0],
                [4.0, 0.0],
            ]),
        )

    def test_time_pair_resampling_uses_requested_sample_count(self):
        t1 = np.array([0.0, 1.0], dtype=np.float64)
        xy1 = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float64)
        t2 = np.array([10.0, 15.0, 20.0], dtype=np.float64)
        xy2 = np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]], dtype=np.float64)

        a, b = _resample_pair(xy1, xy2, t1=t1, t2=t2, mode="time", samples=4)

        self.assertEqual(a.shape, (4, 2))
        self.assertEqual(b.shape, (4, 2))
        np.testing.assert_allclose(a, b)

    def test_index_resampling_preserves_legacy_min_length(self):
        xy1 = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float64)
        xy2 = np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]], dtype=np.float64)

        a, b = _resample_pair(xy1, xy2, mode="index")

        self.assertEqual(a.shape, (2, 2))
        self.assertEqual(b.shape, (2, 2))


if __name__ == "__main__":
    unittest.main()
