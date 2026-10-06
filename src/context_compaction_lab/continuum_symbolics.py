"""Continuous task-level budget regularization of exact endogenous threshold laws.

One budget H=max(1,h+sigma*Z) is sampled for the entire task. Gaussian smoothing
does not replace any endogenous simulator transitions and is not per-decision
jitter. A smooth randomized-controller objective is not automatically a
continuum approximation to the unsmoothed physical system.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import sympy as sp
from scipy.special import log_ndtr, logsumexp, ndtr

from .structural_symbolics import PRICES, THRESHOLD, ThresholdCurve

SIGMA = sp.Symbol("sigma", positive=True)
"""Positive task-level threshold uncertainty, in the threshold's token units."""


def normal_cdf(expression: sp.Expr) -> sp.Expr:
    """Return the exact normal CDF through erf, suitable for symbolic differentiation."""
    return (1 + sp.erf(expression / sp.sqrt(2))) / 2


@dataclass(frozen=True)
class GaussianThresholdModel:
    """Exact base invoice and jump masses of a whole-task randomized controller.

    Boundaries are positive integer tokens from an exact ThresholdCurve. The
    lower clipping point 1 lies in its first right-closed cell, so clipping adds
    no new jump and P(H>b)=Phi((h-b)/sigma) at every existing boundary.
    """

    base: sp.Expr
    boundaries: tuple[int, ...]
    jumps: tuple[sp.Expr, ...]

    def __post_init__(self) -> None:
        """Detach data and reject unordered boundaries or approximate symbolic values."""
        boundaries = tuple(self.boundaries)
        jumps = tuple(sp.sympify(jump) for jump in self.jumps)
        base = sp.sympify(self.base)
        if len(boundaries) != len(jumps):
            raise ValueError("Each threshold boundary requires exactly one jump.")
        if (any(type(boundary) is not int or boundary < 1 for boundary in boundaries)
                or any(left >= right for left, right in zip(boundaries, boundaries[1:]))):
            raise ValueError("Boundaries must be strictly increasing positive integer tokens.")
        if any(value.has(sp.Float, sp.nan, sp.oo, -sp.oo) for value in (base, *jumps)):
            raise ValueError("Symbolic invoices require exact finite expressions, not floats.")
        object.__setattr__(self, "base", base)
        object.__setattr__(self, "boundaries", boundaries)
        object.__setattr__(self, "jumps", jumps)

    @classmethod
    def from_curve(
        cls, curve: ThresholdCurve, prices: Sequence[sp.Expr] = PRICES,
    ) -> GaussianThresholdModel:
        """Preserve actual-engine stopping, recovery and cache effects inside jump costs."""
        boundaries = tuple(band.upper for band in curve.bands[:-1])
        jumps = tuple(right.occupation.difference(left.occupation).cost(prices)
                      for left, right in zip(curve.bands, curve.bands[1:]))
        return cls(curve.bands[0].occupation.cost(prices), boundaries, jumps)

    def symbolic_cost(
        self, mean: sp.Expr = THRESHOLD, sigma: sp.Expr = SIGMA,
    ) -> sp.Expr:
        """Return E[J(max(1,h+sigma Z))] with one Gaussian budget per whole task."""
        return self.base + sp.Add(*(jump * normal_cdf((mean - boundary) / sigma)
                                   for boundary, jump in zip(self.boundaries, self.jumps)))

    def symbolic_gradient(
        self, mean: sp.Expr = THRESHOLD, sigma: sp.Expr = SIGMA,
    ) -> sp.Expr:
        """Convolve exact jump masses with the Gaussian density, not ordinary-state noise."""
        return sp.Add(*(jump * sp.exp(-(mean - boundary)**2 / (2 * sigma**2))
                        / (sigma * sp.sqrt(2 * sp.pi))
                        for boundary, jump in zip(self.boundaries, self.jumps)))

    def symbolic_curvature(
        self, mean: sp.Expr = THRESHOLD, sigma: sp.Expr = SIGMA,
    ) -> sp.Expr:
        """Differentiate the Gaussian jump-density gradient exactly."""
        return sp.Add(*(-jump * (mean - boundary)
                        * sp.exp(-(mean - boundary)**2 / (2 * sigma**2))
                        / (sigma**3 * sp.sqrt(2 * sp.pi))
                        for boundary, jump in zip(self.boundaries, self.jumps)))

    def evaluate(
        self, mean: np.ndarray | float, sigma: float, substitutions: dict,
    ) -> dict[str, np.ndarray]:
        """Evaluate stable normal kernels; approximate numbers appear only at this boundary."""
        centers, width = _numeric_inputs(mean, sigma)
        base, boundaries, jumps = self._numeric_coefficients(substitutions)
        offsets = centers[..., None] - boundaries
        z = offsets / width
        density = np.exp(-z**2 / 2) / (width * math.sqrt(2 * math.pi))
        log_jumps = np.full(len(jumps), -math.inf)
        nonzero = jumps != 0
        log_jumps[nonzero] = np.log(np.abs(jumps[nonzero]))
        return {
            "cost": base + np.sum(ndtr(z) * jumps, axis=-1),
            "gradient": np.sum(density * jumps, axis=-1),
            "curvature": np.sum(-offsets / width**2 * density * jumps, axis=-1),
            "local_error_bound": np.sum(ndtr(-np.abs(z)) * np.abs(jumps), axis=-1),
            "log_local_error_bound": logsumexp(log_jumps + log_ndtr(-np.abs(z)), axis=-1),
        }

    def band_integral(
        self, mean: np.ndarray | float, sigma: float, substitutions: dict,
    ) -> np.ndarray:
        """Independently integrate cell costs against the entire-task budget distribution."""
        centers, width = _numeric_inputs(mean, sigma)
        base, boundaries, jumps = self._numeric_coefficients(substitutions)
        probabilities = gaussian_band_probabilities(boundaries, centers, width)
        cell_costs = base + np.concatenate(([0.0], np.cumsum(jumps)))
        return np.sum(probabilities * cell_costs, axis=-1)

    def scaled_gradient(
        self, mean: float, sigma: float, substitutions: dict,
    ) -> float:
        """Preserve derivative sign for root finding even when all density values underflow."""
        centers, width = _numeric_inputs(mean, sigma)
        if centers.ndim:
            raise ValueError("Scaled root evaluation requires a scalar mean.")
        _, boundaries, jumps = self._numeric_coefficients(substitutions)
        nonzero = jumps != 0
        if not np.any(nonzero):
            return 0.0
        log_terms = (np.log(np.abs(jumps[nonzero]))
                     - ((float(centers) - boundaries[nonzero]) / width)**2 / 2)
        return float(np.sum(np.sign(jumps[nonzero]) * np.exp(log_terms - log_terms.max())))

    def derivative_log(
        self, mean: float, sigma: float, substitutions: dict, *, order: int = 1,
    ) -> tuple[float, float]:
        """Return log absolute derivative and sign, retaining small-bandwidth information."""
        centers, width = _numeric_inputs(mean, sigma)
        if centers.ndim or order not in (1, 2):
            raise ValueError("Derivative logs require a scalar mean and order 1 or 2.")
        _, boundaries, coefficients = self._numeric_coefficients(substitutions)
        offsets = float(centers) - boundaries
        if order == 2:
            coefficients = coefficients * (-offsets / width**2)
        nonzero = coefficients != 0
        if not np.any(nonzero):
            return -math.inf, 0.0
        logs = (np.log(np.abs(coefficients[nonzero])) - (offsets[nonzero] / width)**2 / 2
                - math.log(width * math.sqrt(2 * math.pi)))
        log_absolute, sign = logsumexp(logs, b=np.sign(coefficients[nonzero]), return_sign=True)
        return float(log_absolute), float(sign)

    def _numeric_coefficients(self, substitutions: dict) -> tuple[float, np.ndarray, np.ndarray]:
        """Evaluate exact symbolic invoices, rejecting unresolved or nonfinite coefficients."""
        values = (self.base, *self.jumps)
        converted = [float(value.subs(substitutions)) for value in values]
        if not np.all(np.isfinite(converted)):
            raise ValueError("Numerical invoices must be finite after substitution.")
        return converted[0], np.asarray(self.boundaries, dtype=float), np.array(converted[1:])


