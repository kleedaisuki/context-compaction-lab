"""Derive an exact analytic bridge for a finite-resolution renewal model.

Run with ``uv run python experiments/finite_continuum_bridge.py``. These
identities explain continuum use; the illustrative scenario is not a fitted
engineering workload or a simulation-based optimum.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def derive() -> dict[str, object]:
    """Check lattice identities and return a reproducible explanatory scenario."""
    k = sp.symbols("k", integer=True, nonnegative=True)
    r = sp.symbols("r", nonnegative=True)
    g, a, c = sp.symbols("g A c", positive=True)
    gap = g * (k + r)
    lag = g * (k + 1) * (k / 2 + r)
    ripple = g * r * (1 - r) / 2
    assert sp.simplify(lag - gap**2 / (2 * g) - gap / 2 - ripple) == 0
    assert sp.simplify(g / 8 - ripple - g * (r - sp.Rational(1, 2)) ** 2 / 2) == 0

    # The cost is constant on (k*g, (k+1)*g]; compare neighboring plateaus.
    cost = a / (k + 1) + c * g * k / 2
    next_cost = a / (k + 2) + c * g * (k + 1) / 2
    boundary_lag = g * (k + 1) * (k + 2) / 2
    jump = (c * boundary_lag - a) / ((k + 1) * (k + 2))
    assert sp.simplify(next_cost - cost - jump) == 0

    growth = 2000
    fee_ratio = 2_500_000
    plateau = 49
    canonical = sp.Rational(fee_ratio + growth * plateau * (plateau + 1) // 2, plateau + 1)
    assert growth * plateau < canonical <= growth * (plateau + 1)
    assert lag.subs({g: growth, k: plateau, r: canonical / growth - plateau}) == fee_ratio
    return {
        "scope": "Exact constant-growth renewal ledger; illustrative, not empirical",
        "lag_identity": str(lag),
        "lattice_ripple": str(ripple),
        "ripple_upper_bound": "g/8 for 0 <= r <= 1",
        "cost_jump": str(jump),
        "scenario": {
            "growth_tokens": growth,
            "fee_over_carry_token_actions": fee_ratio,
            "fluid_gap_tokens": int(sp.sqrt(2 * growth * fee_ratio)),
            "canonical_exact_gap_tokens": int(canonical),
            "optimal_gap_plateau": {"lower_exclusive": 98000, "upper_inclusive": 100000},
        },
        "midpoint_quantization": {
            "grid_states": 1000,
            "cdf_sup_error": 1 / 2000,
            "coupled_mean_absolute_error": 1 / 4000,
            "total_variation_distance_sup_event_convention": 1,
        },
    }


def main() -> None:
    """Persist small symbolic findings inside the repository cache."""
    result = derive()
    destination = Path(__file__).resolve().parents[1] / ".cache" / "finite-continuum-bridge"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
