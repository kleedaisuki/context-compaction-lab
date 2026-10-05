"""Monte Carlo inference for expected finite-horizon API cost.

Independent trajectories, not calls inside a trajectory, are statistical
units. Paired differences share exogenous marks across policies. Intervals
quantify simulation error conditional on an assumed workload, not uncertainty
about whether that workload describes a real user session.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats

from .config import Workload
from .simulation import RandomField, draw_random_field, simulate


@dataclass(frozen=True)
class MeanEstimate:
    """A pointwise Student-t interval for independent trajectory outcomes.

    Attributes:
        mean: Sample expectation estimate.
        standard_deviation: Across-trajectory sample deviation, ddof=1.
        standard_error: Monte Carlo standard error of the sample mean.
        ci_low: Lower approximate confidence bound for the mean.
        ci_high: Upper approximate confidence bound for the mean.
        replicates: Number of independent trajectories.
        confidence: Nominal pointwise confidence probability.
    """

    mean: float
    standard_deviation: float
    standard_error: float
    ci_low: float
    ci_high: float
    replicates: int
    confidence: float

    def to_dict(self) -> dict[str, float | int]:
        """Serialize a conditional Monte Carlo interval, not a model-validity claim."""
        return asdict(self)


def estimate_mean(values: np.ndarray, confidence: float = 0.95) -> MeanEstimate:
    """Estimate an expectation with a large-sample t interval.

    Heavy tails or small trajectory counts can make the approximation poor.
    Nonfinite observations are rejected rather than silently dropped.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError("At least two finite independent trajectory outcomes are required.")
    if not 0 < confidence < 1:
        raise ValueError("Confidence must lie strictly between zero and one.")
    mean, std = float(values.mean()), float(values.std(ddof=1))
    se = std / np.sqrt(values.size)
    margin = float(stats.t.ppf((1 + confidence) / 2, values.size - 1)) * se
    return MeanEstimate(mean, std, float(se), mean - margin, mean + margin, values.size, confidence)


def paired_difference(left: np.ndarray, right: np.ndarray) -> MeanEstimate:
    """Estimate E[left-right] using paired common-random-number trajectories."""
    left, right = np.asarray(left), np.asarray(right)
    if left.shape != right.shape:
        raise ValueError("Paired policy outcomes must have identical shapes.")
    return estimate_mean(left - right)


def expected_secant(
    workload: Workload, threshold: float, step: float, field: RandomField
) -> MeanEstimate:
    """Estimate a centered finite-difference slope of expected total price.

    This is not an unbiased derivative estimator: the reported interval
    excludes finite-difference bias, token rounding, and model uncertainty.
    Units are USD per threshold token. Use several steps as a bias probe.
    """
    if not np.isfinite(step) or step <= 0 or threshold <= step:
        raise ValueError("A positive finite step smaller than threshold is required.")
    upper = simulate(workload, threshold + step, field).costs
    lower = simulate(workload, threshold - step, field).costs
    return estimate_mean((upper - lower) / (2 * step))


def sweep_thresholds(
    workload: Workload,
    thresholds: list[float],
    replicates: int,
    seed: int,
    difference_step: float = 5_000,
) -> tuple[dict[str, object], np.ndarray]:
    """Explore a finite threshold grid with shared marks and paired secants.

    The grid minimum is a training-set selection, not proof of a global
    optimum. An independently drawn validation field evaluates that selected
    policy against no compaction without using it for further selection.
    """
    if not np.isfinite(difference_step) or difference_step <= 0:
        raise ValueError("Difference step must be positive and finite.")
    if not isinstance(replicates, int) or isinstance(replicates, bool) or replicates < 2:
        raise ValueError("Inference requires at least two independent trajectories.")
    if not thresholds or len(set(thresholds)) != len(thresholds):
        raise ValueError("A nonempty grid of unique thresholds is required.")
    if any(not np.isfinite(h) or h <= difference_step for h in thresholds):
        raise ValueError("Finite grid thresholds must exceed the difference step.")
    field = draw_random_field(workload, replicates, seed)
    all_points = set(thresholds) | {float("inf")}
    all_points |= {h - difference_step for h in thresholds}
    all_points |= {h + difference_step for h in thresholds}
    results = {h: simulate(workload, h, field) for h in sorted(all_points)}
    rows = []
    for h in sorted(thresholds):
        result = results[h]
        slope = (results[h + difference_step].costs - results[h - difference_step].costs) / (
            2 * difference_step
        )
        row = {
            "threshold_tokens": h,
            "expected_cost_usd": estimate_mean(result.costs).to_dict(),
            "paired_secant_usd_per_token": estimate_mean(slope).to_dict(),
            "difference_step_tokens": difference_step,
            "mean_compactions": float(result.compactions.mean()),
            "mean_cache_hits": float(result.cache_hits.mean()),
            "mean_cache_misses": float(result.cache_misses.mean()),
            "mean_recovery_above_threshold": float(result.recovery_above_threshold.mean()),
            "p99_max_context_tokens": float(np.quantile(result.max_context, 0.99)),
        }
        rows.append(row)
    chosen = min(thresholds, key=lambda h: float(results[h].costs.mean()))
    validation = draw_random_field(workload, replicates, seed + 1)
    selected_cost = simulate(workload, chosen, validation).costs
    no_reset_cost = simulate(workload, float("inf"), validation).costs
    report = {
        "workload": workload.to_dict(),
        "replicates": replicates,
        "seed": seed,
        "rows": rows,
        "selected_grid_threshold_tokens": chosen,
        "no_compaction_expected_cost_usd": estimate_mean(results[float("inf")].costs).to_dict(),
        "independent_validation": {
            "seed": seed + 1,
            "selected_expected_cost_usd": estimate_mean(selected_cost).to_dict(),
            "no_compaction_expected_cost_usd": estimate_mean(no_reset_cost).to_dict(),
            "paired_selected_minus_no_compaction_usd": paired_difference(
                selected_cost, no_reset_cost
            ).to_dict(),
        },
        "interpretation": {
            "data_status": "synthetic_unvalidated_workload_assumptions",
            "objective": "expected_total_API_cost_for_fixed_normal_call_count",
            "interval_scope": "pointwise_Monte_Carlo_error_conditional_on_model",
            "slope_scope": "centered_secant_not_exact_derivative_includes_no_bias_bound",
            "selection_scope": "finite_grid_exploration_not_global_optimum_or_simultaneous_CI",
            "capacity_scope": "no_hard_context_limit_or_price_tiers_enforced",
        },
    }
    samples = np.stack([results[h].costs for h in sorted(thresholds)], axis=0)
    return report, samples
