"""Price geometry and core threshold sensitivities for a declared renewal lane.

Prices change invoices, not the workload or tokenization in these interventions.
The core gradient selects the canonical D-inverse representative of an optimal
lattice plateau; marked-law minima must still be evaluated separately. Use
expected_category_rates for the full physical four-category ledger.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .config import Pricing
from .renewal_numerics import RenewalLedger

PRICE_CATEGORIES = ("input", "write", "read", "output")
"""Disjoint invoice coordinates, shared by analytic and trajectory repricing."""


def price_array(prices: Pricing) -> NDArray[np.float64]:
    """Return per-token USD coordinates without adding input and write together."""
    return np.array([getattr(prices, name) for name in PRICE_CATEGORIES], dtype=float)


@dataclass(frozen=True)
class CoreSensitivity:
    """Local canonical-root sensitivities with all nonvaried inputs held fixed.

    Price gradients are tokens per USD/token in PRICE_CATEGORIES order. Both
    elasticities are dimensionless: multiplying a gradient by its price and
    dividing by either the gap or full threshold. Other gradients distinguish
    replacement inside fixed S from adding material while preserving existing
    content. Growth-scale elasticity scales the whole increment law, not merely
    its mean. No ordinary Jacobian is returned at a positive renewal atom.
    """

    gap: float
    threshold: float
    duration: float
    carry: float
    reset_fee: float
    price_gradient: tuple[float, float, float, float]
    gap_price_elasticity: tuple[float, float, float, float]
    threshold_price_elasticity: tuple[float, float, float, float]
    hit_gradient: float
    stable_reclassification_gradient: float
    added_stable_gradient: float
    added_volatile_gradient: float
    summary_preserve_material_gradient: float
    summary_replace_material_gradient: float
    growth_scale_gap_elasticity: float


def core_sensitivity(renewal: dict, ledger: RenewalLedger) -> CoreSensitivity:
    """Differentiate cD=A jointly through the complete physical price coefficients.

    This is not a derivative of the integer controller's selected grid argmin,
    and does not omit c's dependence on write/read/hit parameters. It also does
    not include the terminal mark correction. Compare the separate full rates
    to determine whether that reduction changes a direction near a boundary.
    """
    c, kappa, a, _ = ledger.coefficients()
    if c <= 0 or a <= 0:
        raise ValueError("Positive carry and reset fee are needed for an interior core root.")
    ratio = a / c
    if not renewal["lag"][0] <= ratio < renewal["lag"][-1]:
        raise ValueError("The renewal domain must bracket the canonical core root.")
    gap = float(np.interp(ratio, renewal["lag"], renewal["gaps"]))
    left = int(np.argmin(abs(renewal["gaps"] - gap)))
    at_grid = abs(float(renewal["gaps"][left]) - gap) < 1e-8
    if at_grid and left + 1 >= len(renewal["duration"]):
        raise ValueError("Expand the renewal domain to bracket both slopes near its endpoint.")
    if at_grid and renewal["duration"][left + 1] - renewal["duration"][left] > 1e-12:
        raise ValueError(
            "Core root lies at a renewal atom: use directional slopes or exact plateau comparison."
        )
    index = int(np.searchsorted(renewal["gaps"], gap, side="right"))
    duration = float(renewal["duration"][index])
    p, q, s, b, summary = (
        ledger.prices,
        ledger.cache_hit,
        ledger.reset,
        ledger.stable_base,
        ledger.summary,
    )
    a_price = np.array([ledger.compaction_instruction + (1 - q) * s, q * (s - b), q * b, summary])
    c_price = np.array([0, 1 - q, q, 0])
    gradient = (a_price - ratio * c_price) / (c * duration)
    prices = price_array(p)
    a_hit = (p.write - p.input) * s - (p.write - p.read) * b
    c_hit = p.read - p.write
    hit_gradient = (a_hit - ratio * c_hit) / (c * duration)
    a_reset = (1 - q) * p.input + q * p.write
    return CoreSensitivity(
        gap=gap,
        threshold=s + gap,
        duration=duration,
        carry=c,
        reset_fee=a,
        price_gradient=tuple(float(x) for x in gradient),
        gap_price_elasticity=tuple(float(x) for x in gradient * prices / gap),
        threshold_price_elasticity=tuple(float(x) for x in gradient * prices / (s + gap)),
        hit_gradient=hit_gradient,
        stable_reclassification_gradient=-q * (p.write - p.read) / (c * duration),
        added_stable_gradient=1 + kappa / (c * duration),
        added_volatile_gradient=1 + a_reset / (c * duration),
        summary_preserve_material_gradient=1 + (a_reset + p.output) / (c * duration),
        summary_replace_material_gradient=p.output / (c * duration),
        growth_scale_gap_elasticity=(gap * duration - ratio) / (gap * duration),
    )


def expected_category_rates(
    renewal: dict, ledger: RenewalLedger, output_mean: float
) -> NDArray[np.float64]:
    """Return full marked-ledger expected input/write/read/output tokens per action.

    Each row is independent of prices. Contract: immutable workload/reset/cache
    law, no extra recovery requests, and complete regenerative cycles. The latest
    cold terminal increment is explicitly included. Columns align with
    PRICE_CATEGORIES; multiplying by price_array produces the existing physical
    rate formula. Counts cannot become negative even if a separated correction
    term is negative. Finite simulations must use their own endpoint categories.
    """
    if not np.isfinite(output_mean) or output_mean < 0:
        raise ValueError("Expected ordinary billed output must be finite nonnegative.")
    u, m, z, g = (
        renewal["duration"],
        renewal["area"],
        renewal["terminal_growth"],
        renewal["binned_mean"],
    )
    q, theta, s, b = ledger.cache_hit, ledger.tail_fraction, ledger.reset, ledger.stable_base
    inputs = (
        ledger.ordinary_suffix
        + (1 - q) * g
        + (ledger.compaction_instruction + (1 - q) * s + q * theta * z) / u
    )
    writes = (
        (1 - (1 - q) * theta) * g + (1 - q) * s + (q * (s - b) + (1 - q) * m - q * theta * z) / u
    )
    reads = q * ((1 - theta) * g + s + (b + m) / u)
    outputs = output_mean + ledger.summary / u
    basis = np.column_stack((inputs, writes, reads, outputs))
    if np.min(basis) < -1e-7 or np.any(~np.isfinite(basis)):
        raise ArithmeticError("Expected invoice categories must be finite nonnegative.")
    return basis


def reprice_categories(categories: NDArray, prices: Pricing) -> NDArray[np.float64]:
    """Reprice final-axis four-category counts with no new workload simulation.

    Examples:
        ``costs = reprice_categories(token_totals, Pricing())`` where the array
        has shape (replicates, thresholds, 4), returns (replicates, thresholds).
    """
    counts = np.asarray(categories, dtype=float)
    if counts.ndim < 1 or not counts.size or counts.shape[-1] != 4:
        raise ValueError("The last axis must contain the four disjoint categories.")
    if np.any(~np.isfinite(counts)) or np.min(counts) < 0:
        raise ValueError("Category totals must be finite nonnegative.")
    return counts @ price_array(prices)
