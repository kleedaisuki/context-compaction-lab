"""Reject invalid stochastic-domain inputs before simulation or array allocation."""

import math

import pytest

from context_compaction_lab.config import RecoverySpec, Workload
from context_compaction_lab.inference import sweep_thresholds


@pytest.mark.parametrize("value", [math.nan, math.inf, 1.5, True, -1])
def test_context_requires_nonnegative_integer(value) -> None:
    """Typed configuration must enforce finite token counts at runtime."""
    with pytest.raises(ValueError):
        Workload(initial_context=value)


@pytest.mark.parametrize("value", [math.nan, 1.5, True, -1])
def test_summary_requires_nonnegative_integer(value) -> None:
    """Malformed recovery must not create NaN trajectory costs."""
    with pytest.raises(ValueError):
        RecoverySpec(summary_base=value)


@pytest.mark.parametrize("value", [math.nan, 1.5, True, 0])
def test_calls_requires_positive_integer(value) -> None:
    """Shape errors are domain errors, not deferred NumPy failures."""
    with pytest.raises(ValueError):
        Workload(calls=value)


@pytest.mark.parametrize("step", [0, -1, math.nan, math.inf])
def test_secant_step_must_be_positive_and_finite(step) -> None:
    """Never divide by zero or invent derivative intervals from invalid steps."""
    with pytest.raises(ValueError):
        sweep_thresholds(Workload(calls=2), [25_000], 2, 7, difference_step=step)
