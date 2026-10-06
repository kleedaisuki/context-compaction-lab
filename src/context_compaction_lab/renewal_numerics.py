"""Deterministic empirical-renewal evaluation and four-price finite simulation.

The analytic optimum comes from renewal lag, not a fitted positive distribution.
Empirical increments are binned with declared quantum for convolution. Ordinary
outputs are invoice marks and are never inserted into growth a second time.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import fftconvolve

from .config import Pricing


@dataclass(frozen=True)
class RenewalLedger:
    """Concentrated reset and explicit cache/timing interventions.

    ``reset`` includes ``stable_base`` and ``summary``. ``tail_fraction`` is an
    unidentified split of aggregate growth, not an inference from billed output.
    Cache marks are independent Bernoulli hits; no expiry delay is added after
    compaction. Cache eligibility is assumed throughout. No recovery model
    request is hidden in this primary protocol. Initial reset context is warm.
    """

    reset: float = 65_588
    summary: float = 4_382
    stable_base: float = 20_000
    cache_hit: float = 1.0
    tail_fraction: float = 1.0
    compaction_instruction: float = 128
    ordinary_suffix: float = 128
    prices: Pricing = Pricing()

    def __post_init__(self) -> None:
        """Reject overlapping reset decomposition and impossible probabilities."""
        if not 0 <= self.stable_base <= self.reset or not 0 <= self.summary <= (
            self.reset - self.stable_base
        ):
            raise ValueError("Stable base and generated summary must fit INSIDE reset context.")
        if not 0 <= self.cache_hit <= 1 or not 0 <= self.tail_fraction <= 1:
            raise ValueError("Hit probability and tail fraction must be in [0,1].")
        if (
            any(
                not np.isfinite(x) or x < 0
                for x in (
                    self.reset,
                    self.summary,
                    self.stable_base,
                    self.compaction_instruction,
                    self.ordinary_suffix,
                )
            )
            or self.reset <= 0
        ):
            raise ValueError("Context lengths and instruction sizes must be finite nonnegative.")

    def coefficients(self) -> tuple[float, float, float, float]:
        """Return carry c, affine compactor kappa, reset A0 and crossing-tail coefficient."""
        p, q = self.prices, self.cache_hit
        carry = p.write - q * (p.write - p.read)
        compactor = p.input - q * (p.input - p.read)
        setup = p.input * self.compaction_instruction + p.output * self.summary
        reset_fee = setup + (p.write - carry) * (self.reset - self.stable_base)
        reset_fee += compactor * self.reset
        return carry, compactor, reset_fee, q * (p.input - p.write)


def empirical_renewal(
    values: np.ndarray, weights: np.ndarray | None, quantum: int, maximum_gap: int
) -> dict[str, np.ndarray | float]:
    """Solve the renewal convolution deterministically, retaining zero growth.

    Nearest-lattice aggregation changes an increment by at most quantum/2.
    Actual finite simulations use original increments, not these bins. U and M
    at gap k*quantum include renewal locations STRICTLY below that gap, matching
    a >= crossing rule. Terminal marks use the full crossing increment.
    """
    if quantum <= 0 or maximum_gap < quantum:
        raise ValueError("Use a positive quantum and a larger finite gap range.")
    x = np.asarray(values, dtype=float)
    w = np.ones(len(x)) if weights is None else np.asarray(weights, dtype=float)
    if (
        x.ndim != 1
        or not len(x)
        or w.shape != x.shape
        or np.any(~np.isfinite(x))
        or np.any(~np.isfinite(w))
        or np.any(x < 0)
        or np.any(w < 0)
        or w.sum() <= 0
    ):
        raise ValueError("Need aligned nonnegative growth values and marginal weights.")
    w = w / w.sum()
    indices = np.floor(x / quantum + 0.5).astype(int)
    probabilities = np.bincount(indices, weights=w)
    positive_mass = 1 - probabilities[0]
    if positive_mass <= 0:
        raise ValueError("The ordinary growth law must have positive mean.")
    count = maximum_gap // quantum + 1
    mass = np.zeros(count)
    mass[0] = 1 / positive_mass
    for k in range(1, count):
        length = min(k, len(probabilities) - 1)
        mass[k] = np.dot(probabilities[1 : length + 1], mass[k - length : k][::-1]) / positive_mass
    gaps = np.arange(1, count) * quantum
    durations = np.cumsum(mass)[:-1]
    areas = quantum * np.cumsum(np.arange(count) * mass)[:-1]
    lag = gaps * durations - areas
    marked_mass = np.arange(len(probabilities)) * quantum * probabilities
    tail_expectation = np.cumsum(marked_mass[::-1])[::-1]
    forcing = np.zeros(count)
    length = min(count, len(tail_expectation))
    forcing[1:length] = tail_expectation[1:length]
    terminal_growth = np.maximum(0, fftconvolve(mass, forcing)[:count][1:])
    # Verify the WHOLE renewal equation, not merely its atom at zero.
    reconstructed = fftconvolve(probabilities, mass)[:count]
    residual = mass - reconstructed
    residual[0] -= 1
    return {
        "gaps": gaps,
        "duration": durations,
        "area": areas,
        "lag": lag,
        "terminal_growth": terminal_growth,
        "mean": float(np.dot(w, x)),
        "binned_mean": float(np.dot(probabilities, np.arange(len(probabilities)) * quantum)),
        "binned_moment2": float(
            np.dot(probabilities, (np.arange(len(probabilities)) * quantum) ** 2)
        ),
        "binned_moment3": float(
            np.dot(probabilities, (np.arange(len(probabilities)) * quantum) ** 3)
        ),
        "moment2": float(np.dot(w, x**2)),
        "moment3": float(np.dot(w, x**3)),
        "zero_mass": float(probabilities[0]),
        "lattice_span": float(quantum * np.gcd.reduce(np.flatnonzero(probabilities[1:] > 0) + 1)),
        "maximum_growth": float(quantum * np.flatnonzero(probabilities > 0)[-1]),
        "renewal_residual": float(np.max(np.abs(residual))),
    }


def analytic_rates(
    renewal: dict, ledger: RenewalLedger, output_mean: float
) -> dict[str, np.ndarray | float]:
    """Evaluate the exact binned-law cycle reward, plus separately labeled analytic reductions."""
    carry, compactor, setup, tail_coefficient = ledger.coefficients()
    if carry <= 0 or not np.isfinite(output_mean) or output_mean < 0:
        raise ValueError("Positive carry price and finite nonnegative output mean are required.")
    if not renewal["lag"][0] <= setup / carry <= renewal["lag"][-1]:
        raise ValueError("Expand the deterministic gap domain to bracket the analytic core root.")
    growth = renewal["binned_mean"]
    baseline = ledger.prices.input * ledger.ordinary_suffix + ledger.prices.output * output_mean
    baseline += (ledger.prices.write - carry * ledger.tail_fraction + compactor) * growth
    rate = (
        baseline
        + carry * ledger.reset
        + (
            setup
            + carry * renewal["area"]
            + tail_coefficient * ledger.tail_fraction * renewal["terminal_growth"]
        )
        / renewal["duration"]
    )
    core_gap = float(np.interp(setup / carry, renewal["lag"], renewal["gaps"]))
    index = int(np.argmin(rate))
    if index in (0, len(rate) - 1):
        raise ValueError("Expand or refine the gap domain: marked minimum is at an endpoint.")
    # Beyond the bracket the core rate is nondecreasing. Since G_T <= max G,
    # a negative terminal coefficient has a monotone lower envelope -C/U(L).
    # This certifies the unbounded right tail, rather than assuming a grid
    # interior minimum is globally optimal for an arbitrary marked law.
    terminal_price = tail_coefficient * ledger.tail_fraction
    core_end = rate[-1] - terminal_price * renewal["terminal_growth"][-1] / renewal["duration"][-1]
    tail_lower_bound = (
        core_end + min(terminal_price, 0) * renewal["maximum_growth"] / renewal["duration"][-1]
    )
    if tail_lower_bound <= rate[index]:
        raise ValueError("Expand the gap domain to certify the unbounded marked-cost tail.")
    return {
        "thresholds": renewal["gaps"] + ledger.reset,
        "rates": rate,
        "core_root_threshold": core_gap + ledger.reset,
        "marked_minimum_threshold": float(renewal["gaps"][index] + ledger.reset),
        "marked_minimum_rate": float(rate[index]),
        "fluid_threshold": ledger.reset + np.sqrt(2 * growth * setup / carry),
        "first_moment_correction_threshold": (
            ledger.reset
            + np.sqrt(2 * growth * setup / carry)
            - renewal["binned_moment2"] / (2 * growth)
        ),
        "duration_at_minimum": float(renewal["duration"][index]),
        "terminal_growth_at_minimum": float(renewal["terminal_growth"][index]),
        "baseline": baseline,
        "global_right_tail_lower_bound": float(tail_lower_bound),
        "global_right_tail_margin": float(tail_lower_bound - rate[index]),
    }


def simulate_renewal_ledger(
    growth: np.ndarray,
    output: np.ndarray,
    cache_marks: np.ndarray,
    ledger: RenewalLedger,
    thresholds: np.ndarray,
) -> dict[str, np.ndarray]:
    """Bill raw data-driven trajectories at all candidate thresholds, with no terminal reset.

    Arrays share ordinary action indices, not cycle count. Growth has already
    absorbed real output/tool context additions. Compaction reads warm prefix,
    consumes the uncached latest tail, generates summary, rebuilds context and
    then executes the next ordinary request. Four billed categories reconcile.
    """
    if growth.ndim != 2 or not growth.size or thresholds.ndim != 1 or not len(thresholds):
        raise ValueError("Need nonempty trajectory rows and one-dimensional thresholds.")
    count, calls = growth.shape
    if output.shape != growth.shape or cache_marks.shape != growth.shape:
        raise ValueError("Growth, invoice outputs and cache marks must align by ordinary action.")
    if (
        np.any(~np.isfinite(growth))
        or np.any(growth < 0)
        or np.any(~np.isfinite(output))
        or np.any(output < 0)
        or cache_marks.dtype != np.dtype(bool)
        or np.any(np.isnan(thresholds))
    ):
        raise ValueError(
            "Finite nonnegative increments/outputs and boolean cache marks are required."
        )
    if np.any(thresholds <= ledger.reset):
        raise ValueError("The regenerative lane requires trigger above reconstructed context.")
    shape = (count, len(thresholds))
    context = np.full(shape, ledger.reset, dtype=float)
    tail = np.zeros(shape)
    totals = {name: np.zeros(shape) for name in ("input", "write", "read", "output", "resets")}
    for t in range(calls):
        warm = cache_marks[:, t, None] * (context - tail)
        reset = context >= thresholds[None, :]
        totals["read"] += np.where(reset, warm, 0)
        totals["input"] += np.where(reset, context - warm + ledger.compaction_instruction, 0)
        totals["output"] += reset * ledger.summary
        context = np.where(reset, ledger.reset, context)
        warm = np.where(reset, cache_marks[:, t, None] * ledger.stable_base, warm)
        context += (1 - ledger.tail_fraction) * growth[:, t, None]
        totals["input"] += ledger.ordinary_suffix
        totals["write"] += context - warm
        totals["read"] += warm
        totals["output"] += output[:, t, None]
        totals["resets"] += reset
        tail = ledger.tail_fraction * growth[:, t, None]
        context += tail
    p = ledger.prices
    totals["cost"] = (
        p.input * totals["input"]
        + p.write * totals["write"]
        + p.read * totals["read"]
        + p.output * totals["output"]
    )
    totals["terminal_context"] = context
    return totals
