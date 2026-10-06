"""Publish compact result metadata and readable cost-zoom figures from real runs.

Run after run_working_set_study.py and the documented fine-grid commands.
Raw output pools and public source-file bodies remain in ignored .cache.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read(path: str) -> dict:
    """Read a completed experiment rather than regenerate or invent a result."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compact(report: dict) -> dict:
    """Retain selections, whole-task holdout invoices and interpretable diagnostics."""
    return {
        "calls": report["workload"]["calls"],
        "base_tokens": report["workload"]["base_tokens"],
        "workload": report["workload"],
        "source_sha256": report["environment"]["source_sha256"],
        "replicates": report["replicates"],
        "discovery_seed": report["seed"],
        "confirmation_seed": report["confirmation_seed"],
        "action_field_sha256": report["action_field_sha256"],
        "confirmation_field_sha256": report["confirmation_field_sha256"],
        "demand_controls": report["demand_controls"],
        "difference_step_tokens": report["difference_step_tokens"],
        "paired_confirmed_policy_differences_usd": report[
            "paired_confirmed_policy_differences_usd"
        ],
        "policies": {
            name: {
                "policy": item["policy"],
                "mode": item["selected_mode"],
                "threshold": item["selected_threshold_tokens"],
                "one_percent_grid": item["one_percent_grid_tokens"],
                "holdout": item["confirmation"]["selected"],
                "no_compaction": item["confirmation"]["no_compaction"],
                "discovery_curve": [
                    {
                        key: row[key]
                        for key in (
                            "threshold_tokens",
                            "sampled_feasible",
                            "failure_share",
                            "expected_cost_usd",
                            "paired_secant_usd_per_token",
                        )
                    }
                    for row in item["rows"]
                ],
                "infeasible_grid_points": [
                    row["threshold_tokens"] for row in item["rows"] if not row["sampled_feasible"]
                ],
            }
            for name, item in report["policies"].items()
        },
    }


def curve(axis, report: dict, policy: str, label: str, color: str, band=False) -> None:
    """Plot genuine discovery estimates; material truncation is explicitly labeled."""
    rows = [row for row in report["policies"][policy]["rows"] if row["sampled_feasible"]]
    x = [row["threshold_tokens"] / 1000 for row in rows]
    y = [row["expected_cost_usd"]["mean"] for row in rows]
    axis.plot(x, y, label=label, color=color, linewidth=2)
    if band:
        axis.fill_between(
            x,
            [row["expected_cost_usd"]["ci_low"] for row in rows],
            [row["expected_cost_usd"]["ci_high"] for row in rows],
            color=color,
            alpha=0.15,
        )


def figure(phase: dict, mandatory: dict, fine_phase: dict, fine_mandatory: dict) -> None:
    """Show why access timing, not just a constant reload size, changes the sweet region."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.7))
    colors = {"first": "#246cb5", "eager": "#19847c", "keep": "#d08b36", "guard": "#a35b60"}
    curve(axes[0], phase, "eager_warm", "Eager reload", colors["eager"])
    curve(axes[0], phase, "preserve_warm", "Keep 20k + valid read guards", colors["keep"])
    curve(axes[0], phase, "preserve_guard_lost", "Keep 20k, read guards cleared", colors["guard"])
    curve(
        axes[0], fine_phase, "first_use_warm", "First-use reload (fine grid)", colors["first"], True
    )
    curve(
        axes[1],
        fine_mandatory,
        "first_use_warm",
        "Eager = first-use = valid retention",
        colors["first"],
        True,
    )
    curve(
        axes[1],
        mandatory,
        "preserve_guard_lost",
        "Retention with lost read guards",
        colors["guard"],
    )
    for axis, report in zip(axes, (fine_phase, fine_mandatory)):
        item = report["policies"]["first_use_warm"]
        region = item["one_percent_grid_tokens"]
        axis.axvspan(min(region) / 1000, max(region) / 1000, color=colors["first"], alpha=0.07)
        axis.axvline(
            item["selected_threshold_tokens"] / 1000,
            color=colors["first"],
            linestyle="--",
            alpha=0.65,
        )
        axis.set_xlabel("Compaction threshold (k tokens)")
        axis.set_ylabel("Expected 400-action invoice (USD)")
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(alpha=0.13)
        axis.legend(frameon=False, fontsize=8, loc="upper left")
    axes[0].set(title="Phase-local prerequisites: cost zoom", xlim=(60, 180), ylim=(22, 34))
    axes[1].set(
        title="All files compulsory each action: cost zoom", xlim=(100, 160), ylim=(30.3, 36)
    )
    fig.suptitle("Compaction sweet regions depend on the compulsory working set", x=0.07, ha="left")
    fig.text(
        0.07,
        0.02,
        "Zoomed cost panels; full 40k-240k sweeps and high early-reset costs remain in JSON.\n"
        "Fine grids: 4,096 trajectories; shading: pointwise MC CI and 1% discovery plateau.\n"
        "Measured file-size proxy/output blocks; other task/cache assumptions controlled.",
        fontsize=8,
        color="#4d5b69",
    )
    fig.tight_layout(rect=(0, 0.12, 1, 0.96))
    destination = Path(".cache/experiments/working-set-comparison.png")
    fig.savefig(destination, dpi=180, facecolor="white")
    plt.close(fig)


def main() -> None:
    """Commit-ready metadata contains aggregate findings, not downloaded traces."""
    root = Path(".cache/experiments/working-set-study")
    reports = {path.parent.name: read(str(path)) for path in sorted(root.glob("*/sweep.json"))}
    base_root = Path(".cache/experiments/working-set-base-study")
    for path in sorted(base_root.glob("*/sweep.json")):
        reports.setdefault(path.parent.name, read(str(path)))
    fine_phase = read(".cache/experiments/working-set-fine-phase/sweep.json")
    fine_mandatory = read(".cache/experiments/working-set-fine-mandatory/sweep.json")
    retention = {
        f"delay_{delay}": read(
            f".cache/experiments/working-set-retention/delay-{delay}/sweep.json"
        )
        for delay in (0, 360)
    }
    metadata = {
        "version": "0.2.0",
        "scope": "conditional_cost_not_full_real_task_replay",
        "evidence": reports["phase"]["evidence"],
        "coarse_cases": {name: compact(report) for name, report in reports.items()},
        "fine_cases": {"phase": compact(fine_phase), "mandatory": compact(fine_mandatory)},
        "retention_cases": {
            name: {**compact(report), "selected_budget_policy": report["selected_budget_policy"]}
            for name, report in retention.items()
        },
    }
    destination = Path("docs/research/working-set-results.json")
    destination.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    figure(reports["phase"], reports["mandatory"], fine_phase, fine_mandatory)
    print(f"Saved {len(reports)} coarse, 2 fine, 2 retention cases and the comparison figure.")


if __name__ == "__main__":
    main()
