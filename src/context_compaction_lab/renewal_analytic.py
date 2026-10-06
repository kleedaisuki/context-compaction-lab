"""Closed renewal laws for analytic compaction economics, without Monte Carlo.

These are iid regenerative models with idealized homogeneous cache prices,
not a claim that a full versioned working-set simulator regenerates. Ordinary
growth includes every retained addition; output must not be added twice.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

import numpy as np
from scipy.optimize import brentq
from scipy.stats import poisson

from .config import Pricing


def _finite(value: float, name: str, *, minimum: float | None = None) -> None:
    """Validate scalar physical rates and moments without silently clipping inputs."""
    if (
        isinstance(value, bool)
        or not math.isfinite(value)
        or (minimum is not None and value < minimum)
    ):
        suffix = f" and >= {minimum}." if minimum is not None else "."
        raise ValueError(f"{name} must be finite" + suffix)


@dataclass(frozen=True)
class RenewalMoments:
    """First three raw moments of one nonnegative ordinary-growth increment."""

    mean: float
    second: float
    third: float

    def __post_init__(self) -> None:
        """Require finite positive mean and necessary nonnegative moment inequalities."""
        for name in ("mean", "second", "third"):
            _finite(getattr(self, name), name, minimum=0)
        if self.mean <= 0 or self.second < self.mean**2 * (1 - 1e-12):
            raise ValueError("Positive mean and second >= mean squared are required.")
        if self.third < self.second**2 / self.mean * (1 - 1e-12):
            raise ValueError("Third moment must satisfy third*mean >= second squared.")

    @property
    def cv_squared(self) -> float:
        """Return population increment variance divided by squared mean."""
        return self.second / self.mean**2 - 1

    @property
    def renewal_intercept(self) -> float:
        """Return a=E[G²]/(2E[G]²), including the initial renewal at zero."""
        return self.second / (2 * self.mean**2)

    @property
    def integrated_constant(self) -> float:
        """Return C0 in D(L)=L²/(2g)+aL+C0+o(1), for a nonarithmetic law."""
        return self.second**2 / (4 * self.mean**3) - self.third / (6 * self.mean**2)


@dataclass(frozen=True)
class RenewalStatistics:
    """Exact-law numeric values of U,D and the mean terminal crossing increment.

    Zero gap means a right limit; physical cycle evaluation requires L>0.
    Derivatives refer to continuous growth laws, not lattice interpolation.
    """

    duration: float
    integrated_duration: float
    duration_derivative: float
    terminal_increment: float
    terminal_derivative: float


class RenewalLaw(Protocol):
    """Analytic renewal law interface; evaluations are deterministic, not sampled."""

    @property
    def moments(self) -> RenewalMoments:
        """Return raw moments of one increment, including any zero mass."""
        ...

    def statistics(self, gap: float) -> RenewalStatistics:
        """Evaluate U(L), D(L), their needed derivatives and E[G_T]."""
        ...


@dataclass(frozen=True)
class ErlangRenewal:
    """IID Erlang-k positive growth with optional zero increments.

    mean_growth is the unconditional mean including zeros. The positive law's
    mean is mean_growth/(1-p0). Shape 1 recovers exponential growth. Evaluation
    uses a finite roots-of-unity sum, with O(shape) arithmetic.
    """

    mean_growth: float
    shape: int = 1
    zero_probability: float = 0.0

    def __post_init__(self) -> None:
        """Validate positive mean, phase count and a proper nondegenerate zero mass."""
        _finite(self.mean_growth, "mean_growth", minimum=0)
        _finite(self.zero_probability, "zero_probability", minimum=0)
        if (
            self.mean_growth <= 0
            or type(self.shape) is not int
            or self.shape < 1
            or self.zero_probability >= 1
        ):
            raise ValueError("Require mean>0, positive integer shape, and 0<=p0<1.")

    @property
    def positive_mean(self) -> float:
        """Return the conditional mean given strictly positive growth."""
        return self.mean_growth / (1 - self.zero_probability)

    @property
    def moments(self) -> RenewalMoments:
        """Return unconditional raw moments; zeros do not disappear from cycle duration."""
        q, g, k = 1 - self.zero_probability, self.positive_mean, self.shape
        return RenewalMoments(q * g, q * g**2 * (1 + 1 / k), q * g**3 * (1 + 1 / k) * (1 + 2 / k))

    def statistics(self, gap: float) -> RenewalStatistics:
        """Evaluate exact Erlang phase sums and analytic terminal-mark moments."""
        _finite(gap, "gap", minimum=0)
        g, k, q = self.positive_mean, self.shape, 1 - self.zero_probability
        x = gap / g
        omega = np.exp(2j * np.pi * np.arange(1, k) / k)
        rates = k * (omega - 1)
        weights = omega / (k * (omega - 1))
        changes = np.expm1(rates * x)
        duration = (1 + x + float(np.real(np.sum(weights * changes)))) / q
        integrated = (
            g * (x + x**2 / 2 + float(np.real(np.sum(weights * (changes / rates - x))))) / q
        )
        density = (1 + float(np.real(np.sum(omega * np.exp(rates * x))))) / (g * q)
        if k > 1 and k * x < 0.25:
            # The equivalent positive Poisson phase probability avoids cancellation at zero.
            phase_mean = k * x
            cutoff = max(k - 1, int(poisson.ppf(1 - 1e-14, phase_mean)))
            phases = np.arange(k - 1, cutoff + 1, k)
            density = (k / (g * q)) * float(poisson.pmf(phases, phase_mean).sum())
        terminal = g * (1 + 1 / k) + (g / k) * float(np.real(np.exp(rates * x).sum()))
        terminal -= g * math.exp(-k * x)
        terminal_derivative = float(np.real((rates * np.exp(rates * x)).sum())) / k + k * math.exp(
            -k * x
        )
        return RenewalStatistics(duration, integrated, density, terminal, terminal_derivative)


@dataclass(frozen=True)
class HyperexponentialRenewal:
    """IID two-exponential mixture, allowing high-CV bursty positive growth.

    This is a mechanistic two-scale law, not a fit or a replacement for observed
    dependence. rate_fast and rate_slow are inverse token lengths, not time.
    """

    weight_fast: float
    rate_fast: float
    rate_slow: float
    zero_probability: float = 0.0

    def __post_init__(self) -> None:
        """Reject invalid mixture weights, rates or an all-zero increment law."""
        for name in ("weight_fast", "rate_fast", "rate_slow", "zero_probability"):
            _finite(getattr(self, name), name, minimum=0)
        if (
            self.weight_fast > 1
            or self.rate_fast <= 0
            or self.rate_slow <= 0
            or self.zero_probability >= 1
        ):
            raise ValueError("Require weights in [0,1], rates>0, and 0<=p0<1.")

    @classmethod
    def from_mean_cv(cls, mean: float, cv: float) -> HyperexponentialRenewal:
        """Construct a balanced-means two-phase law with prescribed mean and CV>=1."""
        _finite(mean, "mean", minimum=0)
        _finite(cv, "cv", minimum=1)
        if mean <= 0:
            raise ValueError("A positive growth mean is required.")
        p = (1 + math.sqrt((cv**2 - 1) / (cv**2 + 1))) / 2
        return cls(p, 2 * p / mean, 2 * (1 - p) / mean)

    @property
    def positive_mean(self) -> float:
        """Return the positive component's mean, which excludes zero-action waiting."""
        return self.weight_fast / self.rate_fast + (1 - self.weight_fast) / self.rate_slow

    @property
    def moments(self) -> RenewalMoments:
        """Return exact-law mixture moments evaluated numerically."""
        p, q = self.weight_fast, 1 - self.zero_probability
        values = [
            q
            * math.factorial(order)
            * (p / self.rate_fast**order + (1 - p) / self.rate_slow**order)
            for order in (1, 2, 3)
        ]
        return RenewalMoments(*values)

    def statistics(self, gap: float) -> RenewalStatistics:
        """Evaluate the one-decaying-mode closed form and terminal increment correction."""
        _finite(gap, "gap", minimum=0)
        p, q = self.weight_fast, 1 - self.zero_probability
        g = self.positive_mean
        rate = (1 - p) * self.rate_fast + p * self.rate_slow
        second = 2 * (p / self.rate_fast**2 + (1 - p) / self.rate_slow**2)
        a = second / (2 * g**2)
        change = -math.expm1(-rate * gap)
        duration = (1 + gap / g + (a - 1) * change) / q
        integrated = (gap**2 / (2 * g) + gap + (a - 1) * (gap - change / rate)) / q
        density = (1 / g + (a - 1) * rate * math.exp(-rate * gap)) / q
        coefficient = g - second / g + 1 / self.rate_fast + 1 / self.rate_slow
        terminal = (
            second / g
            + coefficient * math.exp(-rate * gap)
            - math.exp(-self.rate_fast * gap) / self.rate_fast
            - math.exp(-self.rate_slow * gap) / self.rate_slow
        )
        terminal_derivative = (
            -coefficient * rate * math.exp(-rate * gap)
            + math.exp(-self.rate_fast * gap)
            + math.exp(-self.rate_slow * gap)
        )
        return RenewalStatistics(duration, integrated, density, terminal, terminal_derivative)


