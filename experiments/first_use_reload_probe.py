"""Discriminate eager reset volume from mandatory first-use restoration.

Run ``uv run python experiments/first_use_reload_probe.py``. This is an
idealized fixed-duration-cycle probe, not a new production workload profile.
File availability and prefix reuse are distinct; here ordinary cache stays
warm after the file's initial write. Summary/base costs cancel in comparisons.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import sympy as sp


def expected_file_cost(m: int, a: float, d: int, pw: float, pr: float, k1: float) -> float:
    """Price a Bernoulli first-use file including later carries and terminal compact.

    A file is required independently with probability a before each of m
    ordinary calls. First exposure is cache-written once; later ordinary calls
    cache-read it. Terminal compaction adds k1 per resident token. Its
    contribution is an analytical cycle control, not an unnecessary reset
    appended to a finite task invoice. No recovery-model extra calls here.
    """
    u = 1 - (1 - a) ** m
    return d * ((pw + k1) * u + pr * (m - u / a))


def probe(seed: int = 20261006, replicates: int = 200_000) -> dict[str, object]:
    """Compare exact costs with Monte Carlo and expose endogenous stopping bias."""
    rng = np.random.default_rng(seed)
    a, d, pw, pr, k1 = 0.08, 12_000, 3.75e-6, 0.30e-6, 0.30e-6
    uses = rng.random((replicates, 80)) < a
    rows = []
    for m in (5, 10, 20, 40, 80):
        seen = uses[:, :m].any(axis=1)
        first = uses[:, :m].argmax(axis=1) + 1
        carries = np.where(seen, m - first, 0)
        costs = d * ((pw + k1) * seen + pr * carries)
        eager = d * (pw + k1 + pr * (m - 1))
        mean, se = float(costs.mean()), float(costs.std(ddof=1) / np.sqrt(replicates))
        rows.append({
            "ordinary_calls_in_cycle": m,
            "probability_required_before_reset": 1 - (1 - a) ** m,
            "expected_lazy_file_cost_usd": expected_file_cost(m, a, d, pw, pr, k1),
            "mc_lazy_mean_usd": mean, "mc_standard_error_usd": se,
            "eager_file_cost_usd": eager,
            "mean_subsequent_file_carries": float(carries.mean()),
        })
    # s=0,h=2,g=1,d=1: first-use input itself changes the crossed-call count.
    # A use on call 1 crosses immediately; otherwise a second call is executed.
    p = 0.5
    actual_use = p + (1 - p) * p
    mean_t = p + 2 * (1 - p)
    independent_pgf_prediction = 1 - (p * (1 - p) + (1 - p) * (1 - p) ** 2)
    return {
        "scope": "synthetic_mechanism_probe_not_empirical_recovery_fit",
        "parameters": {
            "first_use_hazard": a, "file_tokens": d,
            "write_usd_per_token": pw, "read_usd_per_token": pr,
            "terminal_compactor_marginal_usd_per_token": k1,
            "replicates": replicates, "seed": seed,
        },
        "fixed_cycle_results": rows,
        "endogenous_threshold_counterexample": {
            "parameters": {"reset_tokens": 0, "threshold": 2, "ordinary_growth": 1,
                           "file_tokens": 1, "required_use_probability": p},
            "actual_probability_used_before_crossing": actual_use,
            "incorrect_independent_T_prediction": independent_pgf_prediction,
            "mean_crossed_call_count": mean_t,
            "actual_subsequent_file_carries": 0,
            "compensator_carry_identity": mean_t - actual_use / p,
        },
        "symbolic_fixed_duration_rate": symbolic_rate(),
    }


def symbolic_rate() -> dict[str, str]:
    """Verify a continuous-duration relaxation, never call it a token-h gradient.

    Per-call constants are dropped because their derivative is zero. K is
    fixed cycle setup cost; g is independent ordinary non-file growth scale.
    The sign-changing beta term explains why first-use timing matters beyond
    substituting one larger constant reload size into a square-root rule.
    """
    m, a = sp.symbols("m a", positive=True)
    d, pw, pr, k1, g, setup = sp.symbols("d p_w p_r k_1 g K", positive=True)
    u = 1 - sp.exp(m * sp.log(1 - a))
    beta = d * (pw + k1 - pr / a)
    q = pr * d * m + beta * u
    rate = pr * g * (m - 1) / 2 + setup / m + q / m
    claimed = pr * g / 2 - setup / m**2 + beta * (m * sp.diff(u, m) - u) / m**2
    assert sp.simplify(sp.diff(rate, m) - claimed) == 0
    return {
        "domain": "m>0 continuous relaxation; 0<a<1; fixed exogenous duration",
        "u": sp.sstr(u), "beta": sp.sstr(beta),
        "rate": sp.sstr(rate), "verified_derivative_wrt_m": sp.sstr(claimed),
        "not_claimed": "token-threshold derivative when restoration alters crossing time",
    }


def main() -> None:
    """Persist inspectable synthetic output in the root cache."""
    destination = Path(".cache/experiments/first-use-reload/probe.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    report = probe()
    destination.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
