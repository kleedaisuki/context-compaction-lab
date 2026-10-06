"""Exact occupation-vector algebra for price-independent finite policy laws.

No stochastic transition or invoice is reimplemented here. Integer token
ledgers from ``simulate_working_set`` are lifted into exact SymPy expressions.
Price linearity requires fixed, price-independent transition and feasibility
laws; a price-adaptive policy must first be frozen before using this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import sympy as sp
from numpy.typing import NDArray

from .working_set_simulation import WorkingSetResult

ALPHA = sp.Symbol("alpha", nonnegative=True)
"""IID demand probability; callers additionally restrict it to [0, 1]."""
PRICES = sp.symbols("p_i p_w p_r p_o", nonnegative=True)
"""Four symbolic USD-per-token prices in the engine's disjoint category order."""
THRESHOLD = sp.Symbol("h", positive=True)
"""Physical token threshold, distinct from a continuous duration surrogate."""
CHANNELS = ("input_tokens", "write_tokens", "read_tokens", "output_tokens")
"""Occupation-vector ordering; file reload counts are not additional fees."""


@dataclass(frozen=True)
class OccupationVector:
    """Exact expected billed tokens in four disjoint categories.

    Entries may depend on demand parameters, but must not depend on price for
    price-linearity claims. The algebra supports symbolic differences as well
    as nonnegative occupation vectors; a difference need not be nonnegative.
    """

    entries: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]

    def __post_init__(self) -> None:
        """Canonicalize exact expressions without converting floats to rationals."""
        if len(self.entries) != 4:
            raise ValueError("Occupation vectors require exactly four categories.")
        entries = tuple(sp.expand(sp.sympify(entry)) for entry in self.entries)
        if any(entry.has(sp.Float) for entry in entries):
            raise ValueError("Use exact integers/rationals, not floating symbolic coefficients.")
        object.__setattr__(self, "entries", entries)

    def cost(self, prices: Sequence[sp.Expr] = PRICES) -> sp.Expr:
        """Pair the occupation vector with four prices, preserving exact algebra."""
        if len(prices) != 4:
            raise ValueError("Exactly four disjoint prices are required.")
        exact_prices = tuple(sp.sympify(price) for price in prices)
        if any(price.has(sp.Float) for price in exact_prices):
            raise ValueError("Symbolic prices require exact integers/rationals, not floats.")
        return sp.expand(sum(entry * price for entry, price in zip(self.entries, exact_prices)))

    def difference(self, other: OccupationVector) -> OccupationVector:
        """Return this policy minus another, the coefficients of a price hyperplane."""
        return OccupationVector(tuple(a - b for a, b in zip(self.entries, other.entries)))

    def derivative(self, symbol: sp.Symbol) -> OccupationVector:
        """Differentiate occupations, e.g. with respect to demand probability."""
        return OccupationVector(tuple(sp.diff(entry, symbol) for entry in self.entries))

    def substitute(self, replacements: dict) -> OccupationVector:
        """Evaluate parameters exactly, including rational Bernoulli probabilities."""
        return OccupationVector(tuple(entry.subs(replacements) for entry in self.entries))


def _paths_and_counts(paths: NDArray) -> tuple[int, NDArray]:
    """Require a complete, unique boolean cube before treating grouped sums as exact."""
    if paths.ndim != 2 or paths.dtype.kind != "b" or paths.shape[1] < 1:
        raise ValueError("Paths must be a nonempty two-dimensional boolean array.")
    trials = paths.shape[1]
    if len(paths) != 2**trials or len(np.unique(paths, axis=0)) != len(paths):
        raise ValueError("Enumerate every Bernoulli path exactly once.")
    return trials, paths.sum(axis=1)


def exact_integer_values(values: NDArray) -> tuple[int, ...]:
    """Reject noninteger or precision-unsafe engine totals before exact lifting.

    The current engine stores token totals as float64. Values at or above 2**53
    are refused: rounded larger integers cannot be recovered from those floats.
    This is a boundary check, not rounding or an approximate rational fit.
    """
    array = np.asarray(values)
    if array.ndim != 1 or array.dtype.kind not in "iuf":
        raise ValueError("Token totals must be a numeric one-dimensional array.")
    if (np.any(~np.isfinite(array)) or np.any(array < 0)
            or np.any(array >= 2**53) or np.any(array != np.floor(array))):
        raise ValueError("Token totals must be exact nonnegative integers below 2**53.")
    return tuple(int(value) for value in array)


def bernoulli_polynomial(
    paths: NDArray, values: NDArray, alpha: sp.Symbol = ALPHA,
) -> sp.Expr:
    """Lift arbitrary integer path rewards into a degree-at-most-N exact polynomial.

    All effects of endogenous resets and restorations are already in rewards.
    Group sums include the binomial multiplicities; no extra binomial factor
    must be introduced. This function never assumes stopping time independence.
    """
    trials, counts = _paths_and_counts(paths)
    integers = exact_integer_values(values)
    if len(integers) != len(paths):
        raise ValueError("Provide one integer reward per enumerated path.")
    grouped = [0] * (trials + 1)
    for count, value in zip(counts, integers):
        grouped[int(count)] += value
    expectation = sum(sp.Integer(total) * alpha**k * (1 - alpha)**(trials - k)
                      for k, total in enumerate(grouped))
    return sp.Poly(expectation, alpha).as_expr()


