"""Reproducible CLI for stochastic sweeps, marginal fitting, and symbolic controls.

Examples:
    compaction-lab sweep --scenario baseline --replicates 2048 --calls 400
    compaction-lab fit --input .temp/trace.csv --column growth_tokens
    compaction-lab symbolic

Experiments default to .cache/experiments; no remote model calls occur.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from .analytic import exponential_benchmark, renewal_quotient_derivative
from .calibration import fit_positive_samples
from .config import PositiveSpec, RecoverySpec, Workload
from .inference import sweep_thresholds
from .profiles import engineering_evidence, engineering_workload


def _threshold_grid(text: str) -> list[float]:
    """Parse an inclusive start:stop:step integer-token grid."""
    try:
        start, stop, step = (int(part) for part in text.split(":"))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Use start:stop:step integer tokens.") from error
    if start <= 0 or stop < start or step <= 0:
        raise argparse.ArgumentTypeError("Require 0 < start <= stop and positive step.")
    return [float(value) for value in range(start, stop + 1, step)]


def _recovery(args: argparse.Namespace, base: RecoverySpec) -> RecoverySpec:
    """Validate simultaneous overrides atomically, not invalid intermediate states."""
    changes: dict[str, object] = {"basis": args.recovery_basis}
    for option, field_name in (
        ("summary_tokens", "summary_base"),
        ("preserved_tokens", "preserved_tokens"),
        ("surviving_prefix_tokens", "surviving_prefix_tokens"),
        ("restored_input_tokens", "restored_input_tokens"),
    ):
        value = getattr(args, option)
        if value is not None:
            changes[field_name] = value
    documents = (
        replace(base.documents, mean=args.documents_mean)
        if args.documents_mean is not None else base.documents
    )
    if args.recovery_cv is not None:
        cv = args.recovery_cv
        if not np.isfinite(cv) or cv < 0:
            raise ValueError("Recovery CV must be finite and nonnegative.")
        if args.scenario == "legacy":
            raise ValueError("Use the corrected scenarios for fixed/narrow recovery sensitivity.")
        family = "constant" if cv == 0 else "lognormal"
        summary_mean = changes.get("summary_base", base.summary_base)
        changes["fraction_mean"] = 0
        changes["summary"] = PositiveSpec(
            family if summary_mean else "constant", mean=summary_mean, cv=cv,
        )
        documents = PositiveSpec(
            family if documents.mean else "constant", mean=documents.mean, cv=cv,
        )
    changes["documents"] = documents
    return replace(base, **changes)


def _scenario(args: argparse.Namespace) -> Workload:
    """Build source-anchored scenarios or named historical synthetic controls."""
    workload = (
        engineering_workload(args.calls) if args.scenario == "engineering"
        else Workload(calls=args.calls)
    )
    if args.scenario == "legacy":
        workload = replace(
            workload,
            recovery=RecoverySpec(
                summary_base=2_000,
                fraction_mean=0.03,
                documents=PositiveSpec("lognormal", mean=12_000, cv=0.8),
            ),
        )
    if args.scenario == "constant":
        workload = replace(
            workload,
            growth=PositiveSpec("constant", mean=2_000),
            gaps=PositiveSpec("constant", mean=90),
        )
    if args.scenario == "bursty":
        workload = replace(workload, growth=PositiveSpec("burst_lognormal", mean=2_000))
    if args.scenario == "long-gaps":
        workload = replace(workload, gaps=PositiveSpec("lognormal", mean=360, cv=1.5))
    growth = (
        replace(workload.growth, cv=args.growth_cv)
        if args.growth_cv is not None
        else workload.growth
    )
    if args.growth_mean is not None:
        growth = replace(growth, mean=args.growth_mean)
    gaps = (
        replace(workload.gaps, mean=args.gap_mean) if args.gap_mean is not None else workload.gaps
    )
    return replace(
        workload,
        growth=growth,
        gaps=gaps,
        recovery=_recovery(args, workload.recovery),
        cache_ttl_seconds=None if args.no_expiry else args.ttl,
    )


def _environment() -> dict[str, object]:
    """Record versions and source identity without exporting local credentials."""
    package_root = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for path in sorted(package_root.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return {
        "python": platform.python_version(),
        "packages": {
            name: version(name)
            for name in ("context-compaction-lab", "numpy", "scipy", "sympy", "matplotlib")
        },
        "source_sha256": digest.hexdigest(),
        "rng": "numpy.default_rng_PCG64",
    }


def _save_json(path: Path, report: dict[str, object]) -> None:
    """Reject nonfinite JSON data and create only the chosen artifact directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _draw_sweep(report: dict[str, object], output: Path) -> None:
    """Show expected price and paired secants with conditional pointwise intervals."""
    rows = report["rows"]
    x = np.array([row["threshold_tokens"] for row in rows]) / 1_000
    mean = np.array([row["expected_cost_usd"]["mean"] for row in rows])
    low = np.array([row["expected_cost_usd"]["ci_low"] for row in rows])
    high = np.array([row["expected_cost_usd"]["ci_high"] for row in rows])
    slopes = np.array([row["paired_secant_usd_per_token"]["mean"] for row in rows]) * 1_000
    slope_low = np.array([row["paired_secant_usd_per_token"]["ci_low"] for row in rows]) * 1_000
    slope_high = np.array([row["paired_secant_usd_per_token"]["ci_high"] for row in rows]) * 1_000
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(x, mean, color="#386cce", linewidth=2)
    axes[0].fill_between(x, low, high, color="#386cce", alpha=0.18)
    selected = report["selected_grid_threshold_tokens"] / 1_000
    axes[0].axvline(
        selected, color="#df8b32", linestyle="--", label="Selected discovery grid point"
    )
    axes[0].set_ylabel("Expected total API price (USD)")
    axes[0].set_title("Conditional expected invoice under scenario assumptions", loc="left")
    axes[0].legend(frameon=False)
    axes[1].plot(x, slopes, color="#1c978a", linewidth=2)
    axes[1].fill_between(x, slope_low, slope_high, color="#1c978a", alpha=0.18)
    axes[1].axhline(0, color="#607080", linewidth=1)
    axes[1].set_xlabel("Compaction threshold (thousand tokens)")
    axes[1].set_ylabel("Paired centered secant\nUSD per 1k threshold tokens")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.15)
    fig.text(
        0.10,
        0.02,
        f"{report['replicates']:,} independent trajectories; "
        f"{report['workload']['calls']} normal calls each; "
        f"seed {report['seed']}.\n"
        "Shading: 95% pointwise Monte Carlo intervals conditional on the assumed model. "
        "No finite-difference bias bound.",
        fontsize=8.5,
        color="#5b6572",
    )
    fig.tight_layout(rect=(0, 0.065, 1, 1))
    fig.savefig(output, dpi=170, facecolor="white")
    plt.close(fig)