@dataclass(frozen=True)
class RenewalFees:
    """Collapsed four-price ledger coefficients with declared regenerative assumptions.

    fixed_cost is the per-cycle surcharge F, including cold reset rewrites but
    excluding crossing_price*S. ordinary_baseline excludes crossing_price*g,
    which rate() adds explicitly. terminal_coefficient multiplies E[Z_T].
    """

    reset_tokens: float
    fixed_cost: float
    carry_price: float
    crossing_price: float
    ordinary_baseline: float = 0.0
    terminal_coefficient: float = 0.0

    def __post_init__(self) -> None:
        """Validate units; fixed_cost may be a net price correction of either sign."""
        for name in ("reset_tokens", "carry_price", "crossing_price", "ordinary_baseline"):
            _finite(getattr(self, name), name, minimum=0)
        _finite(self.fixed_cost, "fixed_cost")
        _finite(self.terminal_coefficient, "terminal_coefficient")
        if self.carry_price <= 0:
            raise ValueError("Interior renewal optimization requires carry_price>0.")

    @property
    def numerator_fee(self) -> float:
        """Return A=F+kappa*S, the threshold-changing one-cycle fee."""
        return self.fixed_cost + self.crossing_price * self.reset_tokens


def physical_cache_fees(
    pricing: Pricing,
    *,
    reset_tokens: float,
    surviving_base: float,
    summary_tokens: float,
    mean_growth: float,
    mean_output: float,
    hit_probability: float = 1,
    normal_uncached: float = 128,
    compaction_instruction: float = 128,
) -> RenewalFees:
    """Derive c,kappa,F,b and the uncached terminal-output correction from four prices.

    Cache hit marks are iid and independent of growth/output; base survival is
    eligible on a hit and no compaction delay expires it. Summary is already
    inside S. This helper places all ordinary growth in the post-call retained
    tail. Billed output is a separate nonnegative mark and need not equal, or
    be bounded by, retained growth. Tool payload is not billed model output.
    This does not model TTL coupling or arbitrary missing-prefix dependence.
    Changing rate()'s terminal_fraction changes the crossing correction only;
    it does not reclassify the pre/post timing baseline constructed here.
    """
    for name, value in (
        ("reset_tokens", reset_tokens),
        ("surviving_base", surviving_base),
        ("summary_tokens", summary_tokens),
        ("mean_growth", mean_growth),
        ("mean_output", mean_output),
        ("hit_probability", hit_probability),
        ("normal_uncached", normal_uncached),
        ("compaction_instruction", compaction_instruction),
    ):
        _finite(value, name, minimum=0)
    if surviving_base + summary_tokens > reset_tokens or hit_probability > 1 or mean_growth <= 0:
        raise ValueError("Require B+C<=S, g>0, nonnegative output, and q in [0,1].")
    q, p = hit_probability, pricing
    carry = p.write - q * (p.write - p.read)
    crossing = p.input - q * (p.input - p.read)
    fixed = p.input * compaction_instruction + p.output * summary_tokens
    fixed += (p.write - carry) * (reset_tokens - surviving_base)
    baseline = (p.write - carry) * mean_growth + p.input * normal_uncached + p.output * mean_output
    return RenewalFees(reset_tokens, fixed, carry, crossing, baseline, q * (p.input - p.write))


