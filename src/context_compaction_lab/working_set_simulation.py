"""Versioned file residency and cache-aware four-price request accounting."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .working_set_config import ActionField, WorkingSetPolicy, WorkingSetWorkload

Array = NDArray[np.float64]


@dataclass(frozen=True)
class WorkingSetResult:
    """Per-trajectory invoices and diagnostics; failed invoices are incomplete.

    Token input categories are disjoint. Reload and retained file counts include
    wrappers. Context area sums ordinary request context (including background
    input), excluding uncached instruction suffixes and additional model rounds.
    Max context includes generated output and automatic observations. Overshoots
    count post-reset states strictly above the threshold, not provider failures.
    A loop failure stops its trajectory; callers must reject that policy point.
    Arrays own immutable bytes-backed storage.
    """

    costs: Array
    input_tokens: Array
    write_tokens: Array
    read_tokens: Array
    output_tokens: Array
    compactions: NDArray[np.int64]
    recovery_rounds: NDArray[np.int64]
    reload_events: NDArray[np.int64]
    reload_tokens: Array
    reload_payload_tokens: Array
    retained_file_tokens: Array
    context_area: Array
    max_context: Array
    overshoots: NDArray[np.int64]
    loop_failures: NDArray[np.int64]
    completed_actions: NDArray[np.int64]
    base_cache_read_tokens: Array


@dataclass
class _State:
    """Bounded latest-snapshot metadata; obsolete text lives only in context size."""

    context: Array
    prefix: Array
    age: Array
    versions: NDArray[np.int64]
    resident: NDArray[np.int64]
    guards: NDArray[np.int64]
    recency: NDArray[np.int64]
    active: NDArray[np.bool_]
    totals: dict[str, NDArray] = field(default_factory=dict)
    clock: int = 0


def _initial(workload: WorkingSetWorkload, count: int) -> _State:
    """Start with stable base only; no file observations are implicitly known."""
    context = np.full(count, workload.base_tokens, dtype=float)
    prefix = context.copy() if workload.warm_start else np.zeros(count)
    prefix[context < workload.minimum_cache_tokens] = 0
    shape = (count, len(workload.artifacts))
    state = _State(
        context,
        prefix,
        np.zeros(count),
        np.zeros(shape, dtype=np.int64),
        np.full(shape, -1, dtype=np.int64),
        np.full(shape, -1, dtype=np.int64),
        np.full(shape, -1, dtype=np.int64),
        np.ones(count, dtype=bool),
    )
    integers = {
        "compactions",
        "recovery_rounds",
        "reload_events",
        "overshoots",
        "loop_failures",
        "completed_actions",
    }
    for name in WorkingSetResult.__dataclass_fields__:
        state.totals[name] = np.zeros(count, dtype=np.int64 if name in integers else float)
    state.totals["max_context"] = context.copy()
    return state


def _expire(state: _State, workload: WorkingSetWorkload, delay: Array) -> None:
    """Expire only after strictly exceeding TTL, including tool recovery delay."""
    state.age += delay
    if workload.cache_ttl_seconds is not None:
        state.prefix[state.age > workload.cache_ttl_seconds] = 0


def _maximum(state: _State) -> None:
    """Include retained states even when a strict-mode action cannot complete."""
    np.maximum(state.totals["max_context"], state.context, out=state.totals["max_context"])


def _request(
    state: _State,
    workload: WorkingSetWorkload,
    mask: NDArray,
    suffix: int,
    output: Array | int,
    cache_write: bool,
) -> None:
    """Bill a model request; generated output is absent from its new cache entry."""
    context = state.context[mask]
    eligible = context >= workload.minimum_cache_tokens
    warm = np.where(eligible, state.prefix[mask], 0)
    state.totals["read_tokens"][mask] += warm
    state.totals["base_cache_read_tokens"][mask] += np.minimum(warm, workload.base_tokens)
    state.totals["input_tokens"][mask] += suffix
    cold = context - warm
    if cache_write:
        state.totals["write_tokens"][mask] += np.where(eligible, cold, 0)
        state.totals["input_tokens"][mask] += np.where(eligible, 0, context)
        state.prefix[mask] = np.where(eligible, context, 0)
    else:
        state.totals["input_tokens"][mask] += cold
    generated = output if np.isscalar(output) else output[mask]
    state.totals["output_tokens"][mask] += generated
    if cache_write:
        state.context[mask] += generated
    state.age[mask] = 0
    _maximum(state)


def _retained(state: _State, mask: NDArray, weights: Array, budget: int) -> NDArray:
    """Select newest whole valid snapshots greedily, skipping units that do not fit."""
    selected = np.zeros_like(state.resident, dtype=bool)
    valid = (state.resident == state.versions) & mask[:, None]
    order = np.argsort(-state.recency, axis=1, kind="stable")
    remaining = np.full(len(mask), budget, dtype=float)
    rows = np.arange(len(mask))
    for rank in range(len(weights)):
        column = order[:, rank]
        take = valid[rows, column] & (weights[column] <= remaining)
        selected[rows[take], column[take]] = True
        remaining[take] -= weights[column[take]]
    return selected


def _compact(
    state: _State,
    workload: WorkingSetWorkload,
    policy: WorkingSetPolicy,
    mask: NDArray,
    weights: Array,
) -> None:
    """Replace history, retaining only valid observations and explicitly warm base."""
    if not np.any(mask):
        return
    selected = _retained(state, mask, weights, policy.preserve_recent_tokens)
    surviving = np.minimum(state.prefix[mask], policy.surviving_base_tokens)
    _request(
        state,
        workload,
        mask,
        workload.compaction_instruction_tokens,
        workload.summary_tokens,
        False,
    )
    retained = selected @ weights
    state.context[mask] = workload.base_tokens + workload.summary_tokens + retained[mask]
    state.prefix[mask] = surviving
    _expire(state, workload, mask * workload.compaction_delay_seconds)
    state.resident[mask] = np.where(selected[mask], state.versions[mask], -1)
    keep_guards = selected[mask] & policy.preserve_read_guards
    state.guards[mask] = np.where(keep_guards, state.guards[mask], -1)
    state.totals["retained_file_tokens"][mask] += retained[mask]
    state.totals["compactions"][mask] += 1
    _maximum(state)


def _observe(state: _State, mask: NDArray, weights: Array) -> None:
    """Append tool payloads without retroactive cache insertion or free stale eviction."""
    if not np.any(mask):
        return
    state.context += mask @ weights
    state.resident[mask] = state.versions[mask]
    state.guards[mask] = state.versions[mask]
    state.clock += 1
    state.recency[mask] = state.clock
    _maximum(state)


def _restore(
    state: _State,
    workload: WorkingSetWorkload,
    policy: WorkingSetPolicy,
    required: NDArray,
    eager: NDArray,
    weights: Array,
    guarded: NDArray,
) -> None:
    """Batch missing current facts/read guards into one optional recovery round.

    Recovery instructions are uncached, command output is generated and retained,
    and tool payload follows the model round. Delay expires even the newly written
    recovery prefix before the ordinary request; tool I/O is never model output.
    """
    missing = state.resident != state.versions
    guard_missing = guarded & (state.guards != state.versions)
    needed = (required & (missing | guard_missing)) | (eager[:, None] & missing)
    needed &= state.active[:, None]
    events = np.any(needed, axis=1)
    if not np.any(events):
        return
    if policy.recovery_model_round:
        _request(
            state,
            workload,
            events,
            workload.recovery_instruction_tokens,
            workload.recovery_command_tokens,
            True,
        )
        state.totals["recovery_rounds"][events] += 1
    _expire(state, workload, events * workload.recovery_delay_seconds)
    state.totals["reload_events"][events] += 1
    state.totals["reload_tokens"] += needed @ weights
    payload = np.array([artifact.tokens for artifact in workload.artifacts])
    state.totals["reload_payload_tokens"] += needed @ payload
    _observe(state, needed, weights)


def simulate_working_set(
    workload: WorkingSetWorkload, policy: WorkingSetPolicy, threshold: float, field: ActionField
) -> WorkingSetResult:
    """Run fixed ordinary actions, vectorizing independent trajectories.

    Atomic mode permits one reset before restoration. Strict mode repeatedly
    rechecks restored context at ``>= threshold`` and stops bounded failures.
    Fixed post-action observations always append, even when the same file was
    read as a prerequisite earlier: those are distinct tool events. Background
    input must exclude these explicitly represented observation payloads.
    No terminal reset is performed. Example: reuse the identical ActionField
    across policies to compare invoices with paired ordinary-action marks.
    """
    if isinstance(threshold, bool) or math.isnan(threshold) or threshold <= 0:
        raise ValueError("Threshold must be positive; positive infinity disables resets.")
    if policy.surviving_base_tokens > workload.base_tokens:
        raise ValueError("Surviving unchanged prefix cannot exceed the stable base.")
    if 0 < policy.surviving_base_tokens < workload.minimum_cache_tokens:
        raise ValueError("Surviving prefix must meet minimum cache eligibility.")
    count, calls = field.background_input.shape
    if calls != workload.calls or field.required.shape[2] != len(workload.artifacts):
        raise ValueError("Action dimensions must match workload calls and artifacts.")
    state = _initial(workload, count)
    weights = np.array([a.tokens + workload.file_wrapper_tokens for a in workload.artifacts])
    guarded = np.array([a.requires_read_guard for a in workload.artifacts], dtype=bool)
    for call in range(calls):
        _expire(state, workload, field.gaps[:, call] * state.active)
        state.versions += field.mutations[:, call] & state.active[:, None]
        reset = state.active & (state.context >= threshold)
        _compact(state, workload, policy, reset, weights)
        eager = state.active & (reset | (call == 0)) & (policy.restoration == "eager")
        _restore(state, workload, policy, field.required[:, call], eager, weights, guarded)
        state.totals["overshoots"] += reset & (state.context > threshold)
        attempts = reset.astype(np.int64)
        if policy.trigger == "strict":
            _strict(
                state,
                workload,
                policy,
                threshold,
                field.required[:, call],
                attempts,
                weights,
                guarded,
            )
        active = state.active.copy()
        state.context[active] += field.background_input[active, call]
        state.totals["context_area"][active] += state.context[active]
        _request(
            state,
            workload,
            active,
            workload.normal_uncached_tokens,
            field.output_tokens[:, call],
            True,
        )
        observed = field.observed[:, call] & active[:, None]
        _observe(state, observed, weights)
        state.totals["completed_actions"][active] += 1
    pricing = workload.pricing
    state.totals["costs"] = sum(
        state.totals[name] * rate
        for name, rate in (
            ("input_tokens", pricing.input),
            ("write_tokens", pricing.write),
            ("read_tokens", pricing.read),
            ("output_tokens", pricing.output),
        )
    )
    frozen = {
        name: np.frombuffer(value.tobytes(), dtype=value.dtype)
        for name, value in state.totals.items()
    }
    return WorkingSetResult(**frozen)


def _strict(
    state: _State,
    workload: WorkingSetWorkload,
    policy: WorkingSetPolicy,
    threshold: float,
    required: NDArray,
    attempts: NDArray,
    weights: Array,
    guarded: NDArray,
) -> None:
    """Bound non-progressing reset/read loops without counting failed actions."""
    pending = state.active & (state.context >= threshold)
    while np.any(pending):
        failed = pending & (attempts >= workload.max_compactions_per_action)
        state.totals["loop_failures"][failed] += 1
        state.active[failed] = False
        pending &= ~failed
        if not np.any(pending):
            break
        _compact(state, workload, policy, pending, weights)
        attempts[pending] += 1
        eager = pending & (policy.restoration == "eager")
        _restore(state, workload, policy, required, eager, weights, guarded)
        state.totals["overshoots"] += pending & (state.context > threshold)
        pending = state.active & (state.context >= threshold)
