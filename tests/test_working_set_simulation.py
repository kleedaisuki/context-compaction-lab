"""Deterministic version, restoration, and billing contracts for working sets."""

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
from context_compaction_lab.working_set_simulation import simulate_working_set


def workload(**changes):
    """Expose category drift with distinct USD-per-token rates."""
    values = dict(
        artifacts=(ArtifactSpec("a", 5),),
        calls=2,
        base_tokens=10,
        summary_tokens=3,
        pricing=Pricing(1, 2, 3, 4),
        minimum_cache_tokens=1,
        file_wrapper_tokens=1,
        normal_uncached_tokens=1,
        compaction_instruction_tokens=2,
        recovery_instruction_tokens=2,
        recovery_command_tokens=4,
        cache_ttl_seconds=5,
    )
    values.update(changes)
    return WorkingSetWorkload(**values)


def marks(
    required=None,
    *,
    calls=2,
    count=1,
    files=1,
    background=1,
    output=2,
    mutations=None,
    observed=None,
    gaps=None,
):
    """Build paired deterministic action-index marks with optional version changes."""
    shape = (count, calls)
    if required is None:
        required = np.ones((*shape, files), dtype=bool)
    return ActionField(
        np.full(shape, background),
        np.full(shape, output),
        np.zeros(shape) if gaps is None else gaps,
        required=required,
        mutations=mutations,
        observed=observed,
    )


def ledger(result, inputs, writes, reads, outputs):
    """Check disjoint token counts and the exact implied invoice."""
    assert result.input_tokens[0] == inputs
    assert result.write_tokens[0] == writes
    assert result.read_tokens[0] == reads
    assert result.output_tokens[0] == outputs
    assert result.costs[0] == inputs + 2 * writes + 3 * reads + 4 * outputs


def test_cold_and_warm_outputs_cache_only_next_request():
    """The first reload and generated tails are written only as future input."""
    cold = simulate_working_set(workload(), WorkingSetPolicy(), np.inf, marks())
    ledger(cold, 2, 20, 17, 4)
    assert cold.reload_events[0] == 1
    assert cold.reload_tokens[0] == 6
    assert cold.reload_payload_tokens[0] == 5
    assert cold.context_area[0] == 37
    assert cold.max_context[0] == 22
    warm = simulate_working_set(workload(warm_start=True), WorkingSetPolicy(), np.inf, marks())
    ledger(warm, 2, 10, 27, 4)
    assert warm.base_cache_read_tokens[0] == 20


def test_mutation_invalidates_semantics_not_old_text():
    """New versions append alongside stale snapshots until a real reset."""
    changes = np.array([[[False], [True]]])
    result = simulate_working_set(workload(), WorkingSetPolicy(), np.inf, marks(mutations=changes))
    ledger(result, 2, 26, 17, 4)
    assert result.reload_tokens[0] == 12
    assert result.max_context[0] == 28


def test_compaction_and_surviving_stable_prefix():
    """Compactor input is uncached except a genuinely warm old prefix."""
    policy = WorkingSetPolicy()
    cold = simulate_working_set(workload(), policy, 18, marks())
    ledger(cold, 6, 37, 17, 7)
    assert cold.compactions[0] == 1
    warm = simulate_working_set(workload(), replace(policy, surviving_base_tokens=10), 18, marks())
    ledger(warm, 6, 27, 27, 7)
    assert warm.compactions[0] == 1


def test_retained_content_and_read_guards_are_independent():
    """A retained visible snapshot can still require an additional qualifying read."""
    policy = WorkingSetPolicy(preserve_recent_tokens=6)
    reread = simulate_working_set(workload(), policy, 18, marks())
    guarded = simulate_working_set(
        workload(), replace(policy, preserve_read_guards=True), 18, marks()
    )
    assert reread.retained_file_tokens[0] == guarded.retained_file_tokens[0] == 6
    assert reread.reload_tokens[0] == 12
    assert guarded.reload_tokens[0] == 6
    assert reread.max_context[0] == 28
    assert guarded.max_context[0] == 22


