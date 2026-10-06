"""Instantiate analytical renewal structure using pinned community increments.

Run after ``calibrate_renewal_trace.py``. Deterministic empirical-law evaluation
selects the analytic threshold; raw IID/block paths then probe dependence,
finite horizons, and four-price mechanisms. No model API calls are required.
Monte Carlo intervals condition on this empirical pool and declared mechanism;
they do not quantify source selection bias or population-law uncertainty.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from dataclasses import asdict, replace
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from context_compaction_lab.renewal_analytic import (
    ErlangRenewal,
    HyperexponentialRenewal,
    RenewalMoments,
    asymptotic_optimal_gap,
    optimal_gap,
    physical_cache_fees,
)
from context_compaction_lab.renewal_numerics import (
    RenewalLedger,
    analytic_rates,
    empirical_renewal,
    simulate_renewal_ledger,
)


def fields(pool: dict, mode: str, seed: int, replicates: int, calls: int) -> tuple:
    """Sample paired growth/output marks with population-matched IID/block margins."""
    rng = np.random.default_rng(seed)
    if mode == "block":
        length = int(pool["block_length"])
        starts = rng.choice(
            pool["block_starts"], size=(replicates, (calls + 2 * length - 2) // length)
        )
        complete = (starts[:, :, None] + np.arange(length)).reshape(replicates, -1)
        # Random phase makes EVERY action's marginal equal to the block-weighted
        # IID control, not merely the average over a complete 16-action block.
        phase = rng.integers(length, size=(replicates, 1))
        indices = np.take_along_axis(complete, phase + np.arange(calls), axis=1)
    else:
        weights = None if mode == "all_iid" else pool["block_marginal_weights"].astype(float)
        probabilities = None if weights is None else weights / weights.sum()
        indices = rng.choice(len(pool["values"]), size=(replicates, calls), p=probabilities)
    return (
        pool["values"][indices],
        pool["previous_output_tokens"][indices],
        rng.random((replicates, calls)),
    )


def scalar_analytics(curve: dict, renewal: dict, ledger: RenewalLedger) -> dict:
    """Record analytic reductions and numerical residuals without publishing arrays."""
    result = {k: float(v) for k, v in curve.items() if not isinstance(v, np.ndarray)}
    moments = RenewalMoments(renewal["mean"], renewal["moment2"], renewal["moment3"])
    binned_moments = RenewalMoments(
        renewal["binned_mean"], renewal["binned_moment2"], renewal["binned_moment3"]
    )
    carry, _, setup, _ = ledger.coefficients()
    result["third_moment_threshold"] = ledger.reset + asymptotic_optimal_gap(
        binned_moments, setup / carry, lattice_span=renewal["lattice_span"]
    )
    result["growth_lattice_span_tokens"] = renewal["lattice_span"]
    result["renewal_equation_residual"] = renewal["renewal_residual"]
    result["original_mean_growth"] = renewal["mean"]
    result["binned_mean_growth"] = renewal["binned_mean"]
    fees = physical_cache_fees(
        ledger.prices,
        reset_tokens=ledger.reset,
        surviving_base=ledger.stable_base,
        summary_tokens=ledger.summary,
        mean_growth=moments.mean,
        mean_output=0,
        hit_probability=ledger.cache_hit,
    )
    exponential = ErlangRenewal(moments.mean)
    result["exponential_core_threshold"] = ledger.reset + optimal_gap(exponential, fees)
    result["exponential_marked_threshold"] = ledger.reset + optimal_gap(
        exponential, fees, terminal_fraction=ledger.tail_fraction
    )
    cv = np.sqrt(moments.cv_squared)
    if cv >= 1:
        mixture = HyperexponentialRenewal.from_mean_cv(moments.mean, cv)
        result["moment_matched_hyperexponential_core_threshold"] = ledger.reset + optimal_gap(
            mixture, fees
        )
    return result


def summarize(
    billed: dict,
    thresholds: np.ndarray,
    calls: int,
    analytic_threshold: float,
    fluid_threshold: float,
) -> dict:
    """Summarize paired conditional invoices and the exploratory grid minimum."""
    costs = billed["cost"] / calls
    means = costs.mean(axis=0)
    se = costs.std(axis=0, ddof=1) / np.sqrt(len(costs))
    best = int(np.argmin(means))
    analytic = int(np.argmin(np.abs(thresholds - analytic_threshold)))
    fluid = int(np.argmin(np.abs(thresholds - fluid_threshold)))
    paired = costs[:, analytic] - costs[:, fluid]
    near = np.flatnonzero(means <= 1.01 * means[best])
    result = {
        "calls": calls,
        "thresholds": [None if np.isinf(h) else float(h) for h in thresholds],
        "mean_usd_per_call": means.tolist(),
        "mc_se_usd_per_call": se.tolist(),
        "mean_compactions": billed["resets"].mean(axis=0).tolist(),
        "exploratory_best_threshold": None
        if np.isinf(thresholds[best])
        else float(thresholds[best]),
        "exploratory_best_usd_per_call": float(means[best]),
        "analytic_threshold_usd_per_call": float(means[analytic]),
        "analytic_threshold_mc_se": float(se[analytic]),
        "analytic_minus_fluid_usd_per_call": float(paired.mean()),
        "analytic_minus_fluid_mc_95_halfwidth": float(
            1.96 * paired.std(ddof=1) / np.sqrt(len(paired))
        ),
        "one_percent_grid_region": [
            None if np.isinf(thresholds[i]) else float(thresholds[i]) for i in near
        ],
        "mean_invoice_tokens_at_analytic": {
            category: float(billed[category][:, analytic].mean())
            for category in ("input", "write", "read", "output")
        },
    }
    return result


def controlled_checks() -> dict:
    """Probe exact cycle accounting and convergence before interpreting community curves."""
    ledger = RenewalLedger(reset=100, summary=10, stable_base=20)
    growth = np.full((2, 10000), 20)
    output = np.full_like(growth, 7)
    marks = np.ones_like(growth, dtype=bool)
    threshold = np.array([180.0])
    renewal = empirical_renewal(np.array([20]), None, 1, 1000)
    curve = analytic_rates(renewal, ledger, 7)
    index = int(np.where(curve["thresholds"] == 180)[0][0])
    bill = simulate_renewal_ledger(growth, output, marks, ledger, threshold)
    p = ledger.prices
    reconciled = sum(getattr(p, name) * bill[name] for name in ("input", "write", "read", "output"))
    assert np.allclose(reconciled, bill["cost"], atol=1e-12, rtol=0)
    observed = float(bill["cost"][0, 0] / growth.shape[1])
    expected = float(curve["rates"][index])
    assert abs(observed - expected) < 2e-7
    # Initial context is warm; compaction is not charged after the last action.
    tiny = simulate_renewal_ledger(growth[:, :4], output[:, :4], marks[:, :4], ledger, threshold)
    assert np.all(tiny["resets"] == 0)
    assert np.all(tiny["input"] == 4 * ledger.ordinary_suffix)
    assert np.all(tiny["read"] == 4 * ledger.reset + 20 * (0 + 1 + 2))
    assert np.all(tiny["write"] == 3 * 20)
    assert np.all(tiny["output"] == 4 * 7)
    return {
        "constant_growth_rate": expected,
        "finite_10000_rate": observed,
        "finite_boundary_difference": observed - expected,
        "four_category_reconciled": True,
        "no_terminal_compaction_four_action_check": True,
    }


def main() -> None:
    """Execute the theorem-to-community study and persist compact public findings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=512)
    parser.add_argument("--confirmation-replicates", type=int, default=512)
    parser.add_argument("--long-calls", type=int, default=4000)
    args = parser.parse_args()
    if args.replicates < 2 or args.confirmation_replicates < 2 or args.long_calls < 400:
        parser.error("At least two replicates and 400 long-horizon calls are required.")
    root = Path(__file__).resolve().parents[1]
    destination = root / ".cache" / "renewal-community-study"
    destination.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    pool = dict(np.load(root / ".cache" / "renewal-calibration" / "growth-pool.npz"))
    metadata = json.loads(
        (root / ".cache" / "renewal-calibration" / "calibration.json").read_text()
    )
    weights = pool["block_marginal_weights"]
    output_mean = float(np.average(pool["previous_output_tokens"], weights=weights))
    all_output_mean = float(pool["previous_output_tokens"].mean())
    ledger = RenewalLedger()
    scenarios = {
        "warm_base20k": ledger,
        "warm_base0": replace(ledger, stable_base=0),
        "hit80pct": replace(ledger, cache_hit=0.8),
        "hit50pct": replace(ledger, cache_hit=0.5),
        "summary20k": replace(ledger, summary=20000, reset=ledger.reset + 20000 - ledger.summary),
        "pre_call_growth": replace(ledger, tail_fraction=0),
    }
    renewal = empirical_renewal(pool["values"], weights, 25, 150000)
    fine = empirical_renewal(pool["values"], weights, 5, 150000)
    all_renewal = empirical_renewal(pool["values"], None, 25, 150000)
    curves = {name: analytic_rates(fine, config, output_mean) for name, config in scenarios.items()}
    predictions = {
        name: scalar_analytics(curves[name], fine, config) for name, config in scenarios.items()
    }
    all_curve = analytic_rates(all_renewal, ledger, all_output_mean)
    all_predictions = scalar_analytics(all_curve, all_renewal, ledger)
    coarse_curve = analytic_rates(renewal, ledger, output_mean)
    checks = controlled_checks()
    checks["quantum25_vs5_marked_threshold_tokens"] = (
        coarse_curve["marked_minimum_threshold"]
        - curves["warm_base20k"]["marked_minimum_threshold"]
    )
    checks["quantum25_vs5_minimum_rate_usd"] = (
        coarse_curve["marked_minimum_rate"] - curves["warm_base20k"]["marked_minimum_rate"]
    )
    assert abs(checks["quantum25_vs5_marked_threshold_tokens"]) < 100
    assert abs(checks["quantum25_vs5_minimum_rate_usd"]) < 1e-5
    assert fine["renewal_residual"] < 1e-10
    results = {}
    chosen = {}
    primary_plot = []
    for mode, seed in (("iid", 2026100601), ("block", 2026100602), ("all_iid", 2026100603)):
        print(f"Sampling {mode} with {args.replicates} x {args.long_calls} calls", flush=True)
        growth, outputs, uniform = fields(pool, mode, seed, args.replicates, args.long_calls)
        mode_scenarios = scenarios if mode == "iid" else {"warm_base20k": ledger}
        for name, config in mode_scenarios.items():
            prediction = all_predictions if mode == "all_iid" else predictions[name]
            analytic = prediction["marked_minimum_threshold"]
            fluid = prediction["fluid_threshold"]
            thresholds = np.unique(
                np.r_[
                    config.reset + np.arange(5000, 150001, 5000),
                    analytic,
                    fluid,
                    analytic + np.arange(-6000, 6001, 1000),
                    np.inf,
                ]
            )
            horizons = (32, 400, args.long_calls) if name == "warm_base20k" else (args.long_calls,)
            for horizon in horizons:
                print(f"Ledger {mode}/{name}/N{horizon}", flush=True)
                billed = simulate_renewal_ledger(
                    growth[:, :horizon],
                    outputs[:, :horizon],
                    uniform[:, :horizon] < config.cache_hit,
                    config,
                    thresholds,
                )
                row = summarize(billed, thresholds, horizon, analytic, fluid)
                row["realized_mean_growth"] = float(growth[:, :horizon].mean())
                row["realized_mean_output"] = float(outputs[:, :horizon].mean())
                if mode != "block":
                    row["analytic_rate_prediction"] = prediction["marked_minimum_rate"]
                    row["simulation_minus_prediction"] = (
                        row["analytic_threshold_usd_per_call"] - prediction["marked_minimum_rate"]
                    )
                key = f"{mode}/{name}/N{horizon}"
                results[key] = row
                chosen[key] = row["exploratory_best_threshold"]
                if name == "warm_base20k" and horizon == args.long_calls and mode != "all_iid":
                    primary_plot.append(
                        (mode, thresholds.copy(), billed["cost"].mean(axis=0) / horizon)
                    )
    confirmation = {}
    for mode, seed in (("iid", 2026101601), ("block", 2026101602)):
        growth, outputs, uniform = fields(
            pool, mode, seed, args.confirmation_replicates, args.long_calls
        )
        predicted = predictions["warm_base20k"]["marked_minimum_threshold"]
        for horizon in (32, 400, args.long_calls):
            selected = chosen[f"{mode}/warm_base20k/N{horizon}"]
            selected_h = np.inf if selected is None else selected
            thresholds = np.array([predicted, selected_h])
            bill = simulate_renewal_ledger(
                growth[:, :horizon],
                outputs[:, :horizon],
                uniform[:, :horizon] < 1,
                ledger,
                thresholds,
            )
            difference = (bill["cost"][:, 1] - bill["cost"][:, 0]) / horizon
            confirmation[f"{mode}/N{horizon}"] = {
                "selected_threshold": selected,
                "selected_minus_analytic_usd_per_call": float(difference.mean()),
                "mc95_halfwidth": float(1.96 * difference.std(ddof=1) / np.sqrt(len(difference))),
                "selected_rate": float(bill["cost"][:, 1].mean() / horizon),
                "analytic_rate": float(bill["cost"][:, 0].mean() / horizon),
            }
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(
        curves["warm_base20k"]["thresholds"] / 1000,
        curves["warm_base20k"]["rates"],
        label="IID empirical renewal (deterministic)",
    )
    for mode, thresholds, rates in primary_plot:
        finite = np.isfinite(thresholds)
        ax.plot(
            thresholds[finite] / 1000, rates[finite], ".", label=f"Raw {mode}, N={args.long_calls}"
        )
    ax.set(
        xlabel="Compaction threshold (thousand tokens)",
        ylabel="USD per ordinary call",
        ylim=(0.045, 0.080),
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(destination / "renewal-vs-community.png", dpi=170)
    plt.close(fig)
    result = {
        "source": metadata["source"],
        "cohort": metadata["cohort"],
        "design": {
            "replicates": args.replicates,
            "confirmation_replicates": args.confirmation_replicates,
            "long_calls": args.long_calls,
            "block_length": int(pool["block_length"]),
            "block_initial_phase": "Independent uniform offset in 0..15, fixed per trajectory",
            "analytic_quantum_tokens": 5,
            "control_quantum_tokens": 25,
            "seed_schedule": {
                "iid": 2026100601,
                "block": 2026100602,
                "all_iid": 2026100603,
                "confirmation_iid": 2026101601,
                "confirmation_block": 2026101602,
            },
            "mc_intervals": (
                "Conditional empirical-pool uncertainty, not population/source uncertainty"
            ),
            "no_compaction_threshold": "null; no hard context-cap imposed",
        },
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "ledger_scenarios": {name: asdict(config) for name, config in scenarios.items()},
        "analytic_predictions": predictions,
        "all_accepted_iid_predictions": all_predictions,
        "method_checks": checks,
        "simulations": results,
        "independent_confirmation": confirmation,
        "elapsed_seconds": time.perf_counter() - started,
    }
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    (destination / "results.json").write_text(text, encoding="utf-8")
    (root / "docs" / "research" / "renewal-results.json").write_text(text, encoding="utf-8")
    print(f"Completed in {result['elapsed_seconds']:.1f} seconds", flush=True)
    print(
        json.dumps({"predictions": predictions, "confirmation": confirmation}, indent=2), flush=True
    )


if __name__ == "__main__":
    main()
