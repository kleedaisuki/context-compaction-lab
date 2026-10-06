"""Enumerate finite demand paths through the actual working-set simulator.

Run ``uv run python experiments/working_set_exact_control.py``. All scenario
parameters are declared synthetic controls, not estimates of real workloads.
The experiment has no independent invoice ledger and performs no terminal
compaction; it verifies finite expected prices and threshold plateaus directly.
"""

from __future__ import annotations

import itertools
import json
import math
import time
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from context_compaction_lab.config import Pricing
from context_compaction_lab.working_set_config import (
    ActionField,
    ArtifactSpec,
    WorkingSetPolicy,
    WorkingSetWorkload,
)
from context_compaction_lab.working_set_simulation import (
    WorkingSetResult,
    simulate_working_set,
)


def enumerate_demands(calls: int, probability: float) -> tuple[NDArray, NDArray]:
    """Return every iid Bernoulli demand path and its true probability mass."""
    paths = np.array(list(itertools.product((False, True), repeat=calls)), dtype=bool)
    counts = paths.sum(axis=1)
    weights = probability**counts * (1 - probability) ** (calls - counts)
    assert math.isclose(float(weights.sum()), 1.0, abs_tol=1e-14)
    assert np.allclose(weights @ paths, probability, atol=1e-14)
    return paths, weights


def ordinary_fixture(paths: NDArray) -> tuple[WorkingSetWorkload, ActionField]:
    """Build the eight-action one-file control with a warm, eligible stable base."""
    count, calls = paths.shape
    workload = WorkingSetWorkload(
        artifacts=(ArtifactSpec("file-a", 24),), base_tokens=32, summary_tokens=8,
        calls=calls, minimum_cache_tokens=16, cache_ttl_seconds=None,
        normal_uncached_tokens=2, compaction_instruction_tokens=4,
        file_wrapper_tokens=2, warm_start=True,
        recovery_command_tokens=8, recovery_instruction_tokens=80,
    )
    field = ActionField(
        background_input=np.full((count, calls), 20, dtype=np.int64),
        output_tokens=np.full((count, calls), 10, dtype=np.int64),
        gaps=np.zeros((count, calls)), required=paths[:, :, None],
    )
    return workload, field


def policies() -> dict[str, WorkingSetPolicy]:
    """Separate file/guard retention from survival of the matching base prefix."""
    return {
        "first_use": WorkingSetPolicy(),
        "eager": WorkingSetPolicy(restoration="eager"),
        "preserve_without_guard": WorkingSetPolicy(preserve_recent_tokens=26),
        "preserve_with_guard": WorkingSetPolicy(
            preserve_recent_tokens=26, preserve_read_guards=True,
        ),
        "stable_first_use": WorkingSetPolicy(surviving_base_tokens=32),
        "stable_preserve_with_guard": WorkingSetPolicy(
            preserve_recent_tokens=26, preserve_read_guards=True, surviving_base_tokens=32,
        ),
    }


def weighted_result(result: WorkingSetResult, weights: NDArray) -> dict[str, float]:
    """Check completion and invoice closure before taking exact finite means."""
    assert not np.any(result.loop_failures)
    assert np.all(result.completed_actions == 8)
    return {
        name: float(weights @ getattr(result, name))
        for name in (
            "costs", "input_tokens", "write_tokens", "read_tokens", "output_tokens",
            "compactions", "recovery_rounds", "reload_events", "reload_tokens",
            "retained_file_tokens", "context_area", "base_cache_read_tokens", "overshoots",
        )
    }


def verify_invoice(workload: WorkingSetWorkload, result: WorkingSetResult) -> None:
    """Require the engine invoice to close in its four disjoint price categories."""
    p = workload.pricing
    reconstructed = (p.input * result.input_tokens + p.write * result.write_tokens
                     + p.read * result.read_tokens + p.output * result.output_tokens)
    assert np.allclose(result.costs, reconstructed, atol=1e-14, rtol=1e-13)


def integer_intervals(values: list[int]) -> list[list[int]]:
    """Coalesce selected integer thresholds without concealing disconnected optima."""
    intervals: list[list[int]] = []
    for value in values:
        if intervals and value == intervals[-1][1] + 1:
            intervals[-1][1] = value
        else:
            intervals.append([value, value])
    return intervals


