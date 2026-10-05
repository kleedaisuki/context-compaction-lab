"""Fit candidate positive marginals without claiming a validated workload model.

Maximum likelihood uses location zero and two fitted parameters per family.
Selection and in-sample tail diagnostics do not validate independence,
stationarity, or the conditional recovery mechanism required by simulation.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from scipy import stats

_QUANTILES = {"q50": 0.5, "q90": 0.9, "q95": 0.95, "q99": 0.99}


def fit_positive_samples(values: Iterable[float]) -> dict[str, object]:
    """Return JSON-compatible gamma and lognormal maximum-likelihood fits.

    Require at least eight finite, strictly positive, nonconstant observations.
    Candidate AIC/BIC count two parameters because location is fixed to zero.
    The KS distance is descriptive: ordinary KS p-values are invalid after
    fitting parameters on the same observations and are deliberately omitted.

    The caller must establish measurement units, sampling provenance, missing
    values, dependence, and drift before treating fits as calibrated assumptions.
    Even a lowest-AIC family may miss the tail; compare fitted and empirical
    quantiles before using a model for threshold-policy research.

    Example:
        >>> report = fit_positive_samples([1, 2, 3, 4, 5, 6, 7, 8])
        >>> len(report["candidates"])
        2
    """
    samples = np.asarray(list(values), dtype=np.float64)
    if samples.ndim != 1 or samples.size < 8:
        raise ValueError("Calibration requires a one-dimensional sample of at least 8 values.")
    if not np.all(np.isfinite(samples)) or np.any(samples <= 0):
        raise ValueError("Calibration observations must be finite and strictly positive.")
    std = float(np.std(samples, ddof=1))
    if not np.isfinite(std) or std <= 0:
        raise ValueError("Calibration requires positive, finite sample variance.")

    n = int(samples.size)
    mean = float(np.mean(samples))
    empirical = {
        label: float(np.quantile(samples, probability)) for label, probability in _QUANTILES.items()
    }
    candidates = [_fit_candidate(family, samples) for family in ("gamma", "lognormal")]
    selected = min(candidates, key=lambda candidate: candidate["aic"])
    return {
        "n": n,
        "epistemic_status": "fitted_marginals_not_validated_workload",
        "sample_summary": {
            "mean": mean,
            "std": std,
            "cv": std / mean,
            "min": float(np.min(samples)),
            "max": float(np.max(samples)),
            "quantiles": empirical,
            "q99_to_q50": empirical["q99"] / empirical["q50"],
            "max_to_mean": float(np.max(samples)) / mean,
        },
        "candidates": candidates,
        "selected_family": selected["family"],
        "selection_criterion": "minimum_in_sample_aic",
        "warnings": [
            "Synthetic distributions are assumptions; fitted marginals do not validate a workload.",
            "KS distances are descriptive; no fitted-sample KS p-values are reported.",
            "AIC/BIC selection and tail diagnostics are in-sample, not held-out validation.",
            "Fits do not establish independence, stationarity, or recovery dependence.",
            "Tail quantiles, especially q99 in small samples, have substantial uncertainty.",
        ],
    }


def _fit_candidate(family: str, samples: np.ndarray) -> dict[str, object]:
    """Fit one zero-location family and compute comparable in-sample diagnostics."""
    distribution = stats.gamma if family == "gamma" else stats.lognorm
    shape, _, scale = distribution.fit(samples, floc=0)
    fitted = distribution(shape, loc=0, scale=scale)
    log_likelihood = float(np.sum(fitted.logpdf(samples)))
    quantiles = {label: float(fitted.ppf(probability)) for label, probability in _QUANTILES.items()}
    if not np.isfinite(log_likelihood) or not all(np.isfinite(q) for q in quantiles.values()):
        raise ValueError(f"The {family} fit is numerically nonfinite; rescale observations.")
    if family == "gamma":
        parameters = {"shape": float(shape), "scale": float(scale), "loc": 0.0}
        cv = float(1 / np.sqrt(shape))
    else:
        parameters = {"mu": float(np.log(scale)), "sigma": float(shape), "loc": 0.0}
        cv = float(np.sqrt(np.expm1(shape**2)))
    fitted_mean = float(fitted.mean())
    if not np.isfinite(fitted_mean) or not np.isfinite(cv):
        raise ValueError(f"The {family} fit has unrepresentable moments; inspect sample scales.")
    return {
        "family": family,
        "parameters": parameters,
        "mean": fitted_mean,
        "cv": cv,
        "log_likelihood": log_likelihood,
        "parameter_count": 2,
        "aic": 4.0 - 2.0 * log_likelihood,
        "bic": float(2 * np.log(samples.size) - 2 * log_likelihood),
        "ks_distance": float(stats.kstest(samples, fitted.cdf).statistic),
        "fitted_quantiles": quantiles,
    }
