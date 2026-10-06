"""Protect fixed/narrow recovery and distinguish preservation from generation."""

from dataclasses import replace

import numpy as np
import pytest

from context_compaction_lab.config import PositiveSpec, Pricing, RecoverySpec, Workload
from context_compaction_lab.simulation import RandomField, draw_random_field, simulate


def small_workload(recovery: RecoverySpec) -> Workload:
    """Use one tiny, initially warm request to isolate compaction accounting."""
    return Workload(
        calls=1,
        initial_context=10,
        minimum_cache_tokens=1,
        output_fraction=0.5,
        normal_uncached_tokens=1,
        compaction_instruction_tokens=2,
        pricing=Pricing(1, 2, 3, 4),
        recovery=recovery,
    )


def field(documents: int = 4) -> RandomField:
    """Provide a deterministic normal request and zero legacy retention fraction."""
    return RandomField([[4]], [[0]], [[0]], [[documents]])


def test_default_recovery_is_constant_and_independent_of_threshold() -> None:
    """The main workload has 2k generated summary plus 12k reloaded documents."""
    workload = replace(Workload(), calls=1, initial_context=50_000)
    marks = draw_random_field(workload, 32, 7)
    assert np.all(marks.documents == 12_000)
    assert np.all(marks.recovery_fractions == 0)
    lower = simulate(workload, 20_000, marks)
    upper = simulate(workload, 40_000, marks)
    np.testing.assert_array_equal(lower.costs, upper.costs)
    np.testing.assert_array_equal(lower.output_tokens, upper.output_tokens)


def test_preserved_messages_are_not_summary_output() -> None:
    """Six verbatim tokens are restored as input but never generated again."""
    recovery = RecoverySpec(
        summary_base=3, documents=PositiveSpec("constant", 4), preserved_tokens=6
    )
    result = simulate(small_workload(recovery), 5, field())
    assert result.output_tokens[0] == 3 + 2
    assert result.write_tokens[0] == 6 + 3 + 4 + 2
    assert result.read_tokens[0] == 10
    assert result.input_tokens[0] == 2 + 1


def test_declared_surviving_prefix_reuses_only_warm_preserved_tokens() -> None:
    """A valid six-token leading boundary is read instead of rewritten."""
    recovery = RecoverySpec(
        summary_base=3,
        documents=PositiveSpec("constant", 4),
        preserved_tokens=6,
        surviving_prefix_tokens=6,
    )
    result = simulate(small_workload(recovery), 5, field())
    assert result.read_tokens[0] == 10 + 6
    assert result.write_tokens[0] == 3 + 4 + 2
    assert result.output_tokens[0] == 5


def test_expired_prefix_cannot_be_resurrected_by_preservation() -> None:
    """Token identity does not make an expired cache boundary warm."""
    recovery = RecoverySpec(
        summary_base=3,
        documents=PositiveSpec("constant", 4),
        preserved_tokens=6,
        surviving_prefix_tokens=6,
    )
    workload = replace(small_workload(recovery), calls=2, cache_ttl_seconds=5)
    marks = RandomField([[4, 4]], [[0, 6]], [[0, 0]], [[4, 4]])
    survivor = simulate(workload, 14, marks)
    cold = simulate(
        replace(workload, recovery=replace(recovery, surviving_prefix_tokens=0)), 14, marks
    )
    np.testing.assert_array_equal(survivor.costs, cold.costs)


def test_preservation_cannot_copy_more_than_the_available_old_context() -> None:
    """Preservation is limited by existing state, not by an arbitrary tail cap."""
    recovery = RecoverySpec(
        summary_base=3, documents=PositiveSpec("constant", 4), preserved_tokens=100
    )
    result = simulate(small_workload(recovery), 5, field())
    assert result.write_tokens[0] == 10 + 3 + 4 + 2
    assert result.output_tokens[0] == 5


def test_preservation_does_not_change_output_only_invoice() -> None:
    """With all input rates zero, retaining old messages creates no new output fee."""
    recovery = RecoverySpec(summary_base=3, documents=PositiveSpec("constant", 4))
    workload = replace(small_workload(recovery), pricing=Pricing(0, 0, 0, 1))
    plain = simulate(workload, 5, field())
    preserved = simulate(
        replace(workload, recovery=replace(recovery, preserved_tokens=6)), 5, field()
    )
    np.testing.assert_array_equal(plain.costs, preserved.costs)


def test_narrow_summary_and_documents_preserve_ordinary_random_marks() -> None:
    """Small recovery noise does not alter the paired growth and gap workload."""
    fixed = Workload(calls=20)
    narrow = replace(
        fixed,
        recovery=replace(
            fixed.recovery,
            summary=PositiveSpec("lognormal", 2_000, cv=0.05),
            documents=PositiveSpec("lognormal", 12_000, cv=0.05),
        ),
    )
    first = draw_random_field(fixed, 256, 7)
    second = draw_random_field(narrow, 256, 7)
    np.testing.assert_array_equal(first.growth, second.growth)
    np.testing.assert_array_equal(first.gaps, second.gaps)
    assert second.summary_tokens is not None
    assert np.std(second.summary_tokens) / np.mean(second.summary_tokens) < 0.07
    with pytest.raises(ValueError):
        second.summary_tokens.setflags(write=True)


def test_summary_distribution_needs_explicit_random_marks() -> None:
    """Do not substitute a mean when a stochastic summary field is missing."""
    recovery = RecoverySpec(summary=PositiveSpec("lognormal", 3, cv=0.05))
    with pytest.raises(ValueError):
        simulate(small_workload(recovery), 5, field())


@pytest.mark.parametrize("fraction", [0.03, 1.0])
def test_distributed_and_proportional_summary_are_exclusive(fraction: float) -> None:
    """One generated summary cannot be silently priced with two conflicting laws."""
    with pytest.raises(ValueError):
        RecoverySpec(summary=PositiveSpec("constant", 3), fraction_mean=fraction)


def test_invalid_surviving_boundaries_are_rejected() -> None:
    """Only a preserved, cache-eligible leading boundary can be declared reusable."""
    with pytest.raises(ValueError):
        RecoverySpec(preserved_tokens=5, surviving_prefix_tokens=6)
    with pytest.raises(ValueError):
        Workload(recovery=RecoverySpec(preserved_tokens=500, surviving_prefix_tokens=500))
