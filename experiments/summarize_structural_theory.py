"""Publish compact exact theory evidence and independently certify the price hull.

Run after the three maintained symbolic/control experiments and formal check.
Only reviewed aggregate expressions are published; full regenerable formulas
and compiler objects stay under .cache. Hull certification checks EVERY
candidate line at both interval endpoints (or asymptotic slope), so it is not
another sample-point price sweep.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import sympy as sp


def read(path: str) -> dict:
    """Read an actually executed artifact, never invent a numerical result."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def certify_price_hull(symbolic: dict) -> dict:
    """Prove each rational lower-envelope interval beats every extracted line."""
    alpha = sp.Symbol("alpha", nonnegative=True)
    candidates = []
    for curve in symbolic["curves"].values():
        for band in curve["bands"]:
            values = [
                sp.sympify(band["occupation"][key]["polynomial"], locals={"alpha": alpha}).subs(
                    alpha, sp.Rational(7, 20)
                )
                for key in ("input_tokens", "write_tokens", "read_tokens", "output_tokens")
            ]
            intercept = sp.Rational(4, 5) * values[0] + values[1] + 4 * values[3]
            candidates.append((intercept, values[2]))
    checks = 0
    for phase in symbolic["global_price_phases"]:
        lower, upper = sp.sympify(phase["ratio_lower"]), sp.sympify(phase["ratio_upper"])
        intercept = sp.sympify(phase["normalized_cost_intercept"])
        slope = sp.sympify(phase["normalized_cost_slope"])
        assert (intercept, slope) in candidates
        for candidate_intercept, candidate_slope in candidates:
            difference = candidate_intercept - intercept
            slope_difference = candidate_slope - slope
            assert difference + lower * slope_difference >= 0
            if upper == sp.oo:
                assert slope_difference >= 0
            else:
                assert difference + upper * slope_difference >= 0
            checks += 2
    return {
        "candidate_lines_including_duplicates": len(candidates),
        "certified_intervals": len(symbolic["global_price_phases"]),
        "exact_endpoint_or_tail_inequalities": checks,
        "domain": "alpha=7/20; p_i/p_w=4/5; p_o/p_w=4; p_r/p_w>=0",
        "scope": "all extracted six-policy threshold cells, not every admissible controller",
    }


def main() -> None:
    """Combine observed SymPy residuals, exact certificates and actual Lean audit."""
    operators = read(".cache/theory/threshold-operators.json")
    symbolic = read(".cache/structural-symbolic-analysis/results.json")
    control = read(".cache/structural-control/counterexample.json")
    audit = Path(".cache/lean/verification.log").read_text(encoding="utf-8-sig")
    source = Path("formal/Structural.lean").read_text(encoding="utf-8")
    declarations = len(re.findall(r"^theorem ", source, re.MULTILINE))
    assert declarations == 21
    assert "sorryAx" not in audit
    assert len(re.findall(r"'ContextCompaction\.", audit)) == declarations
    selected_keys = (
        "h100_occupations",
        "h100_demand_cost_polynomial",
        "h100_demand_cost_derivative",
        "h100_price_gradient",
        "h100_price_hessian",
        "stable_minus_first_use_hyperplane",
        "preserve_guard_minus_first_use_hyperplane",
        "preserve_guard_q_nonnegative_coefficient_certificate",
        "threshold_read_write_crossover_symbolic_alpha",
        "threshold_read_write_crossover_at_7_over_20",
        "threshold_crossover_alpha_stationary_root_interval",
        "demand_curvature_counterexample",
        "global_price_phases",
    )
    result = {
        "version": "0.3.0",
        "scope": "structural_theory_exact_finite_checks_not_production_threshold_advice",
        "operator_checks": operators,
        "symbolic_structure": {key: symbolic[key] for key in selected_keys},
        "price_hull_certificate": certify_price_hull(symbolic),
        "control_certificate": control["bellman_flow_certificate"],
        "state_insufficiency": control["states"],
        "lean": {
            "version": audit.splitlines()[0],
            "checked_theorem_count": declarations,
            "custom_axioms_or_admitted_proofs": False,
            "standard_foundations": ["propext", "Quot.sound", "Classical.choice"],
            "scope": "finite ledgers/weights and rational threshold trees; not Python refinement",
        },
    }
    destination = Path("docs/research/structural-results.json")
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result["price_hull_certificate"], indent=2))
    print(f"Published structural metadata; Lean checked {declarations} theorems.")


if __name__ == "__main__":
    main()