def bernoulli_occupation(
    paths: NDArray, result: WorkingSetResult, alpha: sp.Symbol = ALPHA,
) -> OccupationVector:
    """Extract a successful actual-engine ledger as four exact demand polynomials."""
    trials, _ = _paths_and_counts(paths)
    if np.any(result.loop_failures) or np.any(result.completed_actions != trials):
        raise ValueError("Incomplete or failed policy bills cannot be treated as feasible.")
    return OccupationVector(tuple(bernoulli_polynomial(paths, getattr(result, channel), alpha)
                                  for channel in CHANNELS))


def bernstein_coefficients(
    expression: sp.Expr, degree: int, alpha: sp.Symbol = ALPHA,
) -> tuple[sp.Expr, ...]:
    """Express a polynomial in the nonnegative degree-N Bernstein basis.

    If all coefficients share a strict sign, that sign is certified throughout
    [0,1]. For enumerated iid rewards each coefficient equals the conditional
    mean reward given k successes, unlike the raw grouped sums used above.
    """
    polynomial = sp.Poly(expression, alpha)
    if type(degree) is not int or degree < 0 or polynomial.degree() > degree:
        raise ValueError("The Bernstein degree must cover the polynomial degree.")
    if expression.has(sp.Float):
        raise ValueError("A sign certificate requires exact polynomial coefficients.")
    return tuple(sp.cancel(sum(polynomial.nth(j) * sp.binomial(k, j)
                               / sp.binomial(degree, j) for j in range(k + 1)))
                 for k in range(degree + 1))


@dataclass(frozen=True)
class ThresholdBand:
    """One exact physical-threshold cell (lower, upper], or an infinite final tail."""

    lower: int
    upper: int | None
    occupation: OccupationVector

    def __post_init__(self) -> None:
        """Require ordered nonnegative integer token boundaries."""
        if (type(self.lower) is not int or self.lower < 0
                or (self.upper is not None
                    and (type(self.upper) is not int or self.upper <= self.lower))):
            raise ValueError("Threshold bands require 0 <= lower < upper, or upper=None.")


@dataclass(frozen=True)
class ThresholdCurve:
    """Complete positive-threshold step law with exact demand and price dependence."""

    bands: tuple[ThresholdBand, ...]

    def __post_init__(self) -> None:
        """Require exhaustive consecutive cells and an explicit infinite final tail."""
        if not self.bands or self.bands[0].lower != 0 or self.bands[-1].upper is not None:
            raise ValueError("A complete threshold curve starts at zero and ends at infinity.")
        for left, right in zip(self.bands, self.bands[1:]):
            if left.upper != right.lower:
                raise ValueError("Threshold bands cannot have gaps or overlaps.")

    def at(self, threshold: int | sp.Rational) -> OccupationVector:
        """Select the exact cell, respecting the engine's >= trigger at the boundary."""
        if threshold <= 0:
            raise ValueError("Physical thresholds must be positive.")
        for band in self.bands:
            if band.upper is None or threshold <= band.upper:
                return band.occupation
        raise AssertionError("The infinite tail must cover every positive threshold.")

    def piecewise_cost(
        self, threshold: sp.Symbol = THRESHOLD, prices: Sequence[sp.Expr] = PRICES,
    ) -> sp.Expr:
        """Return a right-closed Piecewise price expression for all h > 0."""
        return sp.Piecewise(*(
            (band.occupation.cost(prices),
             True if band.upper is None else threshold <= band.upper)
            for band in self.bands
        ))

    def distributional_derivative(
        self, threshold: sp.Symbol = THRESHOLD, prices: Sequence[sp.Expr] = PRICES,
    ) -> sp.Expr:
        """Return jump masses, not the zero almost-everywhere classical derivative."""
        return sp.Add(*(
            right.occupation.difference(left.occupation).cost(prices)
            * sp.DiracDelta(threshold - left.upper)
            for left, right in zip(self.bands, self.bands[1:])
        ))


def read_write_crossover(
    delta: OccupationVector, input_write_ratio: sp.Expr, output_write_ratio: sp.Expr,
) -> sp.Expr:
    """Solve a comparison hyperplane for p_r/p_w, assuming p_w>0 and delta_R!=0.

    This root is an algebraic boundary, not an optimality claim. Its inequality
    orientation depends on the sign of the read-occupation difference, and only
    nonnegative price ratios are economically admissible.
    """
    uncached, write, read, output = delta.entries
    if read == 0:
        raise ValueError("A nonzero read difference is required for a unique crossover.")
    return sp.cancel(-(uncached * input_write_ratio + write
                       + output * output_write_ratio) / read)
