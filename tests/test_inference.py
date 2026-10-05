"""Check statistical units, paired contrasts, and the symbolic renewal benchmark."""

import numpy as np
import pytest

from context_compaction_lab.analytic import exponential_benchmark
from context_compaction_lab.inference import estimate_mean, paired_difference


def test_constant_outcomes_have_zero_monte_carlo_error() -> None:
    """A deterministic independent sample has an exact zero-width interval."""
    result = estimate_mean(np.ones(20) * 3)
    assert result.mean == 3
    assert result.ci_low == result.ci_high == 3


def test_pairing_removes_shared_variation() -> None:
    """Subtracting common marks avoids an unpaired variance calculation."""
    values = np.arange(20, dtype=float)
    result = paired_difference(values + 2, values)
    assert result.mean == 2
    assert result.standard_error == 0


def test_nonfinite_samples_are_not_silently_removed() -> None:
    """Invalid replicates must fail instead of biasing the expected cost."""
    with pytest.raises(ValueError):
        estimate_mean(np.array([1, np.nan, 2]))


def test_exponential_benchmark_symbolic_identities() -> None:
    """The exact overshoot benchmark verifies its derivative and minimum."""
    expressions = exponential_benchmark()
    assert len(expressions) == 9
