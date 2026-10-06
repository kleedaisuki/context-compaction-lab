"""Independent tiny ledgers derived from docs/working-set-contract.md."""

from dataclasses import replace

import numpy as np
import pytest

from context_compaction_lab.config import Pricing
from context_compaction_lab.working_set_config import (
    ActionField,
    ArtifactSpec,
    WorkingSetPolicy,
    WorkingSetWorkload,
)
from context_compaction_lab.working_set_inference import sweep_working_sets
from context_compaction_lab.working_set_simulation import simulate_working_set
from context_compaction_lab.working_set_workloads import DemandSpec


def scenario(calls=2, artifacts=(ArtifactSpec("unused", 0),), **changes):
    """Create small integral token counts with distinct category prices."""
    values = dict(
        calls=calls, artifacts=artifacts, base_tokens=10, summary_tokens=2,
        pricing=Pricing(1, 2, 3, 4), minimum_cache_tokens=1,
        normal_uncached_tokens=1, compaction_instruction_tokens=2,
        file_wrapper_tokens=1, recovery_command_tokens=3,
        recovery_instruction_tokens=2, cache_ttl_seconds=5,
    )
    values.update(changes)
    return WorkingSetWorkload(**values)


def actions(background, output=None, required=None, observed=None, mutations=None, gaps=None,
            artifacts=1):
    """Build a single trajectory without encoding simulator state transitions."""
    n = len(background)
    flags = np.zeros((1, n, artifacts), dtype=bool)
    return ActionField(
        background_input=np.array([background]),
        output_tokens=np.array([output if output is not None else [0] * n]),
        gaps=np.array([gaps if gaps is not None else [0] * n], dtype=float),
        required=flags.copy() if required is None else np.array([required], dtype=bool),
        observed=flags.copy() if observed is None else np.array([observed], dtype=bool),
        mutations=flags.copy() if mutations is None else np.array([mutations], dtype=bool),
    )


def ledger(result, inputs, writes, reads, outputs, compactions=0):
    """Assert hand-counted disjoint tokens and independently priced total."""
    expected = dict(input_tokens=inputs, write_tokens=writes, read_tokens=reads,
                    output_tokens=outputs, compactions=compactions)
    for name, count in expected.items():
        assert getattr(result, name).tolist() == [count], name
    assert result.costs.tolist() == [inputs + 2 * writes + 3 * reads + 4 * outputs]


def test_cold_single_call_has_no_terminal_compaction():
    """Crossing h on the last output must not add an unused summary call."""
    result = simulate_working_set(scenario(calls=1), WorkingSetPolicy(), 16,
                                  actions([3], [4]))
    ledger(result, 1, 13, 0, 4)
    assert result.completed_actions.tolist() == [1]


def test_warm_unchanged_prefix_and_generated_tail():
    """Only earlier request input is warm; prior generated output is newly written."""
    result = simulate_working_set(scenario(warm_start=True), WorkingSetPolicy(), np.inf,
                                  actions([3, 1], [4, 2]))
    ledger(result, 2, 8, 23, 6)


def test_compactor_reads_old_prefix_and_bills_uncached_tail():
    """Old 17-token context has 13 warm tokens and four uncached output tokens."""
    policy = WorkingSetPolicy(surviving_base_tokens=10)
    result = simulate_working_set(scenario(warm_start=True), policy, 17,
                                  actions([3, 1], [4, 2]))
    ledger(result, 8, 6, 33, 8, compactions=1)
    assert result.base_cache_read_tokens.tolist() == [30]
    assert result.max_context.tolist() == [17]


def test_generated_recovery_round_reads_full_context_not_just_command():
    """Recovery writes base, generates three tokens, then appends six tool tokens."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5),))
    result = simulate_working_set(workload, WorkingSetPolicy(recovery_model_round=True),
                                  np.inf, actions([0], required=[[True]], artifacts=1))
    ledger(result, 3, 19, 10, 3)
    assert result.recovery_rounds.tolist() == [1]
    assert result.reload_tokens.tolist() == [6]


def test_file_payload_is_input_not_generated_output():
    """A missing five-token file plus wrapper costs six input-write tokens only."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5),))
    result = simulate_working_set(workload, WorkingSetPolicy(), np.inf,
                                  actions([0], required=[[True]], artifacts=1))
    ledger(result, 1, 16, 0, 0)
    assert result.reload_events.tolist() == [1]


def test_expired_stable_prefix_cannot_resurrect_during_compaction():
    """Gap six exceeds TTL five; old context and rebuilt base are both cold."""
    result = simulate_working_set(scenario(warm_start=True),
                                  WorkingSetPolicy(surviving_base_tokens=10), 17,
                                  actions([3, 1], [4, 2], gaps=[0, 6]))
    ledger(result, 21, 16, 10, 8, compactions=1)


