"""Protect the new research controls without changing production policy semantics."""

import importlib.util
from pathlib import Path

import pytest


def load_probe():
    """Load the maintained research script without depending on an ad-hoc sys.path."""
    path = Path(__file__).resolve().parents[1] / "experiments/first_use_reload_probe.py"
    spec = importlib.util.spec_from_file_location("first_use_reload_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_first_use_cost_prices_writes_and_subsequent_carries() -> None:
    """The single-file cycle cost is not merely size times a reuse probability."""
    module = load_probe()
    assert module.expected_file_cost(20, .08, 12_000, 3.75e-6, .30e-6, .30e-6) == (
        pytest.approx(.07492070401501393)
    )


def test_symbolic_relaxation_has_explicit_non_threshold_scope() -> None:
    """A verified duration derivative must not be relabeled an endogenous h-gradient."""
    result = load_probe().symbolic_rate()
    assert "verified_derivative_wrt_m" in result
    assert "restoration alters crossing" in result["not_claimed"]


def test_threshold_dependency_invalidates_independent_pgf() -> None:
    """Exhaustive first-use branches give .75, not the independent-T shortcut .625."""
    result = load_probe().probe(replicates=128)["endogenous_threshold_counterexample"]
    assert result["actual_probability_used_before_crossing"] == .75
    assert result["incorrect_independent_T_prediction"] == .625
    assert result["compensator_carry_identity"] == 0
