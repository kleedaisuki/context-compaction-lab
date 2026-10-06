"""Price-vector and mechanism sensitivities of a fixed renewal growth law.

Symbolic directions are conditional on the declared cache and reset contract,
not universal recommendations. The growth law is price-independent. Prices
are positive, 0<=q,theta<=1, S>=B+C, and all token counts are nonnegative.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class SensitivitySymbols:
    """Immutable identifiers for four disjoint prices and mechanism parameters.

    Attributes:
        prices: Uncached-input, cache-write, cache-read and generated-output rates.
        hit: q, the declared homogeneous cache-hit probability independent of growth.
        reset: S, the whole reconstructed context including stable base and summary.
        stable: B, an eligible unchanged warm prefix within S.
        summary: C, generated compaction summary tokens already included in S.
        instruction: K, the uncached input instruction to each compactor.
        tail_fraction: theta, retained post-call fraction of growth, not billed output fraction.
        growth_mean: g, mean total retained ordinary growth, counted exactly once.
    """

    prices: tuple[sp.Symbol, sp.Symbol, sp.Symbol, sp.Symbol]
    hit: sp.Symbol
    reset: sp.Symbol
    stable: sp.Symbol
    summary: sp.Symbol
    instruction: sp.Symbol
    tail_fraction: sp.Symbol
    growth_mean: sp.Symbol

    @classmethod
    def canonical(cls) -> SensitivitySymbols:
        """Create symbols with explicit positivity; q/theta upper bounds remain assumptions."""
        prices = sp.symbols("p_i p_w p_r p_o", positive=True)
        q, b, summary, instruction, theta = sp.symbols("q B C K theta", nonnegative=True)
        reset, growth = sp.symbols("S g", positive=True)
        return cls(prices, q, reset, b, summary, instruction, theta, growth)

    @property
    def carry(self) -> sp.Expr:
        """Expected history-carry price under independent cache hits."""
        _, write, read, _ = self.prices
        return (1 - self.hit) * write + self.hit * read

    @property
    def crossing(self) -> sp.Expr:
        """Expected old-context compactor price, excluding the terminal cold-tail correction."""
        uncached, _, read, _ = self.prices
        return (1 - self.hit) * uncached + self.hit * read

    @property
    def fee(self) -> sp.Expr:
        """Return A, exposing its nonnegative linear price coefficients."""
        uncached, write, read, output = self.prices
        q, s = self.hit, self.reset
        return (
            uncached * (self.instruction + (1 - q) * s)
            + output * self.summary
            + q * write * (s - self.stable)
            + q * read * self.stable
        )

    @property
    def tail_coefficient(self) -> sp.Expr:
        """Net compactor-versus-cache-write price of the terminal retained tail."""
        uncached, write, _, _ = self.prices
        return self.hit * (uncached - write)

    @property
    def ratio(self) -> sp.Expr:
        """Return R=A/c, whose change selects a larger or smaller core optimum gap."""
        return self.fee / self.carry


def core_sensitivities(model: SensitivitySymbols | None = None) -> dict[str, object]:
    """Derive exact price signs and parameter-path changes of H=S+D^{-1}(A/c)."""
    m = model or SensitivitySymbols.canonical()
    pi, pw, pr, po = m.prices
    q, s, b, c_summary, instruction = m.hit, m.reset, m.stable, m.summary, m.instruction
    carry, ratio = m.carry, m.ratio
    fee_only = pi * instruction + po * c_summary
    numerators = {
        pi: carry * (instruction + (1 - q) * s),
        po: carry * c_summary,
        pw: q * pr * (q * s - b) - (1 - q) * (pi * (instruction + (1 - q) * s) + po * c_summary),
        pr: q * (pw * (b - q * s) - pi * (instruction + (1 - q) * s) - po * c_summary),
        q: (pw - pr) * (pw * (s - b) + fee_only) + pr * s * (pw - pi),
        s: carry * ((1 - q) * pi + q * pw),
        b: -carry * q * (pw - pr),
        c_summary: carry * po,
        instruction: carry * pi,
    }
    for symbol, numerator in numerators.items():
        assert sp.cancel(carry**2 * sp.diff(ratio, symbol) - numerator) == 0
    assert sp.diff(numerators[pw], pw) == 0 and sp.diff(numerators[pr], pr) == 0
    duration, density = sp.symbols("U_star u_star", positive=True)
    gradient = {
        symbol: sp.factor(sp.diff(ratio, symbol)) / duration + (1 if symbol == s else 0)
        for symbol in numerators
    }
    assert sp.cancel(sum(price * gradient[price] for price in m.prices)) == 0
    mixed = {
        (left, right): sp.factor(sp.diff(ratio, left, right)) / duration
        - density * sp.diff(ratio, left) * sp.diff(ratio, right) / duration**3
        for left, right in ((pi, po), (pi, q), (po, q), (s, q), (b, q), (c_summary, s))
    }
    numerator_w_a = s * (pr - pi)
    numerator_w_b = 2 * pi * s + fee_only - pr * b
    numerator_w_e = pi * s + fee_only
    crossover_w = (
        2
        * numerator_w_e
        / (numerator_w_b + sp.sqrt(numerator_w_b**2 + 4 * numerator_w_a * numerator_w_e))
    )
    assert sp.simplify(numerators[pw].subs(q, crossover_w)) == 0
    crossover_r = (pw * b - pi * (instruction + s) - po * c_summary) / (s * (pw - pi))
    assert sp.cancel(numerators[pr].subs(q, crossover_r)) == 0
    mixed_ratio_checks = {
        (pi, q): (instruction * (pw - pr) - s * pr) / carry**2,
        (po, q): c_summary * (pw - pr) / carry**2,
        (s, q): (pw**2 - pi * pr) / carry**2,
        (b, q): -pw * (pw - pr) / carry**2,
    }
    for variables, expression in mixed_ratio_checks.items():
        assert sp.cancel(sp.diff(ratio, *variables) - expression) == 0
    return {
        "carry": carry,
        "crossing": m.crossing,
        "fee": m.fee,
        "original_fee_equivalence": pi * instruction
        + po * c_summary
        + q * (pw - pr) * (s - b)
        + m.crossing * s,
        "ratio": ratio,
        "ratio_gradient": {symbol: sp.factor(sp.diff(ratio, symbol)) for symbol in numerators},
        "sign_numerators": numerators,
        "threshold_gradient": gradient,
        "threshold_mixed_derivatives": mixed,
        "ratio_mixed_i_q": (instruction * (pw - pr) - s * pr) / carry**2,
        "ratio_mixed_o_q": c_summary * (pw - pr) / carry**2,
        "ratio_mixed_S_q": (pw**2 - pi * pr) / carry**2,
        "ratio_mixed_B_q": -pw * (pw - pr) / carry**2,
        "write_hit_crossover": crossover_w,
        "read_hit_crossover": crossover_r,
        "fixed_total_survival_B_direction": gradient[b],
        "adding_stable_B_direction": sp.simplify(gradient[b] + gradient[s]),
        "summary_added_to_reset_direction": sp.simplify(gradient[c_summary] + gradient[s]),
    }


def marked_sensitivities(model: SensitivitySymbols | None = None) -> dict[str, object]:
    """Derive implicit marked-tail directions at a nondegenerate strict stationary minimum.

    W includes theta: W=theta*(zeta-U*zeta'/u), where zeta=E[G_T]. General laws
    require f_L=cU-dW'>0 at the selected branch; exponential W is explicit.
    """
    m = model or SensitivitySymbols.canonical()
    core = core_sensitivities(m)
    pi, pw, pr, _ = m.prices
    w, w_prime, d_value, duration = sp.symbols("W W_prime D U_star", real=True)
    denominator = m.carry * duration - m.tail_coefficient * w_prime
    on_root = {}
    raw_gradient = {}
    for symbol in (*m.prices, m.hit, m.reset, m.stable, m.summary, m.instruction):
        numerator = (
            sp.diff(m.fee, symbol)
            + sp.diff(m.tail_coefficient, symbol) * w
            - sp.diff(m.carry, symbol) * d_value
        )
        raw_gradient[symbol] = numerator / denominator + (1 if symbol == m.reset else 0)
        on_root[symbol] = sp.cancel(
            m.carry * numerator.subs(d_value, (m.fee + m.tail_coefficient * w) / m.carry)
        )
    explicit = {
        pw: core["sign_numerators"][pw] - m.hit * m.crossing * w,
        pr: core["sign_numerators"][pr] - m.hit * m.tail_coefficient * w,
        m.hit: core["sign_numerators"][m.hit] + pw * (pi - pw) * w,
    }
    for symbol, numerator in explicit.items():
        assert sp.cancel(on_root[symbol] - numerator) == 0
    radial = sum(price * (raw_gradient[price]) for price in m.prices)
    assert sp.cancel(radial.subs(d_value, (m.fee + m.tail_coefficient * w) / m.carry)) == 0
    gap = sp.Symbol("L", positive=True)
    g, theta = m.growth_mean, m.tail_fraction
    exponential_w = theta * (2 * g - (2 * g + gap) * sp.exp(-gap / g))
    exponential_denominator = (1 + gap / g) * (
        m.carry - m.tail_coefficient * theta * sp.exp(-gap / g)
    )
    assert (
        sp.simplify(
            denominator.subs({duration: 1 + gap / g, w_prime: sp.diff(exponential_w, gap)})
            - exponential_denominator
        )
        == 0
    )
    return {
        "stationary_equation": m.carry * d_value - m.fee - m.tail_coefficient * w,
        "denominator": denominator,
        "implicit_threshold_gradient": raw_gradient,
        "on_root_numerators": on_root,
        "explicit_regime_numerators": explicit,
        "W_includes_theta": exponential_w,
        "exponential_denominator": exponential_denominator,
        "warm_write_regime_numerator": sp.factor(explicit[pw].subs(m.hit, 1)),
        "warm_read_regime_numerator": sp.factor(explicit[pr].subs(m.hit, 1)),
        "theta_direction": m.tail_coefficient * (exponential_w / theta) / exponential_denominator,
    }


def billed_rate_basis(model: SensitivitySymbols | None = None) -> dict[str, object]:
    """Derive the four physical token-rate coefficients with consistent pre/post timing."""
    m = model or SensitivitySymbols.canonical()
    pi, pw, pr, po = m.prices
    duration, area, terminal = sp.symbols("U M zeta", positive=True)
    ordinary_input, billed_output = sp.symbols("I E_O", nonnegative=True)
    q, theta, g = m.hit, m.tail_fraction, m.growth_mean
    basis = (
        ordinary_input
        + (1 - q) * g
        + (m.instruction + (1 - q) * m.reset + q * theta * terminal) / duration,
        (1 - (1 - q) * theta) * g
        + (1 - q) * m.reset
        + (q * (m.reset - m.stable) + (1 - q) * area - q * theta * terminal) / duration,
        q * ((1 - theta) * g + m.reset + (m.stable + area) / duration),
        billed_output + m.summary / duration,
    )
    baseline = pi * ordinary_input + po * billed_output + pw * g - m.carry * theta * g
    rate = (
        baseline
        + m.carry * m.reset
        + m.crossing * g
        + (m.fee + m.carry * area + m.tail_coefficient * theta * terminal) / duration
    )
    paired = sum(price * coefficient for price, coefficient in zip(m.prices, basis))
    assert sp.cancel(rate - paired) == 0
    for price, coefficient in zip(m.prices, basis):
        assert (
            sp.diff(rate, price) == sp.expand(coefficient)
            or sp.cancel(sp.diff(rate, price) - coefficient) == 0
        )
    assert sp.hessian(rate, m.prices) == sp.zeros(4)
    write_nonnegative = (1 - q) * ((1 - theta) * g + m.reset + area / duration) + q * (
        g + (m.reset - m.stable - theta * terminal) / duration
    )
    assert sp.cancel(basis[1] - write_nonnegative) == 0
    compactor_prefix = g + (m.reset - theta * terminal) / duration
    ordinary_prefix = (
        m.reset - theta * g + (area + theta * terminal - (m.reset - m.stable)) / duration
    )
    cache_gain = (pi - pr) * compactor_prefix + (pw - pr) * ordinary_prefix
    assert sp.cancel(-sp.diff(rate, q) - cache_gain) == 0
    curvature = sp.Symbol("j_LL", positive=True)
    price_gap_gradient = sp.Matrix(sp.symbols("j_L_i j_L_w j_L_r j_L_o", real=True))
    envelope_hessian = -price_gap_gradient * price_gap_gradient.T / curvature
    return {
        "basis": basis,
        "full_rate": rate,
        "consistent_baseline": baseline,
        "write_nonnegative_decomposition": write_nonnegative,
        "nonnegative_condition": "0<=q,theta<=1; S>=B+C; 0<=zeta<=gU; M>=0",
        "cache_gain": cache_gain,
        "compactor_matching_prefix_rate": compactor_prefix,
        "ordinary_matching_prefix_rate": ordinary_prefix,
        "prefix_nonnegative_extra_condition": "U>=1; M>=gU-zeta>=0",
        "price_hessian_fixed_gap": sp.hessian(rate, m.prices),
        "optimized_price_hessian": envelope_hessian,
        "optimized_hessian_condition": "unique smooth interior optimum, j_LL>0, fixed law",
    }