def test_mutation_invalidates_availability_not_old_context_billing():
    """Old six-token observation remains warm history; new version adds six more."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    result = simulate_working_set(workload, WorkingSetPolicy(), np.inf,
                                  actions([0, 0], required=[[True], [True]],
                                          mutations=[[False], [True]], artifacts=1))
    ledger(result, 2, 22, 16, 0)
    assert result.reload_events.tolist() == [2]
    assert result.max_context.tolist() == [22]


@pytest.mark.parametrize("preserve_guard, reloads, writes", [(True, 1, 24), (False, 2, 30)])
def test_visible_preservation_and_read_guard_are_separate(preserve_guard, reloads, writes):
    """Reset retains six tool tokens; clearing guard still forces a fresh read."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    policy = WorkingSetPolicy(preserve_recent_tokens=6, preserve_read_guards=preserve_guard,
                              surviving_base_tokens=10)
    result = simulate_working_set(workload, policy, 16,
                                  actions([0, 0], required=[[True], [True]], artifacts=1))
    # Cold action writes 16; compact reads 16; rebuilt request reads base 10.
    ledger(result, 4, writes, 26, 2, compactions=1)
    assert result.reload_events.tolist() == [reloads]
    assert result.retained_file_tokens.tolist() == [6]


def test_eager_restores_unused_catalog_while_first_use_does_not():
    """With no required files, eager restores both files after reset, first-use neither."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5), ArtifactSpec("b", 7)))
    field = actions([0], artifacts=2)
    lazy = simulate_working_set(workload, WorkingSetPolicy(), 10, field)
    eager = simulate_working_set(workload, WorkingSetPolicy(restoration="eager"), 10, field)
    ledger(lazy, 13, 12, 0, 2, compactions=1)
    ledger(eager, 13, 26, 0, 2, compactions=1)
    assert lazy.reload_tokens.tolist() == [0]
    assert eager.reload_tokens.tolist() == [14]


def test_ordinary_observation_satisfies_next_action_without_reload():
    """Automatic tool result is appended after action one, not billed output."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    field = actions([0, 0], required=[[False], [True]], observed=[[True], [False]],
                    artifacts=1)
    result = simulate_working_set(workload, WorkingSetPolicy(), np.inf, field)
    ledger(result, 2, 16, 10, 0)
    assert result.reload_events.tolist() == [0]


def test_precondition_read_and_postaction_observation_are_distinct_events():
    """A required prerequisite and declared later tool result both occupy history."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    result = simulate_working_set(workload, WorkingSetPolicy(), np.inf,
                                  actions([0, 0], required=[[True], [True]],
                                          observed=[[True], [False]], artifacts=1))
    ledger(result, 2, 22, 16, 0)
    assert result.max_context.tolist() == [22]
    assert result.reload_events.tolist() == [1]


def test_strict_reset_read_loop_is_failure_but_atomic_completes():
    """h=16 always crossed by reset base+summary+required file=18."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5),),
                        max_compactions_per_action=2)
    field = actions([0], required=[[True]], artifacts=1)
    atomic = simulate_working_set(workload, WorkingSetPolicy(), 16, field)
    strict = simulate_working_set(workload, replace(WorkingSetPolicy(), trigger="strict"),
                                  16, field)
    ledger(atomic, 1, 16, 0, 0)
    assert atomic.completed_actions.tolist() == [1]
    assert atomic.loop_failures.tolist() == [0]
    assert strict.completed_actions.tolist() == [0]
    assert strict.loop_failures.tolist() == [1]
    assert strict.compactions.tolist() == [2]


def test_oversized_stable_prefix_declaration_is_rejected():
    """An old file tail cannot masquerade as unchanged stable base cache."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    with pytest.raises(ValueError, match="base"):
        simulate_working_set(workload, WorkingSetPolicy(surviving_base_tokens=20), 16,
                             actions([0, 0], required=[[True], [True]], artifacts=1))


def test_nonzero_stable_boundary_below_cache_minimum_is_rejected():
    """A partial boundary below provider eligibility cannot be declared warm."""
    with pytest.raises(ValueError, match="minimum"):
        simulate_working_set(scenario(minimum_cache_tokens=8),
                             WorkingSetPolicy(surviving_base_tokens=5), 17,
                             actions([3, 1], [4, 2]))


@pytest.mark.parametrize("delay, reads, writes", [(5, 10, 19), (6, 0, 29)])
def test_recovery_delay_expires_new_recovery_prefix(delay, reads, writes):
    """Exactly TTL preserves the recovery cache; longer tool delay destroys it."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5),),
                        recovery_delay_seconds=delay)
    result = simulate_working_set(workload, WorkingSetPolicy(recovery_model_round=True),
                                  np.inf, actions([0], required=[[True]], artifacts=1))
    ledger(result, 3, writes, reads, 3)


