#!/usr/bin/env python3
"""
Estudo de alocação de missão (Fase 1 — sem Gazebo): roda os alocadores sobre
as missões de um cenário e mede, para cada (missão, alocador):

- validade: a alocação cobre exatamente as zonas pedidas, sem robô FUUT/SU;
- estabilidade: em N repetições, quantas alocações distintas aparecem e qual
  a fração da mais frequente (só o LLM varia; os demais são determinísticos);
- distância para o ótimo: makespan comparado ao do OptimalAllocator.

Uso (da raiz do repositório):
  python3 fleet_ws/scripts/mission_allocation_study.py --dry-run
  python3 fleet_ws/scripts/mission_allocation_study.py --repeat 10
  python3 fleet_ws/scripts/mission_allocation_study.py --allocators fixed,greedy,optimal

O LLM usa a API da Anthropic (ANTHROPIC_API_KEY ou perfil do `ant auth login`)
e custa uma chamada por (missão × repetição × alocador LLM). --dry-run mostra
quantas chamadas seriam feitas e o prompt da primeira missão, sem chamar a API.

Saída em --output-dir: runs.jsonl (uma linha por alocação, com plano, custos,
problemas e metadados do modelo) e summary.json (agregado + proveniência).
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from mission import load_scenario, make_allocator  # noqa: E402
from mission.allocators import DEFAULT_MODEL, build_user_prompt  # noqa: E402

DEFAULT_SCENARIO = ROOT / "backend" / "mission" / "scenarios" / "warehouse.yaml"
ALL_ALLOCATORS = ["fixed", "greedy", "optimal", "llm", "llm_dist"]


def git_provenance() -> dict:
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            return None

    return {"commit": run("rev-parse", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def summarize(runs: list[dict], optimal_makespan: float) -> dict:
    valid = [r for r in runs if r["valid"]]
    signatures = Counter(r["signature"] for r in valid)
    partitions = Counter(r["partition"] for r in valid)
    issue_kinds = Counter(i.split(":", 1)[0] for r in runs for i in r["issues"])
    out = {
        "n": len(runs),
        "n_valid": len(valid),
        "valid_rate": len(valid) / len(runs) if runs else None,
        "distinct_allocations": len(signatures),
        "modal_share": signatures.most_common(1)[0][1] / len(runs) if signatures else 0.0,
        "distinct_partitions": len(partitions),
        "modal_allocation": json.loads(signatures.most_common(1)[0][0]) if signatures else None,
        "issues": dict(issue_kinds),
    }
    if valid:
        makespans = [r["makespan"] for r in valid]
        gaps = [100.0 * (m - optimal_makespan) / optimal_makespan for m in makespans]
        out.update({
            "makespan_mean": statistics.fmean(makespans),
            "makespan_std": statistics.stdev(makespans) if len(makespans) > 1 else 0.0,
            "gap_pct_mean": statistics.fmean(gaps),
            "gap_pct_max": max(gaps),
            "optimal_hit_rate": sum(g < 1e-6 for g in gaps) / len(runs),
        })
    llm_meta = [r["meta"] for r in runs if "latency_s" in r["meta"]]
    if llm_meta:
        out["latency_s_mean"] = statistics.fmean(m["latency_s"] for m in llm_meta)
        out["input_tokens"] = sum(m.get("input_tokens") or 0 for m in llm_meta)
        out["output_tokens"] = sum(m.get("output_tokens") or 0 for m in llm_meta)
        out["models_served"] = dict(Counter(m.get("model_served") for m in llm_meta))
        out["fallback_runs"] = sum(bool(m.get("fallback_ran")) for m in llm_meta)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenario", default=str(DEFAULT_SCENARIO))
    ap.add_argument("--missions", default="", help="ids separados por vírgula (padrão: todas)")
    ap.add_argument("--allocators", default=",".join(ALL_ALLOCATORS))
    ap.add_argument("--repeat", type=int, default=10, help="repetições por missão para alocadores LLM")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--no-fallback", action="store_true",
                    help="desliga o fallback de modelo em caso de recusa (toda execução fica no --model)")
    ap.add_argument("--output-dir", default="")
    ap.add_argument("--dry-run", action="store_true", help="não chama a API; mostra o plano de execução")
    args = ap.parse_args()

    # Console do Windows usa cp1252 por padrão e não imprime "→" nem acentos.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    scenario = load_scenario(args.scenario)
    mission_ids = [m for m in args.missions.split(",") if m] or list(scenario.missions)
    unknown = [m for m in mission_ids if m not in scenario.missions]
    if unknown:
        ap.error(f"missões desconhecidas: {unknown}")
    names = [a for a in args.allocators.split(",") if a]
    llm_kwargs = {"model": args.model, "effort": args.effort, "use_fallback": not args.no_fallback}
    allocators = [make_allocator(n, **llm_kwargs) if n.startswith("llm") else make_allocator(n) for n in names]
    optimal = make_allocator("optimal")

    n_calls = sum(args.repeat for a in allocators if not a.deterministic) * len(mission_ids)
    print(f"[study] cenário {scenario.name}: {len(mission_ids)} missões × {names}; "
          f"{n_calls} chamadas à API ({args.model}, effort={args.effort})")
    if args.dry_run:
        print("\n[dry-run] prompt da primeira missão:\n")
        print(build_user_prompt(scenario, scenario.missions[mission_ids[0]], include_distances="llm_dist" in names))
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.output_dir or ROOT / "fleet_ws" / "analysis_results" / f"mission_allocation_{stamp}")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary: dict = {}
    with open(out_dir / "runs.jsonl", "w", encoding="utf-8") as runs_file:
        for mid in mission_ids:
            mission = scenario.missions[mid]
            best = optimal.allocate(scenario, mission)
            summary[mid] = {"text": mission.text, "expected_zones": list(mission.zones),
                            "optimal_makespan": best.makespan, "allocators": {}}
            for allocator in allocators:
                reps = 1 if allocator.deterministic else args.repeat
                runs = []
                for rep in range(1, reps + 1):
                    alloc = allocator.allocate(scenario, mission)
                    row = {**alloc.to_dict(), "partition": alloc.partition_signature(), "replicate": rep}
                    runs.append(row)
                    runs_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                    runs_file.flush()
                    status = "ok" if alloc.valid else "; ".join(alloc.issues)
                    mk = f"{alloc.makespan:.2f}" if alloc.makespan is not None else "-"
                    print(f"  {mid:24s} {allocator.name:9s} r{rep:02d} makespan={mk:>6s} {alloc.signature()} [{status}]")
                summary[mid]["allocators"][allocator.name] = {
                    "deterministic": allocator.deterministic, **summarize(runs, best.makespan)}

    report = {
        "created_at": stamp,
        "scenario": str(Path(args.scenario).resolve().relative_to(ROOT)) if Path(args.scenario).resolve().is_relative_to(ROOT) else args.scenario,
        "args": vars(args),
        "command_line": sys.argv,
        "git": git_provenance(),
        "missions": summary,
    }
    (out_dir / "summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'missão':24s} {'alocador':9s} {'válidas':>8s} {'distintas':>9s} {'modal':>6s} {'gap% méd':>9s} {'gap% máx':>9s}")
    for mid, ms in summary.items():
        for name, s in ms["allocators"].items():
            gap_mean = f"{s['gap_pct_mean']:.1f}" if "gap_pct_mean" in s else "-"
            gap_max = f"{s['gap_pct_max']:.1f}" if "gap_pct_max" in s else "-"
            print(f"{mid:24s} {name:9s} {s['n_valid']:>3d}/{s['n']:<4d} {s['distinct_allocations']:>9d} "
                  f"{s['modal_share']:>6.0%} {gap_mean:>9s} {gap_max:>9s}")
    print(f"\n[study] resultados em {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
