"""
Analyst: interpreta os artefatos produzidos por uma campanha de experimentos
(fleet_ws/runs/<run_id>/analysis/summary.json, gerado por analyze_runs.py) sem
precisar reprocessar bags ROS 2.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class AnalystError(RuntimeError):
    """Erro ao ler ou interpretar artefatos de uma campanha."""


def _default_runs_dir() -> Path:
    workspace = os.environ.get("FLEET_WS") or str(Path(__file__).resolve().parents[2])
    ros_ws = os.environ.get("FLEET_ROS_WS") or str(Path(workspace) / "fleet_ws")
    return Path(ros_ws) / "runs"


class Analyst:
    def __init__(self, runs_dir: str | Path | None = None) -> None:
        self.runs_dir = Path(runs_dir) if runs_dir else _default_runs_dir()

    def _summary_path(self, run_id: str) -> Path:
        path = self.runs_dir / run_id / "analysis" / "summary.json"
        if not path.exists():
            raise AnalystError(f"summary.json não encontrado para run '{run_id}' em {path}")
        return path

    def load_summary(self, run_id: str) -> dict:
        return json.loads(self._summary_path(run_id).read_text())

    def analyze_experiment(self, run_id: str, rmse_threshold_m: float = 0.05) -> dict:
        """Resume uma campanha e sinaliza execuções com RMSE acima do limiar (em metros)."""
        summary = self.load_summary(run_id)
        vs_reference: list[dict[str, Any]] = summary.get("vs_reference", [])

        flagged = [
            entry for entry in vs_reference
            if entry["label"] != summary.get("reference_label") and entry.get("rmse_vs_ref_m", 0.0) > rmse_threshold_m
        ]
        rmse_values = [e["rmse_vs_ref_m"] for e in vs_reference if e["label"] != summary.get("reference_label")]

        return {
            "run_id": run_id,
            "reference_label": summary.get("reference_label"),
            "num_runs": len(summary.get("labels", [])),
            "mean_rmse_vs_ref_m": sum(rmse_values) / len(rmse_values) if rmse_values else 0.0,
            "max_rmse_vs_ref_m": max(rmse_values) if rmse_values else 0.0,
            "rmse_threshold_m": rmse_threshold_m,
            "flagged_runs": flagged,
        }

    def compare_runs(self, run_id: str, label_a: str, label_b: str) -> dict:
        """Compara duas execuções (labels) dentro da mesma campanha via a matriz RMSE pareada."""
        summary = self.load_summary(run_id)
        labels: list[str] = summary.get("labels", [])
        if label_a not in labels or label_b not in labels:
            raise AnalystError(f"Labels devem estar em {labels}, recebido: {label_a!r}, {label_b!r}")

        idx_a, idx_b = labels.index(label_a), labels.index(label_b)
        rmse = summary["pairwise_rmse_m"][idx_a][idx_b]
        stats = {s["label"]: s for s in summary.get("runs", [])}

        return {
            "run_id": run_id,
            "label_a": label_a,
            "label_b": label_b,
            "rmse_m": rmse,
            "duration_sec_a": stats[label_a]["duration_sec"],
            "duration_sec_b": stats[label_b]["duration_sec"],
            "path_length_m_a": stats[label_a]["path_length_m"],
            "path_length_m_b": stats[label_b]["path_length_m"],
        }