def test_multi_trajectory_strict_failure_does_not_corrupt_successful_neighbor():
    """One trajectory loops on a required file while its file-free neighbor completes."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5),),
                        max_compactions_per_action=2)
    field = ActionField(np.array([[0], [0]]), np.array([[0], [0]]),
                        np.array([[0.0], [0.0]]),
                        required=np.array([[[True]], [[False]]]))
    result = simulate_working_set(workload, WorkingSetPolicy(trigger="strict"), 16, field)
    assert result.completed_actions.tolist() == [0, 1]
    assert result.loop_failures.tolist() == [1, 0]
    assert result.costs[1] == 21
    assert result.compactions.tolist() == [2, 0]
    assert field.required.tolist() == [[[True]], [[False]]]


def test_two_missing_files_use_one_batched_recovery_command():
    """Two missing payloads add fourteen input tokens but only one command output."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5), ArtifactSpec("b", 7)))
    result = simulate_working_set(workload, WorkingSetPolicy(recovery_model_round=True),
                                  np.inf, actions([0], required=[[True, True]], artifacts=2))
    ledger(result, 3, 27, 10, 3)
    assert result.reload_events.tolist() == result.recovery_rounds.tolist() == [1]
    assert result.reload_tokens.tolist() == [14]


def test_mutated_obsolete_snapshot_cannot_be_preserved():
    """Mutation before reset invalidates retention even when its budget fits old text."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    policy = WorkingSetPolicy(preserve_recent_tokens=6, preserve_read_guards=True,
                              surviving_base_tokens=10)
    field = actions([0, 0], required=[[True], [True]],
                    mutations=[[False], [True]], artifacts=1)
    result = simulate_working_set(workload, policy, 16, field)
    ledger(result, 4, 24, 26, 2, compactions=1)
    assert result.retained_file_tokens.tolist() == [0]
    assert result.reload_tokens.tolist() == [12]


def test_payload_without_guard_requirement_survives_guard_clearing():
    """Cleared guards do not trigger a read for facts whose contract requires none."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5, requires_read_guard=False),))
    policy = WorkingSetPolicy(preserve_recent_tokens=6, preserve_read_guards=False,
                              surviving_base_tokens=10)
    result = simulate_working_set(workload, policy, 16,
                                  actions([0, 0], required=[[True], [True]], artifacts=1))
    ledger(result, 4, 24, 26, 2, compactions=1)
    assert result.reload_events.tolist() == [1]


def test_inference_rejects_partial_invoices_and_can_select_no_compaction():
    """A strict loop is null, not cheap; an equal baseline beats finite-grid ties."""
    workload = scenario(calls=1, artifacts=(ArtifactSpec("a", 5),),
                        max_compactions_per_action=2)
    demand = DemandSpec(mode="mandatory", mutation_probability=0,
                        background_input_tokens=0, gap_mean_seconds=1, gap_cv=1)
    report, _ = sweep_working_sets(
        workload, demand, {"strict": WorkingSetPolicy(trigger="strict")},
        [16, 24], 2, 41, np.array([0]), np.array([0]), 1, difference_step=1,
    )
    policy = report["policies"]["strict"]
    failed, complete = policy["rows"]
    assert failed["failure_share"] == 1
    assert failed["expected_cost_usd"] is None
    assert failed["paired_secant_usd_per_token"] is None
    assert complete["expected_cost_usd"]["mean"] == 33
    assert policy["selected_mode"] == "no_compaction"
    assert policy["selected_threshold_tokens"] is None
    assert policy["confirmation"]["selected"]["diagnostics"]["compactions"] == 0


def test_inference_preserves_fixed_ordinary_output_across_policy_families():
    """Each complete trajectory generates eight ordinary tokens despite extra calls."""
    workload = scenario(artifacts=(ArtifactSpec("a", 5),))
    demand = DemandSpec(mode="mandatory", mutation_probability=0,
                        background_input_tokens=0, gap_mean_seconds=1, gap_cv=1)
    report, _ = sweep_working_sets(
        workload, demand, {"atomic": WorkingSetPolicy(),
                           "command": WorkingSetPolicy(recovery_model_round=True)},
        [16, 30], 2, 41, np.array([4]), np.array([0]), 1, difference_step=1,
    )
    prices = {"input_tokens": 1, "write_tokens": 2, "read_tokens": 3, "output_tokens": 4}
    for policy in report["policies"].values():
        for row in policy["rows"] + [policy["no_compaction"]]:
            diagnostic = row["diagnostics"]
            assert diagnostic["completed_actions"] == 2
            ordinary = (diagnostic["output_tokens"] - 2 * diagnostic["compactions"]
                        - 3 * diagnostic["recovery_rounds"])
            assert ordinary == 8
            invoice = sum(diagnostic[name] * price for name, price in prices.items())
            assert row["expected_cost_usd"]["mean"] == invoice
