"""Validate zero-location candidate fits and explicit inferential limitations."""

import json

import numpy as np
import pytest

from context_compaction_lab.calibration import fit_positive_samples


@pytest.mark.parametrize(
    "values",
    [
        [1] * 7,
        [1] * 10,
        [0] + list(range(1, 10)),
        [-1] + list(range(1, 10)),
        [np.inf] + list(range(1, 10)),
        [np.nan] + list(range(1, 10)),
        [[1, 2]] * 8,
    ],
)
def test_invalid_samples(values):
    """Do not invent a positive-law fit for unsupported observations."""
    with pytest.raises(ValueError):
        fit_positive_samples(values)


def test_gamma_parameter_recovery():
    """A reproducible gamma sample identifies its generating candidate and parameters."""
    values = np.random.default_rng(51).gamma(shape=2.5, scale=800, size=12_000)
    report = fit_positive_samples(values)
    assert report["selected_family"] == "gamma"
    candidate = next(c for c in report["candidates"] if c["family"] == "gamma")
    assert candidate["parameters"]["shape"] == pytest.approx(2.5, rel=0.05)
    assert candidate["parameters"]["scale"] == pytest.approx(800, rel=0.05)
    assert candidate["parameters"]["loc"] == 0


def test_lognormal_parameter_recovery():
    """A seeded skewed sample recovers log-space rather than raw-space parameters."""
    values = np.random.default_rng(79).lognormal(mean=7, sigma=0.9, size=12_000)
    report = fit_positive_samples(values)
    assert report["selected_family"] == "lognormal"
    candidate = next(c for c in report["candidates"] if c["family"] == "lognormal")
    assert candidate["parameters"]["mu"] == pytest.approx(7, abs=0.03)
    assert candidate["parameters"]["sigma"] == pytest.approx(0.9, abs=0.03)


def test_report_accounting_and_json():
    """Likelihood criteria, tail summaries, and warnings remain machine-readable."""
    report = fit_positive_samples(float(x) for x in range(1, 101))
    json.dumps(report, allow_nan=False)
    assert report["n"] == 100
    assert report["epistemic_status"] == "fitted_marginals_not_validated_workload"
    assert report["sample_summary"]["quantiles"]["q99"] > 98
    for candidate in report["candidates"]:
        ll = candidate["log_likelihood"]
        assert candidate["aic"] == pytest.approx(4 - 2 * ll)
        assert candidate["bic"] == pytest.approx(2 * np.log(100) - 2 * ll)
        assert 0 <= candidate["ks_distance"] <= 1
        assert "pvalue" not in candidate
        assert candidate["fitted_quantiles"]["q99"] > candidate["fitted_quantiles"]["q50"]
    assert any("KS" in warning for warning in report["warnings"])
