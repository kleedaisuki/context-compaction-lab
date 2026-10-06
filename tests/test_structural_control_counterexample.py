"""Protect the exact state-sufficiency counterexample and its production ledger."""

import sys
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


def load_experiment():
    """Load the maintained standalone experiment without packaging experiments."""
    path = Path(__file__).resolve().parents[1] / "experiments/structural_control_counterexample.py"
    spec = spec_from_file_location("structural_control_counterexample", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def experiment():
    """Share one loaded research module across ledger checks."""
    return load_experiment()


def test_opposite_optimal_actions_at_same_context(experiment):
    """No length-only action can optimize both valid and absent fact states."""
    assert experiment.expected_cost(True, "continue") == Fraction("0.0379215")
    assert experiment.expected_cost(False, "continue") == Fraction("0.0454215")
    assert experiment.expected_cost(True, "compact") == Fraction("0.0401805")
    assert experiment.expected_cost(False, "compact") == Fraction("0.0401805")
    assert experiment.expected_cost(True, "continue") < experiment.expected_cost(True, "compact")
    assert experiment.expected_cost(False, "compact") < experiment.expected_cost(False, "continue")


@pytest.mark.parametrize("resident", [True, False])
@pytest.mark.parametrize("action", ["continue", "compact"])
@pytest.mark.parametrize("required", [False, True])
def test_actual_simulator_branch_accounting(experiment, resident, action, required):
    """The production engine must agree in every disjoint invoice category."""
    experiment.production_check(resident, action, required)


def test_randomized_length_only_policy_cannot_remove_regret(experiment):
    """A mixture of two state-blind actions cannot beat its better endpoint."""
    result = experiment.exact_result()["equal_state_mixture"]
    assert result["exact_regret_usd"] == str(Fraction("0.0011295"))
    assert result["strict_length_only_regret_usd"] > 0


@pytest.mark.parametrize("resident", [True, False])
@pytest.mark.parametrize("action", ["continue", "compact"])
@pytest.mark.parametrize("required", [False, True])
def test_all_four_categories_active(experiment, resident, action, required):
    """The stronger variant charges all four categories on either action."""
    usage = experiment.branch_usage(resident, action, required, True)
    assert min(usage.input, usage.write, usage.read, usage.output) > 0
    experiment.production_check(resident, action, required, True)


def test_four_active_rates_still_require_opposite_actions(experiment):
    """Opposite choices do not rely on omitting the cache-read price."""
    assert experiment.expected_cost(True, "continue", True) == Fraction("0.0344715")
    assert experiment.expected_cost(True, "compact", True) == Fraction("0.0356055")
    assert experiment.expected_cost(False, "continue", True) == Fraction("0.0363465")
    assert experiment.expected_cost(False, "compact", True) == Fraction("0.0356055")


def test_exact_bellman_flow_certificate(experiment):
    """Feasible occupation and lower potentials meet at the restricted optimum."""
    certificate = experiment.bellman_certificate()
    assert certificate["exact_primal_value_usd"] == str(Fraction("0.039051"))
    assert certificate["exact_dual_value_usd"] == certificate["exact_primal_value_usd"]
    assert certificate["exact_best_threshold_value_usd"] == str(Fraction("0.0401805"))
    assert certificate["exact_threshold_gap_usd"] == str(Fraction("0.0011295"))
    assert certificate["exact_dual_inequality_slacks_usd"] == [
        "0", str(Fraction("0.002259")), str(Fraction("0.005241")), "0"
    ]
