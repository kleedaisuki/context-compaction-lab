"""Paired working-set policy experiments with explicit failed-policy accounting."""

from __future__ import annotations

import hashlib
from dataclasses import asdict

import numpy as np

from .inference import estimate_mean, paired_difference
from .working_set_config import ActionField, WorkingSetPolicy, WorkingSetWorkload
from .working_set_simulation import WorkingSetResult, simulate_working_set
from .working_set_workloads import DemandSpec, draw_actions


def field_digest(field: ActionField) -> str:
    """Fingerprint shared exogenous actions without exporting private identifiers."""
    digest = hashlib.sha256()
    for name in ("background_input", "output_tokens", "gaps", "required", "mutations", "observed"):
        values = getattr(field, name)
        digest.update(name.encode())
        digest.update(str(values.shape).encode())
        digest.update(values.tobytes())
    return digest.hexdigest()


def successful(result: WorkingSetResult, calls: int) -> bool:
    """Never reward incomplete trajectories with their smaller partial invoice."""
    return bool(np.all(result.completed_actions == calls) and not np.any(result.loop_failures))


def describe(result: WorkingSetResult, calls: int) -> dict[str, object]:
    """Summarize full invoices only when all sampled ordinary work completed."""
    feasible = successful(result, calls)
    diagnostics = {
        name: float(getattr(result, name).mean())
        for name in (
            "compactions",
            "recovery_rounds",
            "reload_events",
            "reload_tokens",
            "reload_payload_tokens",
            "retained_file_tokens",
            "context_area",
            "base_cache_read_tokens",
            "input_tokens",
            "write_tokens",
            "read_tokens",
            "output_tokens",
            "completed_actions",
        )
    }
    return {
        "sampled_feasible": feasible,
        "failure_share": float(np.mean(result.loop_failures > 0)),
        "expected_cost_usd": estimate_mean(result.costs).to_dict() if feasible else None,
        "diagnostics": diagnostics,
        "p99_max_context_tokens": float(np.quantile(result.max_context, 0.99)),
    }


def _points(thresholds: list[float], difference_step: float) -> list[float]:
    """Reuse every grid and centered-contrast policy evaluation once."""
    if not thresholds or len(set(thresholds)) != len(thresholds):
        raise ValueError("Require a nonempty grid of unique thresholds.")
    if not np.isfinite(difference_step) or difference_step <= 0:
        raise ValueError("Difference step must be positive and finite.")
    if any(not np.isfinite(h) or h <= difference_step for h in thresholds):
        raise ValueError("Thresholds must be finite and exceed difference step.")
    points = set(thresholds) | {float("inf")}
    points |= {h - difference_step for h in thresholds} | {h + difference_step for h in thresholds}
    return sorted(points)


def _policy_sweep(
    workload: WorkingSetWorkload,
    policy: WorkingSetPolicy,
    thresholds: list[float],
    points: list[float],
    step: float,
    field: ActionField,
) -> tuple[dict, np.ndarray]:
    """Select within one policy family; retain failures rather than censor rows."""
    results = {h: simulate_working_set(workload, policy, h, field) for h in points}
    rows, costs = [], []
    for h in sorted(thresholds):
        result = results[h]
        row = {"threshold_tokens": h, **describe(result, workload.calls)}
        upper, lower = results[h + step], results[h - step]
        valid_slope = successful(upper, workload.calls) and successful(lower, workload.calls)
        row["paired_secant_usd_per_token"] = (
            estimate_mean((upper.costs - lower.costs) / (2 * step)).to_dict()
            if valid_slope
            else None
        )
        rows.append(row)
        costs.append(result.costs)
    feasible = [row for row in rows if row["sampled_feasible"]]
    selected = min(feasible, key=lambda row: row["expected_cost_usd"]["mean"]) if feasible else None
    baseline = describe(results[float("inf")], workload.calls)
    no_reset_wins = baseline["sampled_feasible"] and (
        selected is None
        or baseline["expected_cost_usd"]["mean"] <= selected["expected_cost_usd"]["mean"]
    )
    best = (
        baseline["expected_cost_usd"]["mean"]
        if no_reset_wins
        else selected["expected_cost_usd"]["mean"]
        if selected
        else None
    )
    report = {
        "policy": asdict(policy),
        "rows": rows,
        "selected_grid_threshold_tokens": selected["threshold_tokens"] if selected else None,
        "selected_mode": "no_compaction"
        if no_reset_wins
        else "finite_grid"
        if selected
        else "no_feasible_policy",
        "selected_threshold_tokens": None
        if no_reset_wins or selected is None
        else selected["threshold_tokens"],
        "no_compaction": baseline,
        "one_percent_grid_tokens": [
            row["threshold_tokens"]
            for row in feasible
            if row["expected_cost_usd"]["mean"] <= 1.01 * best
        ]
        if best is not None
        else [],
    }
    return report, np.stack(costs)


