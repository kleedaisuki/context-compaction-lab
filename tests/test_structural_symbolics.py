"""Validate exact structural algebra and its extraction from the actual engine."""

from __future__ import annotations

import itertools
import runpy
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from context_compaction_lab.structural_symbolics import (
    ALPHA,
    PRICES,
    THRESHOLD,
    OccupationVector,
    ThresholdBand,
    ThresholdCurve,
    bernoulli_occupation,
    bernoulli_polynomial,
    bernstein_coefficients,
    exact_integer_values,
    read_write_crossover,
)
from context_compaction_lab.working_set_simulation import simulate_working_set


@pytest.fixture(scope="module")
def actual_fixture() -> tuple:
    """Reuse the existing working-set extraction basis without running its main."""
    path = Path(__file__).resolve().parents[1] / "experiments/working_set_exact_control.py"
    probe = runpy.run_path(str(path))
    paths, _ = probe["enumerate_demands"](8, 0.35)
    workload, field = probe["ordinary_fixture"](paths)
    return paths, workload, field, probe["policies"]()


def test_exact_cube_lifting_includes_multiplicities_once() -> None:
    """Power coefficients recover a complete weighted cube, not a binomial double count."""
    paths = np.array(list(itertools.product((False, True), repeat=3)), dtype=bool)
    reward = paths.sum(axis=1)
    assert bernoulli_polynomial(paths, reward) == 3 * ALPHA
    assert bernstein_coefficients(3 * ALPHA, 3) == (0, 1, 2, 3)
    with pytest.raises(ValueError, match="exactly once"):
        bernoulli_polynomial(paths[:-1], reward[:-1])
    with pytest.raises(ValueError, match="exactly once"):
        bernoulli_polynomial(np.zeros_like(paths), reward)


@pytest.mark.parametrize("values", [np.array([1.5]), np.array([float(2**53)]),
                                    np.array([np.nan]), np.array([-1])])
def test_exact_lifting_does_not_round_or_rational_fit(values: np.ndarray) -> None:
    """A float or unsafe ledger must not become an apparently exact polynomial."""
    with pytest.raises(ValueError, match="exact nonnegative integers"):
        exact_integer_values(values)


def test_actual_endogenous_price_and_demand_polynomial(actual_fixture: tuple) -> None:
    """The production engine's physical stopping law has exact degree-four cost here."""
    paths, workload, field, policy_map = actual_fixture
    result = simulate_working_set(workload, policy_map["first_use"], 100, field)
    occupation = bernoulli_occupation(paths, result)
    expected = OccupationVector((
        58, 320 + 208 * ALPHA - 78 * ALPHA**2 - 52 * ALPHA**3 + 26 * ALPHA**4,
        578 + 156 * ALPHA - 26 * ALPHA**2, 104,
    ))
    assert occupation == expected
    assert tuple(sp.diff(occupation.cost(), price) for price in PRICES) == occupation.entries
    assert sp.hessian(occupation.cost(), PRICES) == sp.zeros(4)
    prices = (sp.Rational(3, 10**6), sp.Rational(3, 800000),
              sp.Rational(3, 10**7), sp.Rational(3, 200000))
    cost = occupation.cost(prices)
    assert cost.subs(ALPHA, sp.Rational(7, 20)) == sp.Rational(214598127, 64000000000)
    assert sp.diff(cost, ALPHA).subs(ALPHA, sp.Rational(7, 20)) == sp.Rational(449319,
                                                                                         800000000)
    failed = replace(result, loop_failures=np.ones(len(paths), dtype=np.int64))
    with pytest.raises(ValueError, match="failed policy"):
        bernoulli_occupation(paths, failed)


def test_exact_price_comparison_hyperplane(actual_fixture: tuple) -> None:
    """Stable-prefix advantage is controlled by a price ratio, independent of alpha here."""
    paths, workload, field, policy_map = actual_fixture
    lazy = bernoulli_occupation(paths, simulate_working_set(workload, policy_map["first_use"],
                                                          100, field))
    stable = bernoulli_occupation(paths, simulate_working_set(
        workload, policy_map["stable_first_use"], 100, field))
    assert stable.difference(lazy).cost() == 96 * (PRICES[2] - PRICES[1])


def test_exact_threshold_crossover_has_certified_direction(actual_fixture: tuple) -> None:
    """A rational hyperplane root is supported by negative read-occupation coefficients."""
    paths, workload, field, policy_map = actual_fixture
    earlier = bernoulli_occupation(paths, simulate_working_set(
        workload, policy_map["first_use"], 157, field))
    never = bernoulli_occupation(paths, simulate_working_set(
        workload, policy_map["first_use"], 269, field))
    delta = earlier.difference(never)
    assert all(value < 0 for value in bernstein_coefficients(delta.entries[2], 8))
    crossover = read_write_crossover(delta, sp.Rational(4, 5), sp.Integer(4))
    assert crossover.subs(ALPHA, sp.Rational(7, 20)) == sp.Rational(588316516163,
                                                                 2286290402180)
    assert sp.cancel(delta.cost((sp.Rational(4, 5), 1, crossover, 4))) == 0


def test_threshold_boundaries_and_distributional_not_smooth_derivative() -> None:
    """Elementary cells verify the algebraic representation, not another simulator."""
    first = OccupationVector((1, 2, 3, 4))
    second = OccupationVector((1, 2, 5, 4))
    curve = ThresholdCurve((ThresholdBand(0, 2, first), ThresholdBand(2, None, second)))
    assert curve.at(2) == first
    assert curve.at(sp.Rational(5, 2)) == second
    assert sp.diff(curve.piecewise_cost(), THRESHOLD) == 0
    assert curve.distributional_derivative() == 2 * PRICES[2] * sp.DiracDelta(THRESHOLD - 2)
    assert second.cost() - first.cost() == 2 * PRICES[2]
    with pytest.raises(ValueError, match="gaps or overlaps"):
        ThresholdCurve((ThresholdBand(0, 2, first), ThresholdBand(3, None, second)))
    with pytest.raises(ValueError, match="floating"):
        OccupationVector((sp.Float(1.0), 2, 3, 4))
