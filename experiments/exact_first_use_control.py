"""Verify mandatory first-use identities with exact finite path enumeration.

This maintained research probe checks warm-ledger theory, not the production
simulator or any empirical workload law. Run with the project uv environment.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import sympy as sp


def verify_fixed_cycle() -> dict[str, float]:
    """Enumerate all eight-action paths and compare invoice identities."""
    m, a, d = 8, 0.2, 12000
    pw, pr, kappa = 3.75e-6, 0.30e-6, 0.30e-6
    first_fee = (pw + kappa) * d
    probability = loads = carries = cost = 0.0
    for path in itertools.product((False, True), repeat=m):
        p = a ** sum(path) * (1 - a) ** (m - sum(path))
        k = next((n for n, use in enumerate(path, start=1) if use), m + 1)
        loaded = k <= m
        reads = max(m - k, 0)
        probability += p
        loads += p * loaded
        carries += p * reads
        cost += p * (first_fee * loaded + pr * d * reads)
    u = 1 - (1 - a) ** m
    expected_carries = m - u / a
    expected_cost = first_fee * u + pr * d * expected_carries
    eager = first_fee + pr * d * (m - 1)
    saving = first_fee * (1 - a) ** m + pr * d * (u / a - 1)
    for actual, expected in (
        (probability, 1), (loads, u), (carries, expected_carries),
        (cost, expected_cost), (eager - cost, saving),
    ):
        assert math.isclose(actual, expected, abs_tol=1e-12)
    return {
        "ordinary_actions": m, "demand_probability": a,
        "payload_tokens": d, "first_use_probability": u,
        "post_load_read_count": carries, "lazy_invoice_usd": cost,
        "eager_invoice_usd": eager, "saving_usd": eager - cost,
    }


def verify_endogenous_cycle() -> dict[str, float]:
    """Enumerate the threshold example where first use shortens its cycle."""
    a = 0.5
    probability = expected_t = loads = carries = marginal_pgf = 0.0
    for path in itertools.product((False, True), repeat=2):
        p = a ** sum(path) * (1 - a) ** (2 - sum(path))
        t = 1 if path[0] else 2
        k = next((n for n, use in enumerate(path, start=1) if use), 3)
        probability += p
        expected_t += p * t
        loads += p * (k <= t)
        carries += p * max(t - k, 0)
        marginal_pgf += p * (1 - a) ** t
    assert probability == 1.0
    assert expected_t == 1.5 and loads == 0.75 and carries == 0.0
    assert 1 - marginal_pgf == 0.625
    assert carries == expected_t - loads / a
    return {
        "expected_ordinary_actions": expected_t,
        "actual_first_use_probability": loads,
        "independent_T_plugin_probability": 1 - marginal_pgf,
        "actual_post_load_read_count": carries,
        "incorrect_plugin_read_count": expected_t - (1 - marginal_pgf) / a,
    }


def verify_symbolic_slopes() -> dict[str, bool]:
    """Check derivative identities of fixed-duration and passive-clock models."""
    m, a, d, pr, pw, kappa, g, fee = sp.symbols(
        "m a d pr pw kappa g fee", positive=True
    )
    u = 1 - (1 - a) ** m
    beta = d * (pw + kappa - pr / a)
    rate = pr * g * (m - 1) / 2 + fee / m + pr * d + beta * u / m
    derivative = pr * g / 2 - fee / m**2 + beta * (m * sp.diff(u, m) - u) / m**2
    assert sp.simplify(sp.diff(rate, m) - derivative) == 0
    h, s = sp.symbols("h s", positive=True)
    duration = 1 + (h - s) / g
    probability = 1 - (1 - a) * sp.exp(-a * (h - s) / g)
    file_rate = pr * d + beta * probability / duration
    file_derivative = beta * (
        sp.diff(probability, h) * duration - probability / g
    ) / duration**2
    assert sp.simplify(sp.diff(file_rate, h) - file_derivative) == 0
    return {"fixed_duration_derivative": True, "passive_threshold_derivative": True}


def main() -> None:
    """Run all checks and preserve numerical output in the workspace cache."""
    result = {
        "fixed_cycle": verify_fixed_cycle(),
        "endogenous_cycle": verify_endogenous_cycle(),
        "symbolic_checks": verify_symbolic_slopes(),
    }
    text = json.dumps(result, indent=2)
    destination = Path(".cache/experiments/first-use-reload/exact-control.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
