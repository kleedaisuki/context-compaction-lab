"""Deterministic ledgers protect stochastic simulations from billing drift."""

from dataclasses import replace

import numpy as np
import pytest

from context_compaction_lab.config import PositiveSpec, Pricing, RecoverySpec, Workload
from context_compaction_lab.simulation import RandomField, draw_random_field, simulate


def workload(**changes):
    """Use token prices 1, 2, 3, 4 to expose category errors clearly."""
    defaults = dict(
        calls=2,
        initial_context=10,
        minimum_cache_tokens=1,
        output_fraction=0.5,
        normal_uncached_tokens=1,
        compaction_instruction_tokens=2,
        cache_ttl_seconds=5,
        pricing=Pricing(1, 2, 3, 4),
        recovery=RecoverySpec(
            summary_base=3, fraction_mean=0, documents=PositiveSpec("constant", 4)
        ),
    )
    defaults.update(changes)
    return Workload(**defaults)


def marks(calls=2, growth=4, gap=0, documents=4):
    """Create one deterministic trajectory with the initial gap zero."""
    gaps = np.full((1, calls), gap, dtype=float)
    gaps[:, 0] = 0
    return RandomField(
        np.full((1, calls), growth), gaps, np.zeros((1, calls)), np.full((1, calls), documents)
    )


def assert_ledger(result, inputs, writes, reads, outputs, resets=0):
    """Check every disjoint token category and its implied USD total."""
    for name, expected in zip(
        ("input_tokens", "write_tokens", "read_tokens", "output_tokens"),
        (inputs, writes, reads, outputs),
        strict=True,
    ):
        assert getattr(result, name)[0] == expected
    assert result.compactions[0] == resets
    assert result.costs[0] == inputs + 2 * writes + 3 * reads + 4 * outputs


def test_warm_and_cold_output_tail():
    """Generated output is not cached until it is input on a later call."""
    field = marks()
    warm = simulate(workload(), np.inf, field)
    assert_ledger(warm, 2, 6, 22, 4)
    assert warm.cache_hits[0] == 2
    cold = simulate(workload(warm_start=False), np.inf, field)
    assert_ledger(cold, 2, 16, 12, 4)
    assert cold.cache_hits[0] == cold.cache_misses[0] == 1
    all_output = simulate(workload(output_fraction=1), np.inf, field)
    assert_ledger(all_output, 2, 4, 20, 8)


@pytest.mark.parametrize("gap, reads, writes", [(5, 22, 6), (5.001, 10, 18)])
def test_ttl_inclusive(gap, reads, writes):
    """Exactly TTL hits; any larger start gap expires the cached prefix."""
    result = simulate(workload(), np.inf, marks(gap=gap))
    assert_ledger(result, 2, writes, reads, 4)


def test_compaction_document_insertion_once_and_no_trailing_reset():
    """The compressor reads the old uncached tail but never writes old history."""
    result = simulate(workload(), 14, marks())
    # First normal: read 10/write 2/output 2; reset: read 12/input 2+2/output 3;
    # second normal: write summary 3 + docs 4 + retained input 2/output 2.
    assert_ledger(result, 6, 11, 22, 7, resets=1)
    assert result.max_context[0] == 14
    assert result.cache_hits[0] == result.cache_misses[0] == 1


def test_expired_compaction_and_fixed_overhead():
    """Expiry precedes compaction; fixed overhead is not a token category."""
    base = workload(compaction_fixed_usd=7)
    result = simulate(base, 14, marks(gap=6))
    assert result.input_tokens[0] == 18
    assert result.read_tokens[0] == 10
    total = sum(
        getattr(result, name)[0] * price
        for name, price in (
            ("input_tokens", 1),
            ("write_tokens", 2),
            ("read_tokens", 3),
            ("output_tokens", 4),
        )
    )
    assert result.costs[0] == total + 7


def test_minimum_cache_length():
    """Ineligible normal input is ordinary input, never cache writing."""
    result = simulate(workload(minimum_cache_tokens=15), np.inf, marks())
    assert_ledger(result, 14, 16, 0, 4)
    assert result.cache_misses[0] == 2


def test_recovery_overshoot_is_not_clipped_or_repeated():
    """Even a recovery beyond threshold produces at most one reset per call."""
    result = simulate(workload(calls=1), 5, marks(calls=1, documents=100))
    assert_ledger(result, 3, 105, 10, 5, resets=1)
    assert result.recovery_above_threshold[0] == 1
    assert result.max_context[0] == 107


def test_recovery_crossed_basis():
    """A crossed-context policy retains actual context, not the nominal line."""
    base = workload(
        calls=1,
        recovery=RecoverySpec(
            summary_base=0, fraction_mean=1, documents=PositiveSpec("constant", 0), basis="crossed"
        ),
    )
    field = RandomField([[4]], [[0]], [[1]], [[0]])
    result = simulate(base, 5, field)
    assert result.output_tokens[0] == 12
    assert result.write_tokens[0] == 12
    assert result.recovery_above_threshold[0] == 1


def test_reproducible_and_immutable_common_field():
    """Threshold branches cannot change future marks or caller-owned arrays."""
    base = workload(calls=10)
    first = draw_random_field(base, 7, 42)
    second = draw_random_field(base, 7, 42)
    for name in ("growth", "gaps", "recovery_fractions", "documents"):
        assert np.array_equal(getattr(first, name), getattr(second, name))
        with pytest.raises(ValueError):
            getattr(first, name).setflags(write=True)
    expected = simulate(base, np.inf, first).costs.copy()
    simulate(base, 15, first)
    assert np.array_equal(simulate(base, np.inf, first).costs, expected)
    source = np.array([[4.0]])
    owned = RandomField(source, [[0]], [[0]], [[0]])
    source[0, 0] = 99
    assert owned.growth[0, 0] == 4


@pytest.mark.parametrize("threshold", [0, -1, -np.inf, np.nan])
def test_invalid_threshold(threshold):
    """Infinity is allowed only in its positive no-compaction form."""
    with pytest.raises(ValueError):
        simulate(workload(), threshold, marks())


def test_draw_beta_endpoints_and_validation():
    """Degenerate fractions remain exact, without invalid Beta parameters."""
    for fraction in (0, 1):
        base = workload()
        base = replace(base, recovery=replace(base.recovery, fraction_mean=fraction))
        assert np.all(draw_random_field(base, 3, 1).recovery_fractions == fraction)
    with pytest.raises(ValueError):
        draw_random_field(workload(), 0, 1)
    with pytest.raises(ValueError):
        simulate(workload(calls=3), np.inf, marks())