def rate(law: RenewalLaw, fees: RenewalFees, gap: float, *, terminal_fraction: float = 0) -> float:
    """Evaluate the exact renewal ratio for the specified law and ledger reduction."""
    _finite(terminal_fraction, "terminal_fraction", minimum=0)
    if gap <= 0 or terminal_fraction > 1:
        raise ValueError("Physical cycles require L>0 and 0<=terminal_fraction<=1.")
    stats = law.statistics(gap)
    occupation = gap * stats.duration - stats.integrated_duration
    numerator = (
        fees.numerator_fee
        + fees.carry_price * occupation
        + fees.terminal_coefficient * terminal_fraction * stats.terminal_increment
    )
    return (
        fees.ordinary_baseline
        + fees.carry_price * fees.reset_tokens
        + fees.crossing_price * law.moments.mean
        + numerator / stats.duration
    )


def optimal_gap(
    law: RenewalLaw,
    fees: RenewalFees,
    *,
    terminal_fraction: float = 0,
) -> float:
    """Solve D=A/c, or the proven exponential proportional-tail correction.

    Nonzero tail corrections for general phase laws require separate global
    analysis; they are deliberately not labeled universally unimodal here.
    """
    _finite(terminal_fraction, "terminal_fraction", minimum=0)
    if terminal_fraction > 1 or fees.numerator_fee <= 0:
        raise ValueError("Require 0<=terminal_fraction<=1 and A>0 for an interior solution.")
    correction = fees.terminal_coefficient * terminal_fraction
    if correction and not (isinstance(law, ErlangRenewal) and law.shape == 1):
        raise ValueError("Corrected uniqueness is only asserted for exponential growth.")

    def equation(gap: float) -> float:
        """Evaluate the monotone core, with the explicitly proved exponential correction."""
        stats = law.statistics(gap)
        residual = fees.carry_price * stats.integrated_duration - fees.numerator_fee
        if correction:
            positive_mean = law.positive_mean
            terminal_balance = 2 * positive_mean - (2 * positive_mean + gap) * math.exp(
                -gap / positive_mean
            )
            residual -= correction * terminal_balance
        return residual

    upper = max(
        law.moments.mean, math.sqrt(2 * law.moments.mean * fees.numerator_fee / fees.carry_price)
    )
    for _ in range(128):
        if equation(upper) > 0:
            return float(brentq(equation, 0, upper, xtol=1e-10, rtol=1e-12))
        upper *= 2
    raise ValueError("A finite optimum bracket was not obtained.")