def _numeric_inputs(mean: np.ndarray | float, sigma: float) -> tuple[np.ndarray, float]:
    """Validate a real controller center and a strictly positive regularization scale."""
    centers = np.asarray(mean, dtype=float)
    if np.any(~np.isfinite(centers)) or not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("Controller centers must be finite and sigma strictly positive.")
    return centers, float(sigma)


def gaussian_band_probabilities(
    boundaries: np.ndarray, mean: np.ndarray | float, sigma: float,
) -> np.ndarray:
    """Compute exact Gaussian cell probabilities without subtracting two near-one CDFs.

    The first cell absorbs every raw budget below its upper boundary, including
    the atom induced by max(1,raw budget). The final cell has an infinite tail.
    """
    centers, width = _numeric_inputs(mean, sigma)
    edges = np.asarray(boundaries, dtype=float)
    if edges.ndim != 1 or np.any(~np.isfinite(edges)) or np.any(np.diff(edges) <= 0):
        raise ValueError("Band boundaries must be a finite increasing vector.")
    if not len(edges):
        return np.ones((*centers.shape, 1))
    z = (edges - centers[..., None]) / width
    left, right = z[..., :-1], z[..., 1:]
    interior = np.where(left >= 0, ndtr(-left) - ndtr(-right), ndtr(right) - ndtr(left))
    return np.concatenate((ndtr(z[..., :1]), interior, ndtr(-z[..., -1:])), axis=-1)


def uniform_continuum_expressions() -> dict[str, sp.Expr]:
    """Derive a separate uniform moving-boundary law and its Gaussian regularization.

    U~Uniform(0,1), J(h,U)=1{U>=h}. This is an analytic quadrature bridge,
    not a calibrated replacement for the production working-set state law.
    """
    h = sp.Symbol("h", real=True)
    u = sp.Symbol("u", real=True)
    def primitive(z: sp.Expr) -> sp.Expr:
        """Integrate the normal CDF without introducing approximate constants."""
        return z * normal_cdf(z) + sp.exp(-z**2 / 2) / sp.sqrt(2 * sp.pi)
    cost = SIGMA * (primitive((1 - h) / SIGMA) - primitive(-h / SIGMA))
    gradient = -(normal_cdf(h / SIGMA) - normal_cdf((h - 1) / SIGMA))
    assert sp.simplify(sp.diff(cost, h) - gradient) == 0
    return {
        "integrand": normal_cdf((u - h) / SIGMA), "cost": cost,
        "gradient": gradient, "unregularized_interior_cost": 1 - h,
        "unregularized_interior_gradient": sp.Integer(-1),
    }