def threshold_scan(
    workload: WorkingSetWorkload, field: ActionField, weights: NDArray,
) -> dict[str, object]:
    """Scan every positive integer threshold until all policies have a constant tail."""
    policy_map = policies()
    upper = 1 + max(
        int(simulate_working_set(workload, policy, math.inf, field).max_context.max())
        for policy in policy_map.values()
    )
    summaries: dict[str, object] = {}
    curves: dict[str, object] = {}
    for name, policy in policy_map.items():
        rows = []
        previous_costs: NDArray | None = None
        plateaus: list[list[int]] = []
        for threshold in range(1, upper + 1):
            result = simulate_working_set(workload, policy, threshold, field)
            verify_invoice(workload, result)
            row = {"threshold": threshold, **weighted_result(result, weights)}
            rows.append(row)
            if previous_costs is not None and np.array_equal(result.costs, previous_costs):
                plateaus[-1][1] = threshold
            else:
                plateaus.append([threshold, threshold])
            previous_costs = result.costs.copy()
        prices = np.array([row["costs"] for row in rows])
        optimum = float(prices.min())
        winners = [int(i) + 1 for i in np.flatnonzero(np.isclose(prices, optimum, atol=1e-14,
                                                               rtol=1e-12))]
        infinity = simulate_working_set(workload, policy, math.inf, field)
        assert np.array_equal(previous_costs, infinity.costs)
        # Noninteger h in (k-1, k] must have the same decisions as integer k.
        for threshold in (64, 100, 128, upper):
            at_integer = simulate_working_set(workload, policy, threshold, field)
            inside_cell = simulate_working_set(workload, policy, threshold - 0.5, field)
            assert np.array_equal(at_integer.costs, inside_cell.costs)
        summaries[name] = {
            "policy": asdict(policy), "minimum_usd": optimum,
            "optimal_integer_intervals": integer_intervals(winners),
            "constant_tail_starts_at": plateaus[-1][0],
            "optimal_tail_unbounded": winners[-1] == upper,
            "pathwise_invoice_plateaus": plateaus,
            "at_h100": rows[99], "no_compaction": weighted_result(infinity, weights),
            "upward_jumps": int(np.count_nonzero(np.diff(prices) > 1e-14)),
            "downward_jumps": int(np.count_nonzero(np.diff(prices) < -1e-14)),
        }
        curves[name] = rows
    return {"exhaustive_integer_upper": upper, "summaries": summaries, "curves": curves}


def first_cycle_control(
    workload: WorkingSetWorkload, field: ActionField, paths: NDArray, weights: NDArray,
    probability: float, threshold: int = 100,
) -> dict[str, float]:
    """Obtain endogenous first-cycle length by rerunning engine prefixes, not a toy clock."""
    count, calls = paths.shape
    stopping = np.full(count, calls, dtype=np.int64)
    for length in range(2, calls + 1):
        prefix = ActionField(
            field.background_input[:, :length], field.output_tokens[:, :length],
            field.gaps[:, :length], required=field.required[:, :length],
        )
        result = simulate_working_set(replace(workload, calls=length), WorkingSetPolicy(),
                                      threshold, prefix)
        stopping = np.where((result.compactions > 0) & (stopping == calls), length - 1,
                            stopping)
    first = np.where(paths.any(axis=1), paths.argmax(axis=1) + 1, calls + 1)
    loaded = first <= stopping
    u = float(weights @ loaded)
    expected_t = float(weights @ stopping)
    carries = float(weights @ np.maximum(stopping - first, 0))
    independence_plugin = float(1 - weights @ ((1 - probability) ** stopping))
    assert math.isclose(carries, expected_t - u / probability, abs_tol=1e-12)
    assert not math.isclose(u, independence_plugin, abs_tol=1e-6)
    return {
        "threshold": threshold, "expected_first_cycle_actions": expected_t,
        "actual_first_use_probability": u,
        "independence_plugin_probability": independence_plugin,
        "plugin_probability_error": independence_plugin - u,
        "actual_later_ordinary_carries": carries,
        "compensator_identity_carries": expected_t - u / probability,
    }


