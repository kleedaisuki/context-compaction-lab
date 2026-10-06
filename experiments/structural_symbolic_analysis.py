"""Derive exact structural laws from the actual simulator's integer occupations.

Run ``uv run python experiments/structural_symbolic_analysis.py`` from the root.
The previous finite fixture is a checkable extraction basis, not an empirical
workload claim. All results in the artifact are exact symbolic/rational values;
no fitted polynomial, floating probability sum, or independent ledger is used.
"""

from __future__ import annotations

import json
import math
import runpy
import time
from pathlib import Path

import numpy as np
import sympy as sp

from context_compaction_lab.structural_symbolics import (
    ALPHA,
    CHANNELS,
    PRICES,
    OccupationVector,
    ThresholdBand,
    ThresholdCurve,
    bernoulli_occupation,
    bernstein_coefficients,
    exact_integer_values,
    read_write_crossover,
)
from context_compaction_lab.working_set_config import (
    ActionField,
    WorkingSetPolicy,
    WorkingSetWorkload,
)
from context_compaction_lab.working_set_simulation import simulate_working_set

EXACT_PRICES = (sp.Rational(3, 10**6), sp.Rational(15, 4 * 10**6),
                sp.Rational(3, 10**7), sp.Rational(15, 10**6))
"""Default four-price values represented as rationals, not float conversions."""
EXACT_ALPHA = sp.Rational(7, 20)
"""A rational evaluation point; alpha remains symbolic in every structural curve."""


def simulator_curve(
    workload: WorkingSetWorkload, policy: WorkingSetPolicy, field: ActionField,
    paths: np.ndarray,
) -> ThresholdCurve:
    """Extract exact occupation cells from actual-engine transitions for all h>0."""
    infinity = simulate_working_set(workload, policy, math.inf, field)
    upper = int(infinity.max_context.max()) + 1
    bands: list[ThresholdBand] = []
    previous: np.ndarray | None = None
    for threshold in range(1, upper + 1):
        result = simulate_working_set(workload, policy, threshold, field)
        raw = np.stack([getattr(result, channel) for channel in CHANNELS])
        if previous is not None and np.array_equal(raw, previous):
            occupation = bands[-1].occupation
        else:
            occupation = bernoulli_occupation(paths, result)
        if bands and occupation == bands[-1].occupation:
            bands[-1] = ThresholdBand(bands[-1].lower, threshold, occupation)
        else:
            bands.append(ThresholdBand(threshold - 1, threshold, occupation))
        previous = raw
    assert bands[-1].occupation == bernoulli_occupation(paths, infinity)
    bands[-1] = ThresholdBand(bands[-1].lower, None, bands[-1].occupation)
    curve = ThresholdCurve(tuple(bands))
    for threshold in (64, 100, 157, 178, 179, 269):
        result = simulate_working_set(workload, policy, threshold - 0.5, field)
        assert curve.at(threshold).entries == bernoulli_occupation(paths, result).entries
    return curve


def independent_rational_check(
    workload: WorkingSetWorkload, policy: WorkingSetPolicy, field: ActionField,
    paths: np.ndarray, threshold: int, occupation: OccupationVector,
) -> sp.Expr:
    """Compare grouped polynomials with a direct per-path rational invoice sum."""
    result = simulate_working_set(workload, policy, threshold, field)
    integer_columns = [exact_integer_values(getattr(result, channel)) for channel in CHANNELS]
    total = sp.S.Zero
    for index, path in enumerate(paths):
        k = int(path.sum())
        weight = EXACT_ALPHA**k * (1 - EXACT_ALPHA)**(len(path) - k)
        invoice = sum(price * column[index] for price, column
                      in zip(EXACT_PRICES, integer_columns))
        total += weight * invoice
    symbolic = occupation.cost(EXACT_PRICES).subs(ALPHA, EXACT_ALPHA)
    assert total == symbolic
    assert np.isclose(float(total), float(np.dot(
        EXACT_ALPHA.evalf()**paths.sum(axis=1)
        * (1 - EXACT_ALPHA.evalf())**(paths.shape[1] - paths.sum(axis=1)), result.costs,
    )), atol=1e-14)
    return total


def serialized_occupation(occupation: OccupationVector) -> dict[str, object]:
    """Publish exact polynomial coefficients and factorizations for independent reuse."""
    return {
        channel: {
            "polynomial": str(entry), "factorization": str(sp.factor(entry)),
            "coefficients_descending": [str(value) for value in sp.Poly(entry, ALPHA).all_coeffs()],
        }
        for channel, entry in zip(CHANNELS, occupation.entries)
    }


