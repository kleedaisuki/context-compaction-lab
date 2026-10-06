"""Working-set data preparation and paired experimental commands.

The new commands coexist with the legacy aggregate simulator. They make every
synthetic control and every empirical source visible in the saved manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .working_set_config import WorkingSetPolicy, WorkingSetWorkload
from .working_set_data import load_data, prepare_data
from .working_set_inference import sweep_working_sets
from .working_set_workloads import DemandSpec


def named_policies(
    workload: WorkingSetWorkload, preserve_tokens: int
) -> dict[str, WorkingSetPolicy]:
    """Supply mechanism controls while keeping tasks and fees identical."""
    warm = workload.base_tokens if workload.base_tokens >= workload.minimum_cache_tokens else 0
    return {
        "eager_cold": WorkingSetPolicy("eager"),
        "first_use_cold": WorkingSetPolicy(),
        "eager_warm": WorkingSetPolicy("eager", surviving_base_tokens=warm),
        "first_use_warm": WorkingSetPolicy(surviving_base_tokens=warm),
        "preserve_warm": WorkingSetPolicy(
            preserve_recent_tokens=preserve_tokens,
            preserve_read_guards=True,
            surviving_base_tokens=warm,
        ),
        "preserve_guard_lost": WorkingSetPolicy(
            preserve_recent_tokens=preserve_tokens,
            surviving_base_tokens=warm,
        ),
        "eager_round": WorkingSetPolicy(
            "eager",
            surviving_base_tokens=warm,
            recovery_model_round=True,
        ),
        "first_use_round": WorkingSetPolicy(
            surviving_base_tokens=warm,
            recovery_model_round=True,
        ),
        "strict_first_use": WorkingSetPolicy(surviving_base_tokens=warm, trigger="strict"),
        "strict_eager": WorkingSetPolicy("eager", surviving_base_tokens=warm, trigger="strict"),
    }


def _save(path: Path, report: dict) -> None:
    """Write portable strict JSON; infeasible cost is null, never infinity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _environment() -> dict:
    """Record runtime and source identity without exporting user paths or secrets."""
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return {
        "python": platform.python_version(),
        "source_sha256": digest.hexdigest(),
        "packages": {
            name: version(name)
            for name in (
                "context-compaction-lab",
                "numpy",
                "scipy",
                "sympy",
                "matplotlib",
                "tiktoken",
            )
        },
    }


