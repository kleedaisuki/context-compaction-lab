"""Synthetic positive marginals with explicit population-moment parameterization.

These families express assumptions, not evidence of a real workload's law.
Samples are never clipped: downstream simulations must retain tail overshoots.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import PositiveSpec


def sample_positive(
    spec: PositiveSpec,
    rng: np.random.Generator,
    size: int | tuple[int, ...],
) -> NDArray[np.float64]:
    """Draw a configured marginal using the caller-owned random generator.

    ``mean`` is the overall population mean, including for the burst mixture.
    For gamma and lognormal, ``cv`` is the population standard deviation divided
    by its mean. For burst_lognormal it describes each component, not the
    mixture's overall CV. A constant permits zero for gaps or document loads.

    Example:
        >>> draws = sample_positive(PositiveSpec(), np.random.default_rng(7), 10)
        >>> draws.shape
        (10,)
    """
    if spec.family == "constant":
        return np.full(size, spec.mean, dtype=np.float64)
    if spec.family == "gamma":
        shape = (1.0 / spec.cv) ** 2
        return rng.gamma(shape=shape, scale=spec.mean / shape, size=size)

    sigma_squared = 2.0 * np.log(np.hypot(1.0, spec.cv))
    unit_samples = rng.lognormal(mean=-0.5 * sigma_squared, sigma=np.sqrt(sigma_squared), size=size)
    if spec.family == "lognormal":
        return spec.mean * unit_samples

    ordinary_mean = spec.mean / (1.0 + spec.burst_probability * (spec.burst_multiplier - 1.0))
    burst = rng.random(size=size) < spec.burst_probability
    scales = np.where(burst, spec.burst_multiplier, 1.0)
    return ordinary_mean * scales * unit_samples
