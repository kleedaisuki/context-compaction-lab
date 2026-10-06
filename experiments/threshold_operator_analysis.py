"""Execute exact occupation/adjoint identities and a moving-boundary calculation.

Run ``uv run python experiments/threshold_operator_analysis.py``. The finite
matrix entries are formal variables, not a fitted two-state engineering task.
They check an operator identity for dependent state evolution. The continuous
boundary fixture illustrates a regularity issue, not a threshold prediction.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from context_compaction_lab.control_symbolics import (
    FiniteControl,
    adjoint_derivative,
    performance_difference,
)


def matrix_checks() -> dict:
    """Prove exact polynomial identities with arbitrary symbolic ledger entries."""
    theta, phi, rho, beta = sp.symbols("theta phi rho beta", nonnegative=True)
    p = sp.Matrix(sp.symbols("p_i p_w p_r p_o", nonnegative=True))
    ledgers = tuple(sp.Matrix(2, 4, sp.symbols(f"l{t}_0:8", nonnegative=True)) for t in range(3))
    kernels = (
        sp.Matrix([[theta, 1 - theta], [beta, 1 - beta]]),
        sp.Matrix([[beta, 1 - beta], [theta, 1 - theta]]),
        sp.eye(2),
    )
    model = FiniteControl(sp.Matrix([[rho, 1 - rho]]), kernels, ledgers)
    alternative = FiniteControl(
        model.initial, tuple(kernel.subs(theta, phi) for kernel in kernels), ledgers
    )
    ledger = model.expected_ledger()
    invoice = model.invoice(p)
    derivative = adjoint_derivative(model, p, theta)
    policy_change = performance_difference(model, alternative, p)
    checks = {
        "occupation_invoice_residual": sp.expand(invoice - (ledger * p)[0]),
        "adjoint_residual": sp.expand(sp.diff(invoice, theta) - derivative),
        "policy_difference_residual": sp.expand(
            alternative.invoice(p) - invoice - policy_change
        ),
    }
    for category, price in enumerate(p):
        checks[f"price_gradient_residual_{category}"] = sp.expand(
            sp.diff(invoice, price) - ledger[category]
        )
    assert all(value == 0 for value in checks.values())
    return {
        "domain": "theta, phi, rho, beta in [0,1]; ledger entries nonnegative",
        "horizon": 3,
        "state_dimension": 2,
        "exact_ledger": [str(sp.factor(entry)) for entry in ledger],
        "checks": {key: str(value) for key, value in checks.items()},
        "parameter_derivative": str(sp.factor(derivative)),
        "scope": "arbitrary formal ledger coefficients; operator identity, not workload fit",
    }


def boundary_checks() -> dict:
    """Check density-weighted future advantage, and why pathwise diff misses it."""
    x, h = sp.symbols("x h", real=True)
    a, b, c = sp.symbols("a b c", nonnegative=True)
    continue_value, compact_value = a + b * x, c
    expected = sp.integrate(continue_value, (x, 0, h)) + sp.integrate(
        compact_value, (x, h, 1)
    )
    derivative = sp.diff(expected, h)
    boundary = (continue_value - compact_value).subs(x, h)
    assert sp.expand(derivative - boundary) == 0
    # Each fixed-x branch is constant in h away from its crossing. The Dirac
    # boundary term is precisely what an ordinary pathwise derivative omits.
    pathwise = sp.Piecewise((compact_value, h <= x), (continue_value, True))
    ordinary_path_derivative = sp.diff(pathwise, h)
    assert ordinary_path_derivative == 0
    return {
        "domain": "X uniform on [0,1], 0<h<1, a,b,c>=0",
        "expected_cost": str(sp.expand(expected)),
        "true_expected_derivative": str(derivative),
        "ordinary_pathwise_derivative": str(ordinary_path_derivative),
        "boundary_advantage": str(boundary),
        "interpretation": (
            "Q symbols include future costs; this is not an engineering approximation"
        ),
    }


def file_option_checks() -> dict:
    """Derive an open parameter region where equal-length states need opposite controls.

    One ordinary action remains, cache is cold, and a file is required with
    conditional probability alpha. State A has a qualifying file snapshot;
    B does not. Compact erases it and rebuilds base B plus summary S. Symbols
    are declared mechanism parameters, not fitted workload magnitudes.
    """
    x, base, summary, payload, alpha, instruction, suffix, background, output = sp.symbols(
        "X B S D alpha c u b o", nonnegative=True
    )
    p = sp.Matrix(sp.symbols("p_i p_w p_r p_o", nonnegative=True))
    keep_valid = sp.Matrix([[suffix, x + background, 0, output]])
    keep_missing = sp.Matrix([[suffix, x + background + alpha * payload, 0, output]])
    compact = sp.Matrix(
        [[x + instruction + suffix, base + summary + background + alpha * payload,
          0, summary + output]]
    )
    delta_valid = sp.expand(((compact - keep_valid) * p)[0])
    delta_missing = sp.expand(((compact - keep_missing) * p)[0])
    option = sp.expand(delta_valid - delta_missing)
    assert sp.expand(option - alpha * payload * p[1]) == 0
    return {
        "domain": "cold eligible input; alpha in [0,1]; compact clears file/guard",
        "compact_minus_keep_valid": str(delta_valid),
        "compact_minus_keep_missing": str(delta_missing),
        "valid_fact_option_gap": str(option),
        "opposite_control_region": "-alpha*D*p_w < T < 0",
        "T": "p_i*(X+c) + p_w*(B+S-X) + p_o*S",
        "interpretation": (
            "T<0 makes compact best for missing file, but T+alpha*D*p_w>0 "
            "makes keep best for valid file; region is open, not an isolated point"
        ),
    }


def main() -> None:
    """Persist exact expressions and zero residuals from actual SymPy execution."""
    report = {
        "sympy_version": sp.__version__,
        "operator_checks": matrix_checks(),
        "boundary_check": boundary_checks(),
        "file_option_check": file_option_checks(),
    }
    destination = Path(".cache/theory/threshold-operators.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["operator_checks"]["checks"], indent=2))
    print(json.dumps(report["boundary_check"], indent=2))
    print(json.dumps(report["file_option_check"], indent=2))


if __name__ == "__main__":
    main()
