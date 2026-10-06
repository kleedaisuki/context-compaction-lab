"""Prove a same-length opposite-control example with rational four-rate invoices.

The public working-set simulator checks every conditional branch. Its two
reachable histories differ in valid file residency, not in current length,
prefix warmth, remaining task count, or the unrevealed next-demand law.
Run ``uv run python experiments/structural_control_counterexample.py``.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Literal

import numpy as np

from context_compaction_lab.config import Pricing
from context_compaction_lab.working_set_config import (
    ActionField,
    ArtifactSpec,
    WorkingSetPolicy,
    WorkingSetWorkload,
)
from context_compaction_lab.working_set_simulation import simulate_working_set

Action = Literal["continue", "compact"]


@dataclass(frozen=True)
class Usage:
    """Disjoint input, write, read and generated-output token counts."""

    input: int = 0
    write: int = 0
    read: int = 0
    output: int = 0

    def cost(self) -> Fraction:
        """Return exact USD at the project's declared four synthetic rates."""
        return (
            3 * self.input + Fraction(15, 4) * self.write
            + Fraction(3, 10) * self.read + 15 * self.output
        ) / 1_000_000


def branch_usage(
    resident: bool, action: Action, required: bool, read_active: bool = False
) -> Usage:
    """Derive the remaining-action ledger before averaging unrevealed demand.

    Both states have 10,000 tokens and no live cache entry. A valid 4,000-token
    file is present only when resident=True. Reset erases the file observation,
    generates 100 summary tokens, and writes no obsolete context. Required
    payload is restored once before the ordinary request, not generated output.
    The read_active variant uses a 1k live/stable prefix and a 1k file; every
    invoice category is then positive, while the same structural reversal holds.
    """
    compact = action == "compact"
    prefix, base, payload = (1000, 1000, 1000) if read_active else (0, 0, 4000)
    load = payload if required and (compact or not resident) else 0
    return Usage(
        input=128 + (10_000 - prefix + 128 if compact else 0),
        write=(base + 100 if compact else 10_000 - prefix) + load + 2,
        read=prefix,
        output=2 + (100 if compact else 0),
    )


def expected_cost(resident: bool, action: Action, read_active: bool = False) -> Fraction:
    """Average two branches; action cannot condition on the future demand mark."""
    return sum(
        (
            branch_usage(resident, action, required, read_active).cost() / 2
            for required in (False, True)
        ),
        Fraction(0),
    )


def production_check(
    resident: bool, action: Action, required: bool, read_active: bool = False
) -> dict[str, float]:
    """Reach both states through ordinary public APIs and compare each token class.

    The first action appends 4k file + 6k background when resident, or 10k
    background otherwise. Both first invoices and resulting lengths coincide.
    A second-action gap exceeds TTL, making both prefixes cold. A threshold of
    10k compacts only at the second boundary; infinity always continues.
    With read_active=True, the initial warm base is 1k and first outputs are
    8k/9k, with an automatic 1k file observation only in the valid history.
    Prefix remains 1k, there is no expiry, and the respective sunk invoices
    are subtracted rather than incorrectly assumed equal.
    """
    base, payload = (1000, 1000) if read_active else (0, 4000)
    first_input = 0 if read_active else (6000 if resident else 10_000)
    first_output = (8000 if resident else 9000) if read_active else 0
    workload = WorkingSetWorkload(
        artifacts=(ArtifactSpec("current-file", payload),),
        base_tokens=base, summary_tokens=100, calls=2,
        pricing=Pricing(), minimum_cache_tokens=1, cache_ttl_seconds=0.5,
        normal_uncached_tokens=128, compaction_instruction_tokens=128,
        file_wrapper_tokens=0, warm_start=read_active,
    )
    field = ActionField(
        background_input=np.array([[first_input, 2]], dtype=np.int64),
        output_tokens=np.array([[first_output, 2]], dtype=np.int64),
        gaps=np.array([[0.0, 0.0 if read_active else 1.0]]),
        required=np.array([[[resident and not read_active], [required]]], dtype=bool),
        observed=np.array([[[resident and read_active], [False]]], dtype=bool),
    )
    result = simulate_working_set(
        workload, WorkingSetPolicy(), 10_000 if action == "compact" else math.inf, field
    )
    prefix_usage = (
        Usage(input=128, read=1000, output=first_output)
        if read_active else Usage(input=128, write=10_000)
    )
    expected = branch_usage(resident, action, required, read_active)
    actual = {}
    for name in ("input", "write", "read", "output"):
        observed = float(getattr(result, name + "_tokens")[0]) - getattr(prefix_usage, name)
        assert observed == getattr(expected, name), (name, observed, expected)
        actual[name + "_tokens"] = observed
    assert result.completed_actions[0] == 2
    assert result.loop_failures[0] == 0
    assert result.compactions[0] == (action == "compact")
    remaining_cost = float(result.costs[0]) - float(prefix_usage.cost())
    assert math.isclose(remaining_cost, float(expected.cost()), abs_tol=1e-14)
    actual["remaining_cost_usd"] = remaining_cost
    return actual