def _run_sweep(args: argparse.Namespace) -> None:
    """Run discovery and independent confirmation, saving trajectory-level prices."""
    started = time.perf_counter()
    workload = _scenario(args)
    report, samples = sweep_thresholds(
        workload, args.thresholds, args.replicates, args.seed, args.difference_step
    )
    report["environment"] = _environment()
    report["scenario_name"] = args.scenario
    if args.scenario == "engineering":
        report["engineering_evidence"] = engineering_evidence()
        report["interpretation"]["data_status"] = "published_median_anchored_scenario_not_trace_fit"
    report["elapsed_seconds"] = time.perf_counter() - started
    destination = args.output or Path(".cache/experiments") / args.scenario
    _save_json(destination / "sweep.json", report)
    np.savez_compressed(
        destination / "trajectory-costs.npz",
        thresholds=np.array(sorted(args.thresholds)),
        costs=samples,
    )
    _draw_sweep(report, destination / "sweep.png")
    print(
        json.dumps(
            {
                "scenario": args.scenario,
                "selected_grid_threshold_tokens": report["selected_grid_threshold_tokens"],
                "independent_validation": report["independent_validation"],
                "output": str(destination),
                "scope": report["interpretation"],
            },
            indent=2,
        )
    )


def _run_fit(args: argparse.Namespace) -> None:
    """Fit one trace marginal without treating it as a validated joint workload."""
    with args.input.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or args.column not in reader.fieldnames:
            raise ValueError(f"CSV has no column named {args.column!r}.")
        values = [float(row[args.column]) for row in reader]
    report = fit_positive_samples(values)
    report["source"] = {
        "column": args.column,
        "sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "units": args.units,
    }
    report["environment"] = _environment()
    _save_json(args.output, report)
    print(json.dumps(report, indent=2))


