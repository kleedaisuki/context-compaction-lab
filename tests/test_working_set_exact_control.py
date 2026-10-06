"""Maintain the small exact controls against the production simulator API."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def probe() -> dict:
    """Load the maintained experiment without invoking its artifact-writing main."""
    root = Path(__file__).resolve().parents[1]
    return runpy.run_path(str(root / "experiments/working_set_exact_control.py"))


def test_exact_endogenous_first_cycle(probe: dict) -> None:
    """Check the true path weights, failed independence shortcut, and carry identity."""
    paths, weights = probe["enumerate_demands"](8, 0.35)
    workload, field = probe["ordinary_fixture"](paths)
    result = probe["first_cycle_control"](workload, field, paths, weights, 0.35)
    assert len(paths) == 256
    assert weights.sum() == pytest.approx(1)
    assert result["expected_first_cycle_actions"] == pytest.approx(2.4225)
    assert result["actual_first_use_probability"] == pytest.approx(0.725375)
    assert result["actual_later_ordinary_carries"] == pytest.approx(0.35)
    assert result["plugin_probability_error"] == pytest.approx(-0.0853978125)


def test_recovery_request_batching_reverses_policy_order(probe: dict) -> None:
    """Actual four-price additional calls can overcome first-use residency savings."""
    result = probe["batching_counterexample"]()["results"]
    direct = result["no_recovery_round"]
    rounds = result["with_recovery_round"]
    assert direct["first_use"]["costs"] < direct["eager"]["costs"]
    assert rounds["eager"]["costs"] < rounds["first_use"]["costs"]
    assert rounds["eager"]["recovery_rounds"] == 2
    assert rounds["first_use"]["recovery_rounds"] == 3


def test_exact_optimum_is_an_interval_not_a_spurious_derivative(probe: dict) -> None:
    """Every integer threshold is covered and finite-horizon optimum has a flat tail."""
    paths, weights = probe["enumerate_demands"](8, 0.35)
    workload, field = probe["ordinary_fixture"](paths)
    result = probe["threshold_scan"](workload, field, weights)
    assert result["exhaustive_integer_upper"] == 299
    summary = result["summaries"]["first_use"]
    assert summary["optimal_integer_intervals"] == [[269, 299]]
    assert summary["optimal_tail_unbounded"]
    assert summary["upward_jumps"] > 0 and summary["downward_jumps"] > 0