def bellman_certificate() -> dict[str, object]:
    """Certify the known-state one-stage mixture, not unrestricted two-step control.

    Occupation columns are A-continue, A-compact, B-continue, B-compact. The
    two flow rows require each observable initial state to have mass one half.
    Dual potentials are that state's exact minimum invoice. All inequalities
    and primal-dual equality are verified with rational arithmetic.
    """
    costs = tuple(
        expected_cost(resident, action)
        for resident in (True, False) for action in ("continue", "compact")
    )
    potentials = (costs[0], costs[3])
    slacks = tuple(cost - potentials[n // 2] for n, cost in enumerate(costs))
    assert min(slacks) >= 0
    occupations = (Fraction(1, 2), Fraction(0), Fraction(0), Fraction(1, 2))
    optimum = sum((mu * cost for mu, cost in zip(occupations, costs, strict=True)), Fraction(0))
    dual_bound = sum(potentials, Fraction(0)) / 2
    assert optimum == dual_bound
    threshold = min((costs[0] + costs[2]) / 2, (costs[1] + costs[3]) / 2)
    gap = threshold - optimum
    return {
        "scope": "One remaining action; observed A/B mixture; fixed first-use reset semantics",
        "occupation_columns": ["A-continue", "A-compact", "B-continue", "B-compact"],
        "flow_matrix": [[1, 1, 0, 0], [0, 0, 1, 1]],
        "flow_rhs": ["1/2", "1/2"],
        "exact_action_cost_vector_usd": [str(cost) for cost in costs],
        "exact_dual_state_potentials_usd": [str(value) for value in potentials],
        "exact_dual_inequality_slacks_usd": [str(value) for value in slacks],
        "exact_optimal_occupation_vector": [str(value) for value in occupations],
        "exact_primal_value_usd": str(optimum),
        "exact_dual_value_usd": str(dual_bound),
        "exact_best_threshold_value_usd": str(threshold),
        "exact_threshold_gap_usd": str(gap),
        "threshold_gap_percent_of_threshold_invoice": float(100 * gap / threshold),
        "opposite_action_price_coefficients_I_W_R_O": {
            "Delta_A_positive": [10128, -7900, 0, 100],
            "Delta_B_negative": [10128, -9900, 0, 100],
            "four_active_Delta_A_positive": [9128, -7400, 0, 100],
            "four_active_Delta_B_negative": [9128, -7900, 0, 100],
        },
    }


def exact_result() -> dict[str, object]:
    """Return checkable opposite decisions and unavoidable state-blind regret."""
    states = {}
    for name, resident in (("valid_file", True), ("missing_file", False)):
        costs = {action: expected_cost(resident, action) for action in ("continue", "compact")}
        optimum = min(costs, key=costs.get)
        states[name] = {
            "context_tokens": 10_000, "cached_prefix_tokens": 0,
            "valid_file": resident, "remaining_ordinary_actions": 1,
            "next_requirement_probability": "1/2", "optimal_action": optimum,
            "costs_usd": {action: float(cost) for action, cost in costs.items()},
            "exact_costs_usd": {action: str(cost) for action, cost in costs.items()},
        }
    aware = (expected_cost(True, "continue") + expected_cost(False, "compact")) / 2
    compact_all = (expected_cost(True, "compact") + expected_cost(False, "compact")) / 2
    continue_all = (expected_cost(True, "continue") + expected_cost(False, "continue")) / 2
    return {
        "bellman_flow_certificate": bellman_certificate(),
        "states": states,
        "equal_state_mixture": {
            "state_aware_optimum_usd": float(aware),
            "best_length_only_usd": float(min(compact_all, continue_all)),
            "strict_length_only_regret_usd": float(min(compact_all, continue_all) - aware),
            "exact_regret_usd": str(min(compact_all, continue_all) - aware),
        },
        "all_four_categories_active": {
            "cached_prefix_tokens": 1000, "payload_tokens": 1000,
            "valid_file_continue_usd": float(expected_cost(True, "continue", True)),
            "valid_file_compact_usd": float(expected_cost(True, "compact", True)),
            "missing_file_continue_usd": float(expected_cost(False, "continue", True)),
            "missing_file_compact_usd": float(expected_cost(False, "compact", True)),
            "production_branches": {
                f"resident={resident},action={action},required={required}":
                    production_check(resident, action, required, True)
                for resident in (True, False)
                for action in ("continue", "compact")
                for required in (False, True)
            },
        },
        "production_branches": {
            f"resident={resident},action={action},required={required}":
                production_check(resident, action, required)
            for resident in (True, False)
            for action in ("continue", "compact")
            for required in (False, True)
        },
    }


def main() -> None:
    """Write regenerated evidence inside the repository cache and print its result."""
    result = exact_result()
    directory = Path(".cache/structural-control")
    directory.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2)
    (directory / "counterexample.json").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
