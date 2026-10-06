"""Verify whole-task Gaussian responses and the controlled continuum bridge."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from context_compaction_lab.continuum_symbolics import (
    SIGMA,
    GaussianThresholdModel,
    gaussian_band_probabilities,
    uniform_continuum_expressions,
)
from context_compaction_lab.structural_symbolics import THRESHOLD


@pytest.fixture(scope="module")
def actual_model() -> GaussianThresholdModel:
    """Build the prior actual-engine curve afresh, without requiring a cache artifact."""
    root = Path(__file__).resolve().parents[1]
    prior = runpy.run_path(str(root / "experiments/working_set_exact_control.py"))
    extraction = runpy.run_path(str(root / "experiments/structural_symbolic_analysis.py"))
    paths, _ = prior["enumerate_demands"](8, 0.35)
    workload, field = prior["ordinary_fixture"](paths)
    curve = extraction["simulator_curve"](workload, prior["policies"]()["first_use"],
                                          field, paths)
    model = GaussianThresholdModel.from_curve(curve, (
        sp.Rational(3, 10**6), sp.Rational(3, 800000), sp.Rational(3, 10**6),
        sp.Rational(3, 200000)))
    replacements = {sp.Symbol("alpha", nonnegative=True): sp.Rational(7, 20)}
    return GaussianThresholdModel(model.base.subs(replacements), model.boundaries,
                                  tuple(jump.subs(replacements) for jump in model.jumps))


def test_erf_formula_and_gaussian_kernel_derivatives_match_exactly() -> None:
    """The continuous controller response has true symbolic first and second derivatives."""
    model = GaussianThresholdModel(sp.Integer(3), (1, 4), (sp.Integer(-1), sp.Rational(1, 2)))
    assert sp.simplify(sp.diff(model.symbolic_cost(), THRESHOLD)
                       - model.symbolic_gradient()) == 0
    assert sp.simplify(sp.diff(model.symbolic_gradient(), THRESHOLD)
                       - model.symbolic_curvature()) == 0
    assert not model.symbolic_gradient().has(sp.DiracDelta)


@pytest.mark.parametrize("sigma", [0.25, 1, 4, 12])
def test_actual_endogenous_curve_integral_and_jump_sum_agree(
    actual_model: GaussianThresholdModel, sigma: float,
) -> None:
    """Two independent Gaussian integrations preserve actual engine occupations."""
    grid = np.linspace(1, 320, 1001)
    values = actual_model.evaluate(grid, sigma, {})
    integral = actual_model.band_integral(grid, sigma, {})
    assert np.max(np.abs(integral - values["cost"])) < 2e-17
    jumps = np.array([float(jump) for jump in actual_model.jumps])
    cells = float(actual_model.base) + np.concatenate(([0], np.cumsum(jumps)))
    raw = cells[np.searchsorted(actual_model.boundaries, grid, side="left")]
    assert np.all(np.abs(values["cost"] - raw) <= values["local_error_bound"] + 2e-17)
    assert values["cost"].min() >= cells.min() - 2e-17


def test_clip_atom_at_one_and_nonvanishing_half_jump_error() -> None:
    """Clipping leaves the strict-exceedance formula valid even at the floor boundary."""
    model = GaussianThresholdModel(sp.Integer(2), (1,), (sp.Integer(1),))
    for sigma in (1, 0.1, 0.01):
        values = model.evaluate(1, sigma, {})
        assert values["cost"] == pytest.approx(2.5)
        assert values["local_error_bound"] == pytest.approx(0.5)
    assert model.band_integral(1, 0.1, {}) == pytest.approx(2.5)


def test_tail_cell_probabilities_are_stable_and_exhaustive() -> None:
    """Tiny intervals in the far positive-CDF tail must not be rounded to zero."""
    probabilities = gaussian_band_probabilities(np.array([0, 1]), -10, 1)
    assert probabilities[1] > 0
    assert probabilities.sum() == pytest.approx(1)
    assert np.all(probabilities >= 0)
    with pytest.raises(ValueError, match="strictly positive"):
        gaussian_band_probabilities(np.array([1]), 1, 0)


def test_derivative_and_bias_logs_do_not_mistake_underflow_for_zero() -> None:
    """An extremely flat controller response still carries nonzero signed sensitivity."""
    model = GaussianThresholdModel(sp.Integer(2), (1, 3), (sp.Integer(-1), sp.Integer(1)))
    assert model.evaluate(1.99, 0.01, {})["gradient"] == 0
    log_absolute, sign = model.derivative_log(1.99, 0.01, {})
    assert math.isfinite(log_absolute) and log_absolute < -1000 and sign < 0
    assert model.scaled_gradient(1.99, 0.01, {}) < 0
    assert math.isfinite(float(model.evaluate(1.99, 0.01, {})["log_local_error_bound"]))


def test_uniform_continuum_law_is_not_the_unsmoothed_step_derivative() -> None:
    """The moving-boundary expectation has a nonzero continuum derivative."""
    expressions = uniform_continuum_expressions()
    h = sp.Symbol("h", real=True)
    assert sp.simplify(sp.diff(expressions["cost"], h) - expressions["gradient"]) == 0
    assert sp.limit(expressions["gradient"].subs(h, sp.Rational(1, 2)), SIGMA, 0,
                    dir="+") == -1


def test_lattice_resolving_bandwidth_does_not_converge_in_gradient() -> None:
    """Cost convergence with persistent density peaks requires a genuine scale separation."""
    gradients = []
    for cells in (64, 1024):
        delta, sigma = 1 / cells, 1 / (8 * cells)
        locations = (np.arange(cells) + 0.5) * delta
        centers = np.array([0.5, 0.5 + delta / 2])
        z = (centers[:, None] - locations) / sigma
        gradients.append(-delta * np.sum(np.exp(-z**2 / 2), axis=-1)
                         / (sigma * math.sqrt(2 * math.pi)))
    assert np.allclose(gradients[0], gradients[1], atol=1e-14)
    assert gradients[1][0] == pytest.approx(-0.002141283612238166)
    assert gradients[1][1] == pytest.approx(-3.1915382432115424)


def test_continuum_envelope_gradient_bound_constants_exactly() -> None:
    """Verify the Gaussian norm constants and optimal bandwidth in root's bridge theorem."""
    x, epsilon, lipschitz = sp.symbols("x epsilon L", positive=True)
    density = sp.exp(-x**2 / (2 * SIGMA**2)) / (SIGMA * sp.sqrt(2 * sp.pi))
    derivative_norm = 2 * sp.integrate(x * density / SIGMA**2, (x, 0, sp.oo))
    first_moment = 2 * sp.integrate(x * density, (x, 0, sp.oo))
    assert sp.simplify(derivative_norm - sp.sqrt(2 / sp.pi) / SIGMA) == 0
    assert sp.simplify(first_moment - SIGMA * sp.sqrt(2 / sp.pi)) == 0
    bound = sp.sqrt(2 / sp.pi) * (epsilon / SIGMA + lipschitz * SIGMA)
    bandwidth = sp.sqrt(epsilon / lipschitz)
    assert sp.simplify(sp.diff(bound, SIGMA).subs(SIGMA, bandwidth)) == 0
    assert sp.simplify(bound.subs(SIGMA, bandwidth)
                       - 2 * sp.sqrt(2 / sp.pi) * sp.sqrt(epsilon * lipschitz)) == 0


def test_curve_loading_does_not_use_json_key_order_as_billing_semantics(tmp_path: Path) -> None:
    """Channel identities must survive serialized dictionary reordering."""
    root = Path(__file__).resolve().parents[1]
    probe = runpy.run_path(str(root / "experiments/continuum_threshold_analysis.py"))
    path = tmp_path / "reordered.json"
    source = {"curves": {"first_use": {"bands": [{
        "lower_exclusive": 0, "upper_inclusive": None,
        "occupation": {
            "output_tokens": {"polynomial": "4"},
            "read_tokens": {"polynomial": "3"},
            "write_tokens": {"polynomial": "2"},
            "input_tokens": {"polynomial": "1"},
        },
    }]}}}
    path.write_text(json.dumps(source), encoding="utf-8")
    assert probe["load_curve"](path).at(1).entries == (1, 2, 3, 4)