def test_unguarded_retained_file_needs_no_extra_read():
    """Semantic residency suffices when the artifact has no read-before-edit guard."""
    work = workload(artifacts=(ArtifactSpec("a", 5, False),))
    result = simulate_working_set(work, WorkingSetPolicy(preserve_recent_tokens=6), 18, marks())
    assert result.reload_events[0] == 1


def test_recovery_round_full_invoice_and_expiring_delay():
    """Recovery writes its pre-output prefix; appended files do not retroactively cache."""
    policy = WorkingSetPolicy(recovery_model_round=True)
    result = simulate_working_set(workload(), policy, np.inf, marks())
    ledger(result, 4, 24, 31, 8)
    assert result.recovery_rounds[0] == 1
    expired = simulate_working_set(workload(recovery_delay_seconds=6), policy, np.inf, marks())
    ledger(expired, 4, 34, 21, 8)


def test_eager_batch_loads_whole_catalog_once():
    """One extra model round covers multiple required or proactively loaded files."""
    work = workload(artifacts=(ArtifactSpec("a", 5), ArtifactSpec("b", 7)))
    required = np.array([[[True, False], [False, False]]])
    result = simulate_working_set(
        work,
        WorkingSetPolicy(restoration="eager", recovery_model_round=True),
        np.inf,
        marks(required, files=2),
    )
    assert result.reload_events[0] == result.recovery_rounds[0] == 1
    assert result.reload_tokens[0] == 14


def test_automatic_observation_refreshes_version_and_is_policy_independent():
    """Tool observations append after ordinary billing and qualify the next action."""
    required = np.array([[[False], [True]]])
    observed = np.array([[[True], [True]]])
    mutated = np.array([[[True], [False]]])
    result = simulate_working_set(
        workload(),
        WorkingSetPolicy(),
        np.inf,
        marks(required, observed=observed, mutations=mutated),
    )
    ledger(result, 2, 20, 11, 4)
    assert result.reload_events[0] == 0
    assert result.max_context[0] == 28
    duplicated = simulate_working_set(
        workload(), WorkingSetPolicy(), np.inf, marks(observed=np.ones((1, 2, 1), dtype=bool))
    )
    ledger(duplicated, 2, 26, 17, 4)
    assert duplicated.max_context[0] == 34
    assert duplicated.reload_events[0] == 1


def test_strict_loop_is_bounded_and_failed_trajectories_stop():
    """A failed replicate remains failed while other vectorized replicates complete."""
    required = np.array([[[True], [True]], [[False], [False]]])
    work = workload(max_compactions_per_action=3)
    result = simulate_working_set(
        work,
        WorkingSetPolicy(trigger="strict"),
        15,
        marks(required, count=2, background=0, output=0),
    )
    np.testing.assert_array_equal(result.loop_failures, [1, 0])
    np.testing.assert_array_equal(result.completed_actions, [0, 2])
    np.testing.assert_array_equal(result.compactions, [3, 0])
    assert result.reload_events[0] == 4


def test_latest_valid_snapshots_selected_by_observation_recency():
    """Budgeted retention is file-specific, not a recent-background-turn heuristic."""
    work = workload(calls=3, artifacts=(ArtifactSpec("a", 5), ArtifactSpec("b", 5)))
    required = np.array([[[True, True], [False, False], [False, True]]])
    observed = np.array([[[False, False], [False, True], [False, False]]])
    policy = WorkingSetPolicy(preserve_recent_tokens=6, preserve_read_guards=True)
    result = simulate_working_set(
        work,
        policy,
        26,
        marks(required, calls=3, files=2, background=0, output=0, observed=observed),
    )
    assert result.compactions[0] == 1
    assert result.retained_file_tokens[0] == 6
    assert result.reload_events[0] == 1


