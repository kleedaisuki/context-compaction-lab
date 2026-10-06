"""Run the reproducible mechanism study through the installed working-set CLI.

Examples:
    uv run python experiments/run_working_set_study.py --replicates 2048 --jobs 2
    uv run python experiments/run_working_set_study.py --case mandatory

Only measured output marginals/file sizes are imported. Every case fixes its
ordinary tasks across thresholds/policies. Failed strict protocols remain in
the report as infeasible rather than cheaply completed work.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CASES = {
    "phase": (
        "eager_cold,first_use_cold,eager_warm,first_use_warm,preserve_warm,"
        "preserve_guard_lost,eager_round,first_use_round",
        [],
    ),
    "diffuse": (
        "eager_warm,first_use_warm,preserve_warm,eager_round,first_use_round",
        ["--demand", "diffuse"],
    ),
    "mandatory": (
        "eager_warm,first_use_warm,preserve_warm,preserve_guard_lost",
        ["--demand", "mandatory"],
    ),
    "churn": ("eager_warm,first_use_warm,preserve_warm", ["--mutation-probability", "0.02"]),
    "short": ("eager_warm,first_use_warm,preserve_warm,first_use_round", ["--calls", "40"]),
    "delay": (
        "eager_warm,first_use_warm,preserve_warm,eager_round,first_use_round",
        ["--compaction-delay", "360", "--recovery-delay", "360"],
    ),
    "strict": ("strict_eager,strict_first_use,first_use_warm", []),
    "base0": ("eager_warm,first_use_warm", ["--base-tokens", "0"]),
    "base40": ("eager_warm,first_use_warm", ["--base-tokens", "40000"]),
}
"""Predeclared mechanism contrasts; no task-success denominator or new prices."""


def run_case(name: str, args: argparse.Namespace) -> dict:
    """Execute one installed CLI case and extract its frozen-policy confirmation."""
    policies, extra = CASES[name]
    folder = args.output / name
    folder.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "context_compaction_lab.cli",
        "working-set",
        "--calibration",
        str(args.calibration),
        "--calls",
        "400",
        "--replicates",
        str(args.replicates),
        "--thresholds",
        "40000:240000:10000",
        "--difference-step",
        "5000",
        "--policies",
        policies,
        "--output",
        str(folder),
        *extra,
    ]
    environment = os.environ.copy()
    for variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        environment[variable] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(Path(".cache/pycache").resolve())
    environment["MPLCONFIGDIR"] = str(Path(".cache/matplotlib").resolve())
    with (folder / "run.log").open("w", encoding="utf-8") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, env=environment)
    report = json.loads((folder / "sweep.json").read_text())
    return {
        "case": name,
        "command": command[3:],
        "elapsed_seconds": report["elapsed_seconds"],
        "source_sha256": report["environment"]["source_sha256"],
        "action_field_sha256": report["action_field_sha256"],
        "policies": {
            policy: {
                "mode": row["selected_mode"],
                "threshold_tokens": row["selected_threshold_tokens"],
                "one_percent_grid_tokens": row["one_percent_grid_tokens"],
                "confirmation": row["confirmation"]["selected"],
            }
            for policy, row in report["policies"].items()
        },
    }


def main() -> None:
    """Persist completed cases incrementally so useful progress is never discarded."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=2048)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--case", choices=tuple(CASES), action="append")
    parser.add_argument("--calibration", type=Path, default=Path(".cache/calibration/working-set"))
    parser.add_argument("--output", type=Path, default=Path(".cache/experiments/working-set-study"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        pending = {executor.submit(run_case, name, args): name for name in (args.case or CASES)}
        for future in as_completed(pending):
            result = future.result()
            results[result["case"]] = result
            (args.output / "summary.json").write_text(
                json.dumps(results, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            print(f"Completed {result['case']} in {result['elapsed_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