def _plot(report: dict, destination: Path) -> None:
    """Show complete-task cost and reload volume; partial failure bills are absent."""
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    for name, policy in report["policies"].items():
        rows = policy["rows"]
        x = np.array([row["threshold_tokens"] for row in rows]) / 1_000
        y = np.array(
            [
                row["expected_cost_usd"]["mean"] if row["sampled_feasible"] else np.nan
                for row in rows
            ]
        )
        (line,) = axes[0].plot(x, y, label=name, linewidth=1.7)
        axes[1].plot(
            x,
            [row["diagnostics"]["reload_tokens"] / 1_000 for row in rows],
            color=line.get_color(),
            linewidth=1.7,
        )
        slopes = np.array(
            [
                row["paired_secant_usd_per_token"]["mean"] * 10_000
                if row["paired_secant_usd_per_token"]
                else np.nan
                for row in rows
            ]
        )
        axes[2].plot(x, slopes, color=line.get_color(), linewidth=1.5)
    axes[0].set_ylabel("Expected full-task API invoice (USD)")
    axes[0].set_title("Versioned working-set replay: conditional expectation", loc="left")
    axes[0].legend(frameon=False, fontsize=8, ncol=2)
    axes[1].set_ylabel("Mean restored payload + wrappers (k tokens)")
    axes[2].set_xlabel("Compaction threshold (k tokens)")
    axes[2].set_ylabel("Paired cost contrast (USD / 10k threshold tokens)")
    axes[2].axhline(0, color="#566574", linewidth=0.8)
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(alpha=0.16)
    fig.text(
        0.10,
        0.015,
        f"{report['replicates']:,} trajectories, {report['workload']['calls']} ordinary actions; "
        "common random tasks across policies.\n"
        "Measured file-size proxy + output blocks; controlled prerequisites/timing. "
        "Failure costs excluded, not censored into cheap policies.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(destination, dpi=165, facecolor="white")
    plt.close(fig)


def run_sweep(args: argparse.Namespace) -> None:
    """Execute the actual working-set engine and independently confirm selections."""
    started = time.perf_counter()
    artifacts, evidence, pool, starts = load_data(args.calibration)
    workload = WorkingSetWorkload(
        artifacts,
        args.base_tokens,
        args.summary_tokens,
        calls=args.calls,
        cache_ttl_seconds=None if args.no_expiry else args.ttl,
        compaction_delay_seconds=args.compaction_delay,
        recovery_delay_seconds=args.recovery_delay,
    )
    demand = DemandSpec(
        mode=args.demand,
        phase_length=args.phase_length,
        required_probability=args.required_probability,
        mutation_probability=args.mutation_probability,
        observation_probability=args.observation_probability,
        background_input_tokens=args.background_input,
        gap_mean_seconds=args.gap_mean,
    )
    available = named_policies(workload, args.preserve_tokens)
    names = args.policies.split(",")
    if len(names) != len(set(names)) or any(name not in available for name in names):
        raise ValueError(f"Choose unique policies from {','.join(available)}.")
    policies = {name: available[name] for name in names}
    report, samples = sweep_working_sets(
        workload,
        demand,
        policies,
        args.thresholds,
        args.replicates,
        args.seed,
        pool,
        starts,
        evidence["trace"]["block_length"],
        args.difference_step,
    )
    report.update(
        evidence=evidence, environment=_environment(), elapsed_seconds=time.perf_counter() - started
    )
    _save(args.output / "sweep.json", report)
    np.savez_compressed(args.output / "trajectory-costs.npz", **samples)
    _plot(report, args.output / "sweep.png")
    summary = {
        name: {
            "selected_mode": item["selected_mode"],
            "threshold_tokens": item["selected_threshold_tokens"],
            "one_percent_grid": item["one_percent_grid_tokens"],
            "confirmation": item["confirmation"]["selected"],
        }
        for name, item in report["policies"].items()
    }
    print(json.dumps(summary, indent=2, allow_nan=False))


def register_commands(commands, threshold_parser) -> None:
    """Register additive interfaces without breaking legacy aggregate commands."""
    prepare = commands.add_parser(
        "prepare-working-set", help="Measure files and public output pool."
    )
    prepare.add_argument("--trace", type=Path, required=True)
    prepare.add_argument("--provider", choices=("claude", "codex"), default="claude")
    prepare.add_argument("--block-length", type=int, default=16)
    prepare.add_argument("--output", type=Path, default=Path(".cache/calibration/working-set"))
    prepare.set_defaults(
        handler=lambda args: print(
            json.dumps(
                prepare_data(args.trace, args.output, args.provider, args.block_length),
                indent=2,
            )
        )
    )
    sweep = commands.add_parser(
        "working-set", help="Compare stateful compulsory-restoration policies."
    )
    sweep.add_argument("--calibration", type=Path, default=Path(".cache/calibration/working-set"))
    sweep.add_argument(
        "--thresholds", type=threshold_parser, default=threshold_parser("40000:240000:10000")
    )
    sweep.add_argument(
        "--policies", default="eager_cold,first_use_cold,first_use_warm,preserve_warm"
    )
    sweep.add_argument("--replicates", type=int, default=2048)
    sweep.add_argument("--calls", type=int, default=400)
    sweep.add_argument("--seed", type=int, default=20261006)
    sweep.add_argument("--difference-step", type=float, default=5000)
    sweep.add_argument("--base-tokens", type=int, default=20_000)
    sweep.add_argument("--summary-tokens", type=int, default=4_382)
    sweep.add_argument("--preserve-tokens", type=int, default=20_000)
    sweep.add_argument("--demand", choices=("phase", "diffuse", "mandatory"), default="phase")
    sweep.add_argument("--phase-length", type=int, default=25)
    sweep.add_argument("--required-probability", type=float, default=0.85)
    sweep.add_argument("--mutation-probability", type=float, default=0.002)
    sweep.add_argument("--observation-probability", type=float, default=0)
    sweep.add_argument("--background-input", type=int, default=256)
    sweep.add_argument("--gap-mean", type=float, default=90)
    sweep.add_argument("--ttl", type=float, default=300)
    sweep.add_argument("--no-expiry", action="store_true")
    sweep.add_argument("--compaction-delay", type=float, default=0)
    sweep.add_argument("--recovery-delay", type=float, default=0)
    sweep.add_argument("--output", type=Path, default=Path(".cache/experiments/working-set"))
    sweep.set_defaults(handler=run_sweep)