def paired_monte_carlo(probability: float, exact_scan: dict) -> dict[str, object]:
    """Compare a shared seeded action sample against exact means and paired differences."""
    replicates, seed, threshold = 16_384, 20261006, 100
    rng = np.random.default_rng(seed)
    paths = rng.random((replicates, 8)) < probability
    workload, field = ordinary_fixture(paths)
    sample_costs = {
        name: simulate_working_set(workload, policy, threshold, field).costs
        for name, policy in policies().items()
    }
    rows = {}
    baseline = sample_costs["first_use"]
    reference = exact_scan["summaries"]["first_use"]["at_h100"]["costs"]
    for name, values in sample_costs.items():
        true_mean = exact_scan["summaries"][name]["at_h100"]["costs"]
        se = float(values.std(ddof=1) / math.sqrt(replicates))
        mean = float(values.mean())
        delta = values - baseline
        delta_mean = float(delta.mean())
        delta_se = float(delta.std(ddof=1) / math.sqrt(replicates))
        exact_delta = true_mean - reference
        assert abs(mean - true_mean) <= 5 * se + 1e-14
        assert abs(delta_mean - exact_delta) <= 5 * delta_se + 1e-14
        rows[name] = {
            "exact_mean_usd": true_mean, "sample_mean_usd": mean, "standard_error_usd": se,
            "exact_delta_from_first_use_usd": exact_delta,
            "paired_delta_usd": delta_mean, "paired_delta_standard_error_usd": delta_se,
        }
    return {"replicates": replicates, "seed": seed, "threshold": threshold, "rows": rows}


def batching_counterexample() -> dict[str, object]:
    """Show eager can beat first-use when two necessary loads share a recovery request."""
    workload = WorkingSetWorkload(
        (ArtifactSpec("a", 20), ArtifactSpec("b", 20)), base_tokens=32, summary_tokens=8,
        calls=8, minimum_cache_tokens=16, cache_ttl_seconds=None,
        normal_uncached_tokens=2, compaction_instruction_tokens=4,
        file_wrapper_tokens=0, warm_start=True,
        recovery_command_tokens=8, recovery_instruction_tokens=80,
    )
    required = np.zeros((1, 8, 2), dtype=bool)
    required[0, 0, 0] = True
    required[0, 1, 1] = True
    required[0, 2, 0] = True
    background = np.zeros((1, 8), dtype=np.int64)
    background[0, 0] = 80
    field = ActionField(background, np.zeros((1, 8), dtype=np.int64), np.zeros((1, 8)),
                        required=required)
    results = {}
    for recovery_round in (False, True):
        pair = {}
        for restoration in ("first_use", "eager"):
            policy = WorkingSetPolicy(restoration=restoration,
                                      recovery_model_round=recovery_round)
            result = simulate_working_set(workload, policy, 120, field)
            verify_invoice(workload, result)
            pair[restoration] = weighted_result(result, np.ones(1))
        results["with_recovery_round" if recovery_round else "no_recovery_round"] = pair
    recovery = results["with_recovery_round"]
    assert recovery["eager"]["costs"] < recovery["first_use"]["costs"]
    return {"workload": workload.to_dict(), "threshold": 120,
            "background_input": background.tolist(), "required": required.tolist(),
            "results": results}


def main() -> None:
    """Run exhaustive controls and save complete replayable numerical artifacts."""
    start = time.perf_counter()
    probability = 0.35
    paths, weights = enumerate_demands(8, probability)
    workload, field = ordinary_fixture(paths)
    scan = threshold_scan(workload, field, weights)
    expensive_reads = replace(workload, pricing=Pricing(read=3 / 1_000_000))
    sensitivity = threshold_scan(expensive_reads, field, weights)
    result = {
        "scenario_status": "synthetic declared control; not an empirical measurement",
        "method": "actual simulate_working_set; all 256 iid Bernoulli paths, true weights",
        "ordinary_actions": 8, "demand_probability": probability,
        "path_count": len(paths), "probability_mass": float(weights.sum()),
        "workload": workload.to_dict(), "threshold_scan": scan,
        "read_price_sensitivity": {
            "status": "declared stress test, not a provider-price claim",
            "read_price_usd_per_token": expensive_reads.pricing.read,
            "scan": sensitivity,
        },
        "endogenous_first_cycle": first_cycle_control(workload, field, paths, weights,
                                                        probability),
        "paired_monte_carlo": paired_monte_carlo(probability, scan),
        "batching_counterexample": batching_counterexample(),
    }
    result["runtime_seconds"] = time.perf_counter() - start
    output = Path(".cache/working-set-exact-control/results.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    display = {name: {key: value for key, value in summary.items()
                      if key not in ("pathwise_invoice_plateaus", "policy")}
               for name, summary in scan["summaries"].items()}
    print(json.dumps({"path": str(output), "runtime_seconds": result["runtime_seconds"],
                      "summaries": display, "first_cycle": result["endogenous_first_cycle"],
                      "batching": result["batching_counterexample"]["results"]}, indent=2))


if __name__ == "__main__":
    main()
