"""Finite-horizon, four-category billing with paired exogenous random marks."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .config import Workload
from .distributions import sample_positive

Array = NDArray[np.float64]


@dataclass(frozen=True)
class RandomField:
    """Immutable independent marks aligned by ordinary request index.

    All arrays have shape ``(replicates, calls)``. Growth and documents are
    integer-valued token counts; gaps are nonnegative seconds, with first gap
    zero; recovery_fractions lie in [0, 1]. Construction copies caller arrays,
    so callers can safely reuse a field across threshold policies.
    """

    growth: Array
    gaps: Array
    recovery_fractions: Array
    documents: Array

    def __post_init__(self) -> None:
        """Validate marks and take immutable owned copies without tail clipping."""
        shape = np.shape(self.growth)
        if len(shape) != 2 or min(shape) < 1:
            raise ValueError("Random marks require positive replicate and call dimensions.")
        for name in ("growth", "gaps", "recovery_fractions", "documents"):
            value = np.array(getattr(self, name), dtype=np.float64, copy=True)
            if value.shape != shape or not np.all(np.isfinite(value)):
                raise ValueError("Random marks must have matching shapes and finite values.")
            if np.any(value < 0):
                raise ValueError("Random marks must be nonnegative.")
            if name in {"growth", "documents"} and np.any(value != np.rint(value)):
                raise ValueError("Growth and documents must contain integer token counts.")
            if name == "growth" and np.any(value < 1):
                raise ValueError("Growth must be at least one token.")
            if name == "recovery_fractions" and np.any(value > 1):
                raise ValueError("Recovery fractions must lie in [0, 1].")
            if name == "gaps" and np.any(value[:, 0] != 0):
                raise ValueError("The initial request gap must be zero.")
            # Bytes-backed storage cannot have its writeable flag re-enabled.
            frozen = np.frombuffer(value.tobytes(), dtype=np.float64).reshape(shape)
            object.__setattr__(self, name, frozen)


@dataclass(frozen=True)
class SimulationResult:
    """One observation per independent trajectory, not per ordinary request.

    costs are USD; input_tokens, write_tokens and read_tokens are disjoint
    input categories. output_tokens includes ordinary outputs and summaries.
    compactions counts extra requests; cache_hits and cache_misses partition
    ordinary requests (ineligible requests count as misses).
    recovery_above_threshold counts strict recovery overshoots; max_context
    is the largest retained state, including initial and recovered states.
    Arrays are read-only and costs include fixed compaction overhead.
    """

    costs: Array
    input_tokens: Array
    write_tokens: Array
    read_tokens: Array
    output_tokens: Array
    compactions: NDArray[np.int64]
    cache_hits: NDArray[np.int64]
    cache_misses: NDArray[np.int64]
    recovery_above_threshold: NDArray[np.int64]
    max_context: Array


def draw_random_field(workload: Workload, replicates: int, seed: int) -> RandomField:
    """Draw independent marginals for reproducible paired-policy comparisons.

    Example: draw one field, then pass it to simulate for every candidate
    threshold. Unused recovery marks remain aligned by ordinary call index.
    """
    if not isinstance(replicates, int) or isinstance(replicates, bool) or replicates < 1:
        raise ValueError("Replicates must be a positive integer.")
    rng = np.random.default_rng(seed)
    shape = (replicates, workload.calls)
    growth = np.maximum(1, np.rint(sample_positive(workload.growth, rng, shape)))
    gaps = sample_positive(workload.gaps, rng, shape)
    gaps[:, 0] = 0
    recovery = workload.recovery
    mean = recovery.fraction_mean
    if mean in (0, 1):
        fractions = np.full(shape, mean, dtype=np.float64)
    else:
        concentration = recovery.fraction_concentration
        fractions = rng.beta(mean * concentration, (1 - mean) * concentration, shape)
    documents = np.rint(sample_positive(recovery.documents, rng, shape))
    return RandomField(growth, gaps, fractions, documents)


def simulate(workload: Workload, threshold: float, random_field: RandomField) -> SimulationResult:
    """Bill fixed ordinary calls, with at most one reset before each call.

    Positive infinity disables compaction. TTL is inclusive: a gap equal to
    TTL still hits. Outputs are retained but become cacheable only on the next
    request. Recovery above threshold is recorded, never clipped or retried.
    No reset is performed after the final ordinary request.
    """
    if math.isnan(threshold) or threshold <= 0:
        raise ValueError("Threshold must be positive (positive infinity is allowed).")
    if random_field.growth.shape[1] != workload.calls:
        raise ValueError("Random-field call dimension must match workload.calls.")
    size = random_field.growth.shape[0]
    context = np.full(size, workload.initial_context, dtype=np.float64)
    eligible_start = workload.warm_start and (
        workload.initial_context >= workload.minimum_cache_tokens
    )
    prefix = context.copy() if eligible_start else np.zeros(size)
    inputs, writes, reads, outputs = (np.zeros(size) for _ in range(4))
    compactions, hits, misses, overshoots = (np.zeros(size, dtype=np.int64) for _ in range(4))
    maximum = context.copy()
    for call in range(workload.calls):
        if workload.cache_ttl_seconds is not None:
            prefix[random_field.gaps[:, call] > workload.cache_ttl_seconds] = 0
        reset = context >= threshold
        if np.any(reset):
            reads[reset] += prefix[reset]
            inputs[reset] += context[reset] - prefix[reset]
            inputs[reset] += workload.compaction_instruction_tokens
            basis = threshold if workload.recovery.basis == "threshold" else context[reset]
            summary = np.rint(
                workload.recovery.summary_base
                + random_field.recovery_fractions[reset, call] * basis
            )
            outputs[reset] += summary
            context[reset] = summary + random_field.documents[reset, call]
            prefix[reset] = 0
            compactions[reset] += 1
            overshoots[reset] += context[reset] > threshold
            maximum = np.maximum(maximum, context)
        output = np.rint(workload.output_fraction * random_field.growth[:, call])
        cacheable = context + random_field.growth[:, call] - output
        eligible = cacheable >= workload.minimum_cache_tokens
        hit = eligible & (prefix > 0)
        hits += hit
        misses += ~hit
        reads[hit] += prefix[hit]
        writes[eligible] += cacheable[eligible] - prefix[eligible]
        inputs[~eligible] += cacheable[~eligible]
        inputs += workload.normal_uncached_tokens
        outputs += output
        prefix = np.where(eligible, cacheable, 0)
        context = cacheable + output
        maximum = np.maximum(maximum, context)
    pricing = workload.pricing
    costs = (
        inputs * pricing.input
        + writes * pricing.write
        + reads * pricing.read
        + outputs * pricing.output
        + compactions * workload.compaction_fixed_usd
    )
    values = (costs, inputs, writes, reads, outputs, compactions, hits, misses, overshoots, maximum)
    for value in values:
        value.setflags(write=False)
    return SimulationResult(*values)
