"""Crosscheck empirical renewal rewards using an independent category-level DP.

Run ``uv run python experiments/renewal_ledger_crosscheck.py`` from the repository
root. The probe uses a constructed finite law, no private traces or API calls.
Results are written under ``.cache/renewal-ledger-crosscheck/``. Expected costs
are priced only after independently computing the four category token totals.
No renewal reward coefficients are used inside the dynamic program.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from context_compaction_lab.renewal_numerics import (
    RenewalLedger,
    analytic_rates,
    empirical_renewal,
)


@dataclass(frozen=True)
class CycleExpectation:
    """Expected complete-cycle statistics for a constructed finite growth law.

    ``categories`` orders mutually exclusive input, write, read and all output
    tokens. ``area`` is pre-call cumulative growth, excluding reset context.
    ``rate`` divides the priced complete-cycle reward by expected action count.
    The cycle starts after reconstruction and ends with the next compactor.
    """

    duration: float
    area: float
    terminal_increment: float
    categories: tuple[float, float, float, float]
    rate: float


def category_cycle_dp(
    values: NDArray[np.int64],
    probabilities: NDArray[np.float64],
    gap: int,
    ledger: RenewalLedger,
) -> CycleExpectation:
    """Solve ordinary-boundary states directly, without renewal mass or fees.

    This bounded probe requires integer nonnegative growth with positive mean.
    Each state stores cumulative growth ``y`` and the latest post-call tail.
    Holding ``y`` fixed, the tail changes only the immediately next cache read
    and write. State-zero-tail values therefore determine other tail states by
    an exact category transfer; zero increments induce a solvable self-loop.
    Every cache event is averaged from declared Bernoulli hit probability.
    """
    if (
        gap < 1
        or values.ndim != 1
        or probabilities.shape != values.shape
        or np.any(values < 0)
        or np.any(probabilities < 0)
        or not np.isclose(probabilities.sum(), 1)
        or np.dot(values, probabilities) <= 0
    ):
        raise ValueError("Require a positive gap and a finite nonnegative integer law.")
    q, theta = ledger.cache_hit, ledger.tail_fraction
    p0 = float(probabilities[values == 0].sum())
    durations = np.zeros(gap)
    areas = np.zeros(gap)
    terminals = np.zeros(gap)
    categories = np.zeros((gap, 4))

    for y in range(gap - 1, -1, -1):
        durations[y], areas[y] = 1, y
        for growth, weight in zip(values, probabilities, strict=True):
            current_input = ledger.reset + y + (1 - theta) * growth
            cached_input = q * (ledger.reset + y)
            normal = np.array(
                [
                    ledger.ordinary_suffix,
                    current_input - cached_input,
                    cached_input,
                    7.0,
                ]
            )
            categories[y] += weight * normal
            if growth == 0:
                continue
            if y + growth >= gap:
                old_input = ledger.reset + y + growth
                cached_old_input = q * (old_input - theta * growth)
                compactor = np.array(
                    [
                        old_input - cached_old_input + ledger.compaction_instruction,
                        0.0,
                        cached_old_input,
                        ledger.summary,
                    ]
                )
                categories[y] += weight * compactor
                terminals[y] += weight * growth
            else:
                # A prior tail shifts tokens from the next read to its write.
                tail_transfer = np.array([0.0, q * theta * growth, -q * theta * growth, 0.0])
                categories[y] += weight * (categories[y + growth] + tail_transfer)
                durations[y] += weight * durations[y + growth]
                areas[y] += weight * areas[y + growth]
                terminals[y] += weight * terminals[y + growth]
        categories[y] /= 1 - p0
        durations[y] /= 1 - p0
        areas[y] /= 1 - p0
        terminals[y] /= 1 - p0

    # Only the FIRST request after reconstruction can reuse B rather than S.
    initial_transfer = q * (ledger.reset - ledger.stable_base)
    expected_categories = categories[0] + np.array([0.0, initial_transfer, -initial_transfer, 0.0])
    prices = np.array(
        [
            ledger.prices.input,
            ledger.prices.write,
            ledger.prices.read,
            ledger.prices.output,
        ]
    )
    expected_rate = float(np.dot(prices, expected_categories) / durations[0])
    return CycleExpectation(
        float(durations[0]),
        float(areas[0]),
        float(terminals[0]),
        tuple(float(token_count) for token_count in expected_categories),
        expected_rate,
    )


def main() -> None:
    """Compare 45 exact finite-law cases and save compact aggregate discrepancies."""
    values = np.array([0, 1, 3, 8], dtype=np.int64)
    probabilities = np.array([0.2, 0.2, 0.3, 0.3], dtype=np.float64)
    renewal = empirical_renewal(values, probabilities, quantum=1, maximum_gap=2000)
    gaps = (1, 3, 8, 17, 55)
    hits = (0.0, 0.6, 1.0)
    timing = (0.0, 0.4, 1.0)
    errors = []
    example = None
    for hit in hits:
        for fraction in timing:
            ledger = RenewalLedger(
                reset=100,
                summary=10,
                stable_base=20,
                cache_hit=hit,
                tail_fraction=fraction,
            )
            curve = analytic_rates(renewal, ledger, output_mean=7)
            for gap in gaps:
                direct = category_cycle_dp(values, probabilities, gap, ledger)
                index = gap - 1
                direct_values = np.array(
                    [
                        direct.duration,
                        direct.area,
                        direct.terminal_increment,
                        direct.rate,
                    ]
                )
                renewal_values = np.array(
                    [
                        renewal["duration"][index],
                        renewal["area"][index],
                        renewal["terminal_growth"][index],
                        curve["rates"][index],
                    ]
                )
                errors.append(np.abs(direct_values - renewal_values))
                if (hit, fraction, gap) == (0.6, 0.4, 17):
                    example = {
                        "hit": hit,
                        "timing_fraction": fraction,
                        "gap": gap,
                        "expected_categories_I_W_R_O": direct.categories,
                        "duration": direct.duration,
                        "usd_per_action": direct.rate,
                    }
    maximum = np.max(errors, axis=0)
    assert maximum[0] < 1e-12
    assert maximum[1] < 1e-10
    assert maximum[2] < 1e-12
    assert maximum[3] < 1e-15
    report = {
        "law": {"increments": values.tolist(), "probabilities": probabilities.tolist()},
        "gaps": gaps,
        "cache_hits": hits,
        "tail_fractions": timing,
        "cases": len(errors),
        "method": "Independent residual-state category DP; prices applied only at the end",
        "maximum_absolute_error_T_M_terminal_USD_rate": maximum.tolist(),
        "example": example,
        "scope": "Constructed finite-law identity checks, not workload fit or population inference",
    }
    destination = Path(__file__).resolve().parents[1] / ".cache" / "renewal-ledger-crosscheck"
    destination.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    (destination / "results.json").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
