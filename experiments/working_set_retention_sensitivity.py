"""Jointly sweep retention budget and compact line under batched recovery fees.

Run with ``uv run python experiments/working_set_retention_sensitivity.py``.
Two conditions differ ONLY in extra recovery delay: 0 and 360 seconds. This
tests whether retaining facts/guards can avoid costly real recovery requests,
not whether preserving text magically avoids later cache input charges.
"""

from __future__ import annotations

import json
from pathlib import Path

from context_compaction_lab.working_set_cli import _environment, _plot, _save
from context_compaction_lab.working_set_config import WorkingSetPolicy, WorkingSetWorkload
from context_compaction_lab.working_set_data import load_data
from context_compaction_lab.working_set_inference import sweep_working_sets
from context_compaction_lab.working_set_workloads import DemandSpec


def main() -> None:
    """Select budget/threshold on discovery means, then report frozen holdout costs."""
    artifacts, evidence, pool, starts = load_data(Path(".cache/calibration/working-set"))
    policies = {
        f"retain_{budget}": WorkingSetPolicy(
            preserve_recent_tokens=budget,
            preserve_read_guards=True,
            surviving_base_tokens=20_000,
            recovery_model_round=True,
        )
        for budget in (0, 12_000, 20_000, 40_000, 64_000)
    }
    for delay in (0, 360):
        workload = WorkingSetWorkload(
            artifacts, 20_000, 4_382, calls=400, recovery_delay_seconds=delay
        )
        report, _ = sweep_working_sets(
            workload,
            DemandSpec(),
            policies,
            list(range(60_000, 160_001, 10_000)),
            1024,
            20261010,
            pool,
            starts,
            evidence["trace"]["block_length"],
            5000,
        )
        report["evidence"], report["environment"] = evidence, _environment()

        def discovery_mean(name: str) -> float:
            """Select using discovery data only, never holdout outcomes."""
            item = report["policies"][name]
            if item["selected_mode"] == "no_compaction":
                return item["no_compaction"]["expected_cost_usd"]["mean"]
            return next(
                row["expected_cost_usd"]["mean"]
                for row in item["rows"]
                if row["threshold_tokens"] == item["selected_threshold_tokens"]
            )

        report["selected_budget_policy"] = min(policies, key=discovery_mean)
        destination = Path(f".cache/experiments/working-set-retention/delay-{delay}")
        _save(destination / "sweep.json", report)
        _plot(report, destination / "sweep.png")
        print(
            json.dumps(
                {
                    "delay": delay,
                    "chosen": report["selected_budget_policy"],
                    "policies": {
                        name: {
                            "h": item["selected_threshold_tokens"],
                            "confirmed": item["confirmation"]["selected"]["expected_cost_usd"],
                        }
                        for name, item in report["policies"].items()
                    },
                },
                indent=2,
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