def rate_derivative(
    law: RenewalLaw,
    fees: RenewalFees,
    gap: float,
    *,
    terminal_fraction: float = 0,
) -> float:
    """Differentiate a continuous-law rate, including the exact terminal-mark correction."""
    _finite(terminal_fraction, "terminal_fraction", minimum=0)
    if gap <= 0 or terminal_fraction > 1:
        raise ValueError("Physical cycles require L>0 and 0<=terminal_fraction<=1.")
    stats = law.statistics(gap)
    numerator = stats.duration_derivative * (
        fees.carry_price * stats.integrated_duration - fees.numerator_fee
    )
    numerator += (
        fees.terminal_coefficient
        * terminal_fraction
        * (
            stats.terminal_derivative * stats.duration
            - stats.terminal_increment * stats.duration_derivative
        )
    )
    return numerator / stats.duration**2


def asymptotic_optimal_gap(
    moments: RenewalMoments,
    fee_ratio: float,
    *,
    lattice_span: float | None = None,
) -> float:
    """Invert a moment expansion with an optional arithmetic span/phase correction.

    The default preserves the nonarithmetic quadratic approximation. For a
    finite-support law on span d, the grid constant is C0-d²/(12g), and the
    between-grid term is d²*r*(1-r)/(2g). Including that term makes the inverse
    linear within each cell. This remains a large-gap approximation except
    when remaining pole terms vanish, as for constant growth d.
    """
    _finite(fee_ratio, "fee_ratio", minimum=0)
    g, a, constant = moments.mean, moments.renewal_intercept, moments.integrated_constant
    if lattice_span is not None:
        _finite(lattice_span, "lattice_span", minimum=0)
        if lattice_span <= 0:
            raise ValueError("The actual arithmetic span must be strictly positive.")
        constant -= lattice_span**2 / (12 * g)
    discriminant = a**2 * g**2 + 2 * g * (fee_ratio - constant)
    if discriminant < 0:
        raise ValueError("The large-gap quadratic approximation has no real root.")
    approximation = -a * g + math.sqrt(discriminant)
    if approximation <= 0:
        raise ValueError("The large-gap approximation is outside its positive-gap regime.")
    if lattice_span is not None:
        lower = math.floor(approximation / lattice_span) * lattice_span
        grid_value = lower**2 / (2 * g) + a * lower + constant
        slope = lower / g + a + lattice_span / (2 * g)
        approximation = lower + (fee_ratio - grid_value) / slope
    return approximation


def random_reset_exponential_optimum(
    mean_growth: float,
    mean_reset: float,
    reset_variance: float,
    mean_fee: float,
    carry_price: float,
    reset_upper_bound: float,
) -> float:
    """Solve E[D(H-S)]=E[A]/c for bounded independent reset S under exponential growth.

    mean_fee is E[F+kappa*S], not F evaluated at the mean if F is nonlinear.
    The result is accepted only in H>ess sup S, where every cycle has positive gap.
    """
    for name, value in (
        ("mean_growth", mean_growth),
        ("mean_reset", mean_reset),
        ("reset_variance", reset_variance),
        ("mean_fee", mean_fee),
        ("carry_price", carry_price),
        ("reset_upper_bound", reset_upper_bound),
    ):
        _finite(value, name, minimum=0)
    if mean_growth <= 0 or carry_price <= 0 or mean_reset > reset_upper_bound:
        raise ValueError("Require g,c>0 and a valid bounded reset mean.")
    if reset_variance > mean_reset * (reset_upper_bound - mean_reset) * (1 + 1e-12):
        raise ValueError("Reset variance violates its declared nonnegative bounded support.")
    discriminant = mean_growth**2 + 2 * mean_growth * mean_fee / carry_price - reset_variance
    if discriminant <= 0:
        raise ValueError("The random-reset stationary equation has no positive-gap root.")
    threshold = mean_reset - mean_growth + math.sqrt(discriminant)
    if threshold <= reset_upper_bound:
        raise ValueError("The analytic stationary threshold lies outside H>ess sup S.")
    return threshold
