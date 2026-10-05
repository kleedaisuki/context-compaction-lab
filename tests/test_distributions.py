"""Verify synthetic population moments and reproducible uncensored draws."""

import numpy as np
import pytest

from context_compaction_lab.config import PositiveSpec
from context_compaction_lab.distributions import sample_positive


@pytest.mark.parametrize("family", ["gamma", "lognormal"])
def test_moments(family):
    """Large seeded fixtures recover both configured moments within sampling noise."""
    spec = PositiveSpec(family, mean=2_000, cv=0.8)
    draws = sample_positive(spec, np.random.default_rng(17), 200_000)
    assert np.mean(draws) == pytest.approx(spec.mean, rel=0.01)
    assert np.std(draws) / np.mean(draws) == pytest.approx(spec.cv, rel=0.02)
    assert np.all(draws > 0)


def test_burst_overall_mean():
    """Burst scales preserve the overall rather than the ordinary component mean."""
    spec = PositiveSpec(
        "burst_lognormal", mean=2_000, cv=0.4, burst_probability=0.2, burst_multiplier=10
    )
    draws = sample_positive(spec, np.random.default_rng(11), 250_000)
    assert np.mean(draws) == pytest.approx(2_000, rel=0.015)
    assert np.std(draws) / np.mean(draws) > spec.cv
    assert draws.max() > 10 * spec.mean


@pytest.mark.parametrize("probability", [0.0, 1.0])
def test_burst_endpoint_means(probability):
    """Degenerate mixture endpoints still preserve the specified total mean."""
    spec = PositiveSpec(
        "burst_lognormal", mean=3, cv=0.2, burst_probability=probability, burst_multiplier=10
    )
    draws = sample_positive(spec, np.random.default_rng(13), 100_000)
    assert draws.mean() == pytest.approx(3, rel=0.01)


def test_constant_zero_and_shape():
    """Zero-valued constants support gap and document marginals with matrix shapes."""
    draws = sample_positive(
        PositiveSpec("constant", mean=0, cv=0), np.random.default_rng(3), (4, 5)
    )
    assert draws.shape == (4, 5)
    assert draws.dtype == np.float64
    assert np.array_equal(draws, np.zeros((4, 5)))


def test_repeatable_rng():
    """Caller-owned seeds reproduce draws without a hidden global generator."""
    spec = PositiveSpec("burst_lognormal")
    first = sample_positive(spec, np.random.default_rng(9), (3, 9))
    second = sample_positive(spec, np.random.default_rng(9), (3, 9))
    assert np.array_equal(first, second)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mean": 0},
        {"cv": 0},
        {"mean": np.inf},
        {"cv": np.nan},
        {"burst_probability": 1.1},
        {"burst_multiplier": 0.5},
    ],
)
def test_validation_precedes_sampling(kwargs):
    """Invalid moment assumptions fail in the source specification contract."""
    with pytest.raises(ValueError):
        PositiveSpec(**kwargs)