def serialize_curve(curve: ThresholdCurve) -> dict[str, object]:
    """Preserve the full symbolic-alpha step law and distributional jump derivative."""
    return {
        "bands": [{"lower_exclusive": band.lower, "upper_inclusive": band.upper,
                   "occupation": serialized_occupation(band.occupation)}
                  for band in curve.bands],
        "piecewise_cost": str(curve.piecewise_cost()),
        "distributional_derivative": str(curve.distributional_derivative()),
        "integer_delta_jumps": [
            {"integer_k": left.upper,
             "C_k_plus_1_minus_C_k": str(sp.factor(
                 right.occupation.difference(left.occupation).cost()))}
            for left, right in zip(curve.bands, curve.bands[1:])
        ],
    }


def lower_price_envelope(curves: dict[str, ThresholdCurve]) -> list[dict[str, object]]:
    """Find exact global policy/threshold phases as r=p_r/p_w varies over r>=0.

    Hold alpha=7/20, p_i/p_w=4/5, p_o/p_w=4. The hull construction uses only
    exact rational intersections. Endpoint ties are separately evaluated over
    every candidate, including candidates optimal only at a single breakpoint.
    """
    candidates: dict[tuple, list[dict]] = {}
    for name, curve in curves.items():
        for band in curve.bands:
            i, w, read, output = band.occupation.substitute({ALPHA: EXACT_ALPHA}).entries
            key = (read, sp.Rational(4, 5) * i + w + 4 * output)
            candidates.setdefault(key, []).append({
                "policy": name, "integer_lower": band.lower + 1,
                "integer_upper": band.upper,
            })
    by_slope: dict[sp.Expr, tuple] = {}
    for slope, intercept in candidates:
        if slope not in by_slope or intercept < by_slope[slope][1]:
            by_slope[slope] = (slope, intercept)
    stack: list[tuple[tuple, sp.Expr]] = []
    for line in sorted(by_slope.values(), key=lambda item: item[0], reverse=True):
        start = -sp.oo
        while stack:
            previous, previous_start = stack[-1]
            start = sp.cancel((line[1] - previous[1]) / (previous[0] - line[0]))
            if start > previous_start:
                break
            stack.pop()
        if not stack:
            start = -sp.oo
        stack.append((line, start))
    phases = []
    for index, (line, start) in enumerate(stack):
        stop = stack[index + 1][1] if index + 1 < len(stack) else sp.oo
        if stop <= 0:
            continue
        lower = max(start, sp.S.Zero)
        probe = lower + 1 if stop == sp.oo else (lower + stop) / 2
        assert line[0] * probe + line[1] == min(s * probe + b for s, b in candidates)
        at_lower = min(s * lower + b for s, b in candidates)
        ties = [description for (s, b), descriptions in candidates.items()
                if s * lower + b == at_lower for description in descriptions]
        phases.append({
            "ratio_lower": str(lower), "ratio_upper": str(stop),
            "ratio_lower_numeric": float(lower),
            "ratio_upper_numeric": None if stop == sp.oo else float(stop),
            "normalized_cost_intercept": str(line[1]),
            "normalized_cost_slope": str(line[0]),
            "optimizers_inside_interval": candidates[line],
            "optimizers_at_lower_endpoint": ties,
        })
    assert all(sp.Rational(phases[i]["normalized_cost_slope"])
               > sp.Rational(phases[i + 1]["normalized_cost_slope"])
               for i in range(len(phases) - 1))
    return phases