def _run_symbolic(args: argparse.Namespace) -> None:
    """Publish exact stochastic-control expressions as text and LaTeX JSON."""
    expressions = exponential_benchmark()
    expressions["renewal_quotient_derivative"] = renewal_quotient_derivative()
    report = {
        "scope": "idealized_exponential_first_passage_benchmark_not_full_TTL_simulator",
        "expressions": {
            name: {"sympy": sp.sstr(expr), "latex": sp.latex(expr)}
            for name, expr in expressions.items()
        },
        "environment": _environment(),
    }
    _save_json(args.output, report)
    print(json.dumps(report, indent=2))


def main(argv: list[str] | None = None) -> None:
    """Dispatch explicit research commands; malformed assumptions fail fast."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    from .working_set_cli import register_commands

    register_commands(commands, _threshold_grid)
    sweep = commands.add_parser("sweep", help="Estimate expected total invoice on a grid.")
    sweep.add_argument(
        "--scenario",
        choices=("engineering", "baseline", "constant", "bursty", "long-gaps", "legacy"),
        default="engineering",
    )
    sweep.add_argument(
        "--thresholds", type=_threshold_grid, default=_threshold_grid("75000:300000:5000")
    )
    sweep.add_argument("--replicates", type=int, default=2048)
    sweep.add_argument("--calls", type=int, default=400)
    sweep.add_argument("--seed", type=int, default=20261006)
    sweep.add_argument("--difference-step", type=float, default=5000)
    sweep.add_argument("--growth-cv", type=float)
    sweep.add_argument("--growth-mean", type=float, help="Override retained growth scale per call.")
    sweep.add_argument("--gap-mean", type=float)
    sweep.add_argument("--documents-mean", type=float)
    sweep.add_argument("--summary-tokens", type=int, help="Fixed generated-summary size.")
    sweep.add_argument(
        "--restored-input-tokens", type=int,
        help="Aggregate non-generated reset payload; exclusive with document/preservation sizes.",
    )
    sweep.add_argument("--preserved-tokens", type=int, help="Verbatim retained old-context target.")
    sweep.add_argument(
        "--surviving-prefix-tokens",
        type=int,
        help="Declared unchanged warm cache boundary inside preserved context.",
    )
    sweep.add_argument(
        "--recovery-cv",
        type=float,
        help="Summary/document CV: 0 fixed, e.g. 0.05 narrow; aggregate input stays fixed.",
    )
    sweep.add_argument("--recovery-basis", choices=("threshold", "crossed"), default="threshold")
    sweep.add_argument("--ttl", type=float, default=300)
    sweep.add_argument("--no-expiry", action="store_true")
    sweep.add_argument("--output", type=Path)
    sweep.set_defaults(handler=_run_sweep)
    fit = commands.add_parser("fit", help="Fit positive gamma/lognormal trace marginals.")
    fit.add_argument("--input", type=Path, required=True)
    fit.add_argument("--column", required=True)
    fit.add_argument("--units", default="caller_declared_unspecified")
    fit.add_argument("--output", type=Path, default=Path(".cache/experiments/calibration.json"))
    fit.set_defaults(handler=_run_fit)
    symbolic = commands.add_parser("symbolic", help="Derive exact stochastic renewal control.")
    symbolic.add_argument("--output", type=Path, default=Path(".cache/experiments/symbolic.json"))
    symbolic.set_defaults(handler=_run_symbolic)
    args = parser.parse_args(argv)
    try:
        args.handler(args)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