def test_mutation_before_boundary_prevents_stale_retention():
    """External mutation occurs before compaction's valid-snapshot selection."""
    changes = np.array([[[False], [True]]])
    result = simulate_working_set(
        workload(),
        WorkingSetPolicy(preserve_recent_tokens=6, preserve_read_guards=True),
        18,
        marks(mutations=changes),
    )
    assert result.retained_file_tokens[0] == 0
    assert result.reload_tokens[0] == 12


def test_cache_ttl_inclusive_and_compaction_delay_expires_surviving_base():
    """Exact TTL remains warm; policy-added compaction time is charged once."""
    policy = WorkingSetPolicy(surviving_base_tokens=10)
    for delay, reads in ((5, 27), (5.001, 17)):
        result = simulate_working_set(workload(compaction_delay_seconds=delay), policy, 18, marks())
        assert result.read_tokens[0] == reads
    for gap, reads in ((5, 17), (5.001, 0)):
        result = simulate_working_set(
            workload(), WorkingSetPolicy(), np.inf, marks(gaps=np.array([[0, gap]]))
        )
        assert result.read_tokens[0] == reads


def test_no_terminal_reset_and_immutable_results():
    """A final threshold crossing does not invent an extra compactor call."""
    result = simulate_working_set(workload(calls=1), WorkingSetPolicy(), 18, marks(calls=1))
    assert result.compactions[0] == 0
    assert result.max_context[0] == 19
    with pytest.raises(ValueError):
        result.costs.setflags(write=True)


@pytest.mark.parametrize("threshold", [0, -1, np.nan, True])
def test_invalid_threshold_rejected(threshold):
    """Reject nonsensical thresholds at the simulation API boundary."""
    with pytest.raises(ValueError):
        simulate_working_set(workload(), WorkingSetPolicy(), threshold, marks())


def test_surviving_prefix_cannot_include_nonbase_tail():
    """An oversized declaration must never produce negative cache writes."""
    with pytest.raises(ValueError, match="stable base"):
        simulate_working_set(workload(), WorkingSetPolicy(surviving_base_tokens=11), 18, marks())


def test_surviving_prefix_must_be_an_eligible_cache_boundary():
    """A declared short boundary cannot act as a reusable cached prefix."""
    with pytest.raises(ValueError, match="eligibility"):
        simulate_working_set(
            workload(minimum_cache_tokens=10),
            WorkingSetPolicy(surviving_base_tokens=5),
            18,
            marks(),
        )


@pytest.mark.parametrize(
    "policy",
    [
        WorkingSetPolicy(),
        WorkingSetPolicy(restoration="eager", recovery_model_round=True),
        WorkingSetPolicy(trigger="strict", preserve_recent_tokens=6, preserve_read_guards=True),
    ],
)
def test_vectorized_trajectories_equal_independent_scalar_runs(policy):
    """Trajectory batching must not change versions, event order, or invoice totals."""
    rng = np.random.default_rng(741)
    shape = (12, 6)
    mask_shape = (*shape, 2)
    gaps = rng.uniform(0, 8, shape)
    gaps[:, 0] = 0
    field = ActionField(
        rng.integers(0, 4, shape),
        rng.integers(0, 4, shape),
        gaps,
        required=rng.random(mask_shape) < 0.4,
        mutations=rng.random(mask_shape) < 0.2,
        observed=rng.random(mask_shape) < 0.3,
    )
    work = workload(
        calls=6,
        artifacts=(ArtifactSpec("a", 5), ArtifactSpec("b", 7)),
        max_compactions_per_action=3,
        recovery_delay_seconds=2,
    )
    batched = simulate_working_set(work, policy, 25, field)
    names = ("background_input", "output_tokens", "gaps", "required", "mutations", "observed")
    for row in range(12):
        single = ActionField(**{name: getattr(field, name)[row : row + 1] for name in names})
        expected = simulate_working_set(work, policy, 25, single)
        for name in expected.__dataclass_fields__:
            assert getattr(batched, name)[row] == getattr(expected, name)[0], name
