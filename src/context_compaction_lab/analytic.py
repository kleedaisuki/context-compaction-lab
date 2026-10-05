"""An exact stochastic first-passage benchmark and symbolic derivatives.

This idealized ledger has fixed recovered length, independent exponential
growth, warm reads, and affine reset processing. It is NOT an analytic solution
to the fuller finite-horizon TTL and conditional-recovery simulator.
"""

from __future__ import annotations

import sympy as sp


def exponential_benchmark() -> dict[str, sp.Expr]:
    """Derive the expected renewal reward rate without substituting means.

    For gap d=H-S>0 and exponential growth mean g, the crossing time is
    tau=1+Poisson(d/g). The expected crossed length is H+g, not H. A cycle
    reads the pre-call history S+partial sums, and reset surcharge includes
    an affine compactor K(crossed)=k0+k1*crossed plus (p_w-p_r)*S.
    """
    h, s, g, pr, pw = sp.symbols("H S g p_r p_w", positive=True)
    k0, k1, b = sp.symbols("k_0 k_1 b", nonnegative=True)
    d = h - s
    duration = 1 + d / g
    area = s + (s * d + d**2 / 2) / g
    crossing = h + g
    reward = b * duration + pr * area + k0 + k1 * crossing + (pw - pr) * s
    rate = sp.simplify(reward / duration)
    a = k0 + (k1 + pw - pr) * s
    derivative = pr / 2 - (g * a + pr * g**2 / 2) / (d + g) ** 2
    second = (2 * g * a + pr * g**2) / (d + g) ** 3
    optimum = s - g + sp.sqrt(g**2 + 2 * g * a / pr)
    assert sp.simplify(sp.diff(rate, h) - derivative) == 0
    assert sp.simplify(sp.diff(rate, h, 2) - second) == 0
    assert sp.simplify(derivative.subs(h, optimum)) == 0
    return {
        "expected_cycle_requests": duration,
        "expected_retained_token_area": area,
        "expected_crossed_context": crossing,
        "expected_cycle_reward": reward,
        "expected_cost_rate": rate,
        "rate_derivative": derivative,
        "rate_second_derivative": second,
        "stationary_threshold": optimum,
        "deterministic_mean_substitution_threshold": s + sp.sqrt(2 * g * a / pr),
    }


def renewal_quotient_derivative() -> sp.Expr:
    """Differentiate E[cycle reward]/E[cycle length] under smoothness assumptions."""
    h = sp.symbols("H", positive=True)
    reward, duration = sp.Function("expected_reward")(h), sp.Function("expected_length")(h)
    return sp.diff(reward / duration, h)