def sweep_working_sets(
    workload: WorkingSetWorkload,
    demand: DemandSpec,
    policies: dict[str, WorkingSetPolicy],
    thresholds: list[float],
    replicates: int,
    seed: int,
    pool: np.ndarray,
    starts: np.ndarray,
    block_length: int,
    difference_step: float = 2_500,
) -> tuple[dict, dict]:
    """Search and independently confirm paired policies under the same fixed tasks.

    Loop-prone policy points have null expected full-task cost, not artificially
    cheap failure bills. Sampled feasibility is not a hard capacity guarantee.
    A 1% discovery plateau is descriptive, not a simultaneous confidence set.
    """
    if isinstance(replicates, bool) or not isinstance(replicates, int) or replicates < 2:
        raise ValueError("Inference needs at least two independent trajectories.")
    if not policies:
        raise ValueError("At least one named policy is required.")
    points = _points(thresholds, difference_step)
    field = draw_actions(workload, demand, replicates, seed, pool, starts, block_length)
    validation = draw_actions(workload, demand, replicates, seed + 1, pool, starts, block_length)
    reports, samples, chosen = {}, {}, {}
    for name, policy in policies.items():
        report, sample = _policy_sweep(workload, policy, thresholds, points, difference_step, field)
        threshold = (
            float("inf")
            if report["selected_mode"] == "no_compaction"
            else report["selected_threshold_tokens"]
        )
        baseline = simulate_working_set(workload, policy, float("inf"), validation)
        holdout = (
            simulate_working_set(workload, policy, threshold, validation) if threshold else None
        )
        report["confirmation"] = {
            "selected": describe(holdout, workload.calls) if holdout is not None else None,
            "no_compaction": describe(baseline, workload.calls),
            "paired_selected_minus_no_compaction_usd": (
                paired_difference(holdout.costs, baseline.costs).to_dict()
                if holdout is not None
                and successful(holdout, workload.calls)
                and successful(baseline, workload.calls)
                else None
            ),
        }
        reports[name], samples[name] = report, sample
        if threshold is not None:
            chosen[name] = holdout
    paired = {
        f"{left}_minus_{right}": paired_difference(
            chosen[left].costs, chosen[right].costs
        ).to_dict()
        for left in chosen
        for right in chosen
        if left < right
        and successful(chosen[left], workload.calls)
        and successful(chosen[right], workload.calls)
    }
    return {
        "workload": workload.to_dict(),
        "demand_controls": demand.to_dict(),
        "replicates": replicates,
        "seed": seed,
        "confirmation_seed": seed + 1,
        "action_field_sha256": field_digest(field),
        "confirmation_field_sha256": field_digest(validation),
        "difference_step_tokens": difference_step,
        "policies": reports,
        "paired_confirmed_policy_differences_usd": paired,
        "interpretation": {
            "objective": "expected_four_price_invoice_for_fixed_ordinary_actions",
            "data_status": "corpus_size_proxy_empirical_output_blocks_controlled_prerequisites",
            "interval_scope": "conditional_pointwise_Monte_Carlo_error_not_parameter_uncertainty",
            "selection_scope": "finite_grid_then_independent_fixed_selection_confirmation",
            "failure_scope": "any_sampled_loop_failure_rejects_entire_policy_point_no_censoring",
            "gradient_scope": "paired_centered_secant_not_exact_integer_threshold_derivative",
        },
    }, samples