def main() -> None:
    """Execute exact symbolic extraction, comparisons, derivatives, and rational checks."""
    started = time.perf_counter()
    prior = runpy.run_path(str(Path(__file__).with_name("working_set_exact_control.py")))
    paths, _ = prior["enumerate_demands"](8, 0.35)
    workload, field = prior["ordinary_fixture"](paths)
    policy_map = prior["policies"]()
    curves = {name: simulator_curve(workload, policy, field, paths)
              for name, policy in policy_map.items()}
    h100 = {name: curve.at(100) for name, curve in curves.items()}
    checks = {name: str(independent_rational_check(workload, policy_map[name], field, paths,
                                                  100, occupation))
              for name, occupation in h100.items()}
    threshold_delta = curves["first_use"].at(157).difference(curves["first_use"].at(269))
    crossover = read_write_crossover(threshold_delta, sp.Rational(4, 5), sp.Integer(4))
    assert sp.cancel(threshold_delta.cost(
        (sp.Rational(4, 5), 1, crossover, 4))) == 0
    crossing_at_alpha = sp.factor(crossover.subs(ALPHA, EXACT_ALPHA))
    stable_delta = h100["stable_first_use"].difference(h100["first_use"])
    preservation_delta = h100["preserve_with_guard"].difference(h100["first_use"])
    q = sp.Symbol("q", nonnegative=True)
    preservation_certificate = [sp.expand(sp.cancel(entry / (26 * ALPHA * (1 - ALPHA)))
                                          .subs(ALPHA, 1 - q))
                                for entry in preservation_delta.entries]
    assert all(all(coefficient >= 0 for coefficient in sp.Poly(entry, q).all_coeffs())
               for entry in preservation_certificate)
    threshold_bernstein = [bernstein_coefficients(entry, 8)
                           for entry in threshold_delta.entries]
    assert all(value < 0 for value in threshold_bernstein[2])
    assert all(value > 0 for value in threshold_bernstein[1])
    crossing_derivative = sp.cancel(sp.diff(crossover, ALPHA))
    numerator = sp.fraction(crossing_derivative)[0]
    isolated = sp.Poly(numerator, ALPHA).intervals(eps=sp.Rational(1, 10**8))
    interior_roots = [(bounds, multiplicity) for bounds, multiplicity in isolated
                      if 0 < bounds[0] and bounds[1] < 1]
    assert len(interior_roots) == 1 and interior_roots[0][1] == 1
    assert crossing_derivative.subs(ALPHA, 0) < 0
    assert crossing_derivative.subs(ALPHA, 1) > 0
    demand_cost = h100["first_use"].cost(EXACT_PRICES)
    curvature_counterexample = curves["first_use"].at(71).cost(EXACT_PRICES)
    positive_curvature = sp.diff(curvature_counterexample, ALPHA, 2).subs(ALPHA, EXACT_ALPHA)
    assert positive_curvature > 0
    output = {
        "scope": "general price-independent finite-ledger structure; exact extraction control",
        "general_cost": "C_pi(h,alpha,p)=sum_j p_j L_pi,j(h,alpha)",
        "alpha_domain": "[0,1]", "alpha_evaluation": str(EXACT_ALPHA),
        "workload": workload.to_dict(),
        "h100_occupations": {name: serialized_occupation(occupation)
                              for name, occupation in h100.items()},
        "h100_exact_prices": [str(price) for price in EXACT_PRICES],
        "h100_independent_exact_invoices": checks,
        "h100_demand_cost_polynomial": str(sp.factor(demand_cost)),
        "h100_demand_cost_derivative": str(sp.factor(sp.diff(demand_cost, ALPHA))),
        "h100_demand_derivative_at_7_over_20": str(sp.diff(demand_cost, ALPHA)
                                                     .subs(ALPHA, EXACT_ALPHA)),
        "h100_price_gradient": [str(entry) for entry in h100["first_use"].entries],
        "h100_price_hessian": str(sp.hessian(h100["first_use"].cost(), PRICES)),
        "stable_minus_first_use_hyperplane": str(sp.factor(stable_delta.cost())),
        "preserve_guard_minus_first_use_hyperplane": str(sp.factor(preservation_delta.cost())),
        "preserve_guard_q_nonnegative_coefficient_certificate": [
            str(entry) for entry in preservation_certificate],
        "threshold_157_minus_269": serialized_occupation(threshold_delta),
        "threshold_read_write_crossover_symbolic_alpha": str(sp.factor(crossover)),
        "threshold_read_write_crossover_at_7_over_20": str(crossing_at_alpha),
        "threshold_read_write_crossover_numeric": float(crossing_at_alpha),
        "threshold_read_write_crossover_alpha_derivative": str(sp.factor(sp.diff(crossover,
                                                                                 ALPHA))),
        "threshold_difference_bernstein_sign_certificate": [
            [str(value) for value in coefficients] for coefficients in threshold_bernstein],
        "threshold_crossover_alpha_stationary_root_interval": [
            str(endpoint) for endpoint in interior_roots[0][0]],
        "threshold_crossover_alpha_stationary_root_multiplicity": interior_roots[0][1],
        "threshold_crossover_alpha_derivative_at_7_over_20": str(crossing_derivative
                                                                .subs(ALPHA, EXACT_ALPHA)),
        "demand_curvature_counterexample": {
            "physical_threshold": 71,
            "cost_polynomial": str(sp.factor(curvature_counterexample)),
            "second_derivative_at_7_over_20": str(positive_curvature),
        },
        "global_price_phases": lower_price_envelope(curves),
        "curves": {name: serialize_curve(curve) for name, curve in curves.items()},
    }
    output["runtime_seconds"] = time.perf_counter() - started
    destination = Path(".cache/structural-symbolic-analysis/results.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items()
                      if key not in ("curves", "h100_occupations", "workload")}, indent=2))


if __name__ == "__main__":
    main()
