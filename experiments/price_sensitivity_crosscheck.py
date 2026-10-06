"""Bounded independent checks of price basis, core derivatives and geometry.

Run ``uv run python experiments/price_sensitivity_crosscheck.py``. The probe
uses constructed laws, never private traces or paid API calls. Four-category
expectations are checked against an independent state DP; smooth price
derivatives use direct inversions and the Hessian uses a closed exponential
core value. No marked-controller Jacobian is claimed. A small aggregate report
is written beneath ``.cache/price-sensitivity-crosscheck/``.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
from renewal_ledger_crosscheck import category_cycle_dp

from context_compaction_lab.config import Pricing
from context_compaction_lab.price_sensitivity import (
    core_sensitivity,
    expected_category_rates,
    price_array,
)
from context_compaction_lab.renewal_numerics import RenewalLedger, empirical_renewal


def direct_root(renewal: dict, ledger: RenewalLedger, scale: float = 1) -> float:
    """Invert an explicitly expanded price ratio, without importing sensitivities.

    Scaling the WHOLE increment law uses D_scale(L)=scale*D(L/scale).
    Infinitesimally changing and then rounding raw increments is not equivalent.
    """
    p, q, s, b = ledger.prices, ledger.cache_hit, ledger.reset, ledger.stable_base
    fee = (
        p.input * (ledger.compaction_instruction + (1 - q) * s)
        + q * p.write * (s - b)
        + q * p.read * b
        + p.output * ledger.summary
    )
    carry = (1 - q) * p.write + q * p.read
    return float(s + scale * np.interp(fee / (carry * scale), renewal["lag"], renewal["gaps"]))


def exponential_core_value(prices: np.ndarray, ledger: RenewalLedger, mean: float) -> float:
    """Evaluate a directly optimized smooth exponential-core value for Hessian checks.

    This is the UNMARKED core, not a discrete-policy or marked optimum. The
    complete physical baseline here uses tail_fraction=0 and ordinary output 7.
    Its positive-density interior optimizer is locally stable and unique.
    """
    pi, pw, pr, po = prices
    q, s, b = ledger.cache_hit, ledger.reset, ledger.stable_base
    carry = (1 - q) * pw + q * pr
    compactor = (1 - q) * pi + q * pr
    fee = pi * (ledger.compaction_instruction + (1 - q) * s)
    fee += q * pw * (s - b) + q * pr * b + po * ledger.summary
    gap = np.sqrt(mean**2 + 2 * mean * fee / carry) - mean
    duration, area = 1 + gap / mean, gap**2 / (2 * mean)
    baseline = pi * ledger.ordinary_suffix + po * 7 + (pw + compactor) * mean
    return float(baseline + carry * s + (fee + carry * area) / duration)


def main() -> None:
    """Run small identity/contrast checks and record their reproducible assumptions."""
    values = np.array([0, 1, 3, 8], dtype=np.int64)
    probabilities = np.array([0.2, 0.2, 0.3, 0.3], dtype=float)
    renewal = empirical_renewal(values, probabilities, 1, 2000)
    category_errors = []
    for q in (0, 0.6, 1):
        for theta in (0, 0.4, 1):
            ledger = RenewalLedger(
                reset=100,
                summary=10,
                stable_base=20,
                cache_hit=q,
                tail_fraction=theta,
            )
            basis = expected_category_rates(renewal, ledger, output_mean=7)
            for gap in (1, 3, 8, 17, 55):
                direct = category_cycle_dp(values, probabilities, gap, ledger)
                category_errors.append(
                    np.abs(basis[gap - 1] - np.array(direct.categories) / direct.duration)
                )

    ledger = RenewalLedger(reset=100, summary=10, stable_base=20, cache_hit=0.63)
    sensitivity = core_sensitivity(renewal, ledger)
    prices = price_array(ledger.prices)
    numerical_gradient = []
    for name in ("input", "write", "read", "output"):
        price, step = getattr(ledger.prices, name), getattr(ledger.prices, name) * 1e-5
        plus = replace(ledger, prices=replace(ledger.prices, **{name: price + step}))
        minus = replace(ledger, prices=replace(ledger.prices, **{name: price - step}))
        numerical_gradient.append(
            (direct_root(renewal, plus) - direct_root(renewal, minus)) / (2 * step)
        )
    gradient_error = float(
        np.max(np.abs(np.array(numerical_gradient) / np.array(sensitivity.price_gradient) - 1))
    )
    step = 1e-5
    paths = {
        "hit": (
            replace(ledger, cache_hit=ledger.cache_hit + step),
            replace(ledger, cache_hit=ledger.cache_hit - step),
            sensitivity.hit_gradient,
        ),
        "stable_reclassify": (
            replace(ledger, stable_base=ledger.stable_base + step),
            replace(ledger, stable_base=ledger.stable_base - step),
            sensitivity.stable_reclassification_gradient,
        ),
        "stable_add": (
            replace(ledger, reset=ledger.reset + step, stable_base=ledger.stable_base + step),
            replace(ledger, reset=ledger.reset - step, stable_base=ledger.stable_base - step),
            sensitivity.added_stable_gradient,
        ),
        "volatile_add": (
            replace(ledger, reset=ledger.reset + step),
            replace(ledger, reset=ledger.reset - step),
            sensitivity.added_volatile_gradient,
        ),
        "summary_preserve": (
            replace(ledger, reset=ledger.reset + step, summary=ledger.summary + step),
            replace(ledger, reset=ledger.reset - step, summary=ledger.summary - step),
            sensitivity.summary_preserve_material_gradient,
        ),
        "summary_replace": (
            replace(ledger, summary=ledger.summary + step),
            replace(ledger, summary=ledger.summary - step),
            sensitivity.summary_replace_material_gradient,
        ),
    }
    path_results = {
        name: {
            "numeric": (direct_root(renewal, plus) - direct_root(renewal, minus)) / (2 * step),
            "analytic": analytic,
        }
        for name, (plus, minus, analytic) in paths.items()
    }
    growth_elasticity = (
        direct_root(renewal, ledger, 1 + step) - direct_root(renewal, ledger, 1 - step)
    ) / (2 * step * sensitivity.gap)

    basis = expected_category_rates(renewal, ledger, 7)
    first_prices, second_prices = prices, prices * np.array([1.7, 0.4, 3.0, 0.8])
    fraction = 0.37
    mixed_prices = fraction * first_prices + (1 - fraction) * second_prices
    mixed_value = float(np.min(basis @ mixed_prices))
    endpoint_average = float(
        fraction * np.min(basis @ first_prices) + (1 - fraction) * np.min(basis @ second_prices)
    )
    radial_error = float(np.max(np.abs((basis @ (2 * prices)) - 2 * (basis @ prices))))

    # Hessian checks require one smooth active branch, not a lattice argmin.
    mean = 4.0
    carry = (1 - ledger.cache_hit) * prices[1] + ledger.cache_hit * prices[2]
    fee_vector = np.array(
        [
            ledger.compaction_instruction + (1 - ledger.cache_hit) * ledger.reset,
            ledger.cache_hit * (ledger.reset - ledger.stable_base),
            ledger.cache_hit * ledger.stable_base,
            ledger.summary,
        ]
    )
    carry_vector = np.array([0, 1 - ledger.cache_hit, ledger.cache_hit, 0])
    ratio = float(np.dot(prices, fee_vector) / carry)
    gap = np.sqrt(mean**2 + 2 * mean * ratio) - mean
    duration = 1 + gap / mean
    alpha = fee_vector - ratio * carry_vector
    predicted_hessian = -np.outer(alpha, alpha) / (mean * carry * duration**3)
    numerical_hessian = np.zeros((4, 4))
    steps = prices * 1e-3
    for row in range(4):
        for column in range(4):
            left = np.eye(4)[row] * steps[row]
            right = np.eye(4)[column] * steps[column]
            numerical_hessian[row, column] = (
                exponential_core_value(prices + left + right, ledger, mean)
                - exponential_core_value(prices + left - right, ledger, mean)
                - exponential_core_value(prices - left + right, ledger, mean)
                + exponential_core_value(prices - left - right, ledger, mean)
            ) / (4 * steps[row] * steps[column])
    hessian_relative_error = float(
        np.linalg.norm(numerical_hessian - predicted_hessian) / np.linalg.norm(predicted_hessian)
    )

    atomlaw = empirical_renewal(np.array([1]), None, 1, 100)
    atomledger = RenewalLedger(
        reset=10,
        summary=0,
        stable_base=0,
        compaction_instruction=0,
        prices=Pricing(1, 1, 0, 0),
        cache_hit=0,
    )
    atom_rejected = False
    try:
        core_sensitivity(atomlaw, atomledger)
    except ValueError as error:
        atom_rejected = "atom" in str(error)
    epsilon = 1e-6
    atom_write_direction = (
        direct_root(atomlaw, replace(atomledger, prices=Pricing(1, 1 + epsilon, 0, 0)))
        - direct_root(atomlaw, atomledger)
    ) / epsilon
    atom_growth_elasticity = (
        direct_root(atomlaw, atomledger, 1 + epsilon) - direct_root(atomlaw, atomledger)
    ) / (epsilon * 4)

    assert np.max(category_errors) < 1e-10
    assert gradient_error < 1e-7
    assert max(abs(row["numeric"] - row["analytic"]) for row in path_results.values()) < 1e-5
    assert abs(growth_elasticity - sensitivity.growth_scale_gap_elasticity) < 1e-7
    assert abs(sum(sensitivity.threshold_price_elasticity)) < 1e-12
    assert mixed_value >= endpoint_average - 1e-15
    assert radial_error < 1e-15
    assert hessian_relative_error < 1e-4
    assert atom_rejected
    report = {
        "law": {"increments": values.tolist(), "probabilities": probabilities.tolist()},
        "category_cases": len(category_errors),
        "maximum_category_error_I_W_R_O": np.max(category_errors, axis=0).tolist(),
        "non_atom_core_gap": sensitivity.gap,
        "maximum_relative_price_gradient_error": gradient_error,
        "parameter_path_numeric_vs_analytic": path_results,
        "growth_scale_gap_elasticity": growth_elasticity,
        "sum_threshold_price_elasticities": sum(sensitivity.threshold_price_elasticity),
        "radial_repricing_maximum_error": radial_error,
        "finite_policy_concavity_gap": mixed_value - endpoint_average,
        "smooth_exponential_hessian_relative_error": hessian_relative_error,
        "smooth_exponential_predicted_hessian_singular_values": np.linalg.svd(
            predicted_hessian, compute_uv=False
        ).tolist(),
        "atom": {
            "gap": 4,
            "ordinary_gradient_rejected": atom_rejected,
            "positive_write_price_direction": atom_write_direction,
            "positive_growth_scale_gap_elasticity": atom_growth_elasticity,
        },
        "scope": (
            "Constructed-law identities and local smooth-core contrasts; not provider performance"
        ),
    }
    destination = Path(__file__).resolve().parents[1] / ".cache" / "price-sensitivity-crosscheck"
    destination.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    (destination / "results.json").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
