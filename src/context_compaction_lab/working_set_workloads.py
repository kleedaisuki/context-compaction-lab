"""Controlled task prerequisites paired with observed output-only block samples."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np

from .config import PositiveSpec
from .distributions import sample_positive
from .working_set_config import ActionField, WorkingSetWorkload


@dataclass(frozen=True)
class DemandSpec:
    """Declare synthetic action structure separately from empirical measurements.

    phase selects one hot file per phase with occasional other-file demands;
    diffuse samples catalog identities uniformly; mandatory requires all files
    at every action, testing the concentrated compulsory-working-set limit.
    Background excludes all explicit file observations and restored payloads.
    """

    mode: Literal["phase", "diffuse", "mandatory"] = "phase"
    required_probability: float = 0.85
    hot_probability: float = 0.9
    phase_length: int = 25
    mutation_probability: float = 0.002
    observation_probability: float = 0.0
    background_input_tokens: int = 256
    gap_mean_seconds: float = 90.0
    gap_cv: float = 1.5

    def __post_init__(self) -> None:
        """Reject unmeasured but invalid controls rather than clip them."""
        from .config import _validate_integer

        if self.mode not in {"phase", "diffuse", "mandatory"}:
            raise ValueError("Unknown demand mode.")
        for name in (
            "required_probability",
            "hot_probability",
            "mutation_probability",
            "observation_probability",
        ):
            value = getattr(self, name)
            if not np.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must lie in [0,1].")
        _validate_integer(self.phase_length, "phase_length", minimum=1)
        _validate_integer(self.background_input_tokens, "background_input_tokens")
        PositiveSpec("lognormal", self.gap_mean_seconds, self.gap_cv)

    def to_dict(self) -> dict[str, object]:
        """Serialize controlled assumptions independently of source evidence."""
        return asdict(self)


def draw_actions(
    workload: WorkingSetWorkload,
    demand: DemandSpec,
    replicates: int,
    seed: int,
    pool: np.ndarray,
    starts: np.ndarray,
    block_length: int,
) -> ActionField:
    """Draw identical primitive tasks for every threshold and restoration policy.

    Real output blocks preserve within-block serial dependence. The remaining
    actions are controlled, not inferred file-level trajectories. Do not sample
    on compact count or add restored files to measured fresh-append growth.
    """
    if isinstance(replicates, bool) or replicates < 1:
        raise ValueError("Require positive replicate count.")
    output_rng, gap_rng, demand_rng, mutation_rng, observation_rng = (
        np.random.default_rng(child) for child in np.random.SeedSequence(seed).spawn(5)
    )
    shape = (replicates, workload.calls)
    blocks = (workload.calls + block_length - 1) // block_length
    origins = output_rng.choice(starts, size=(replicates, blocks))
    offsets = origins[:, :, None] + np.arange(block_length)[None, None, :]
    outputs = pool[offsets].reshape(replicates, -1)[:, : workload.calls]
    gaps = sample_positive(
        PositiveSpec("lognormal", demand.gap_mean_seconds, demand.gap_cv), gap_rng, shape
    )
    gaps[:, 0] = 0
    files = len(workload.artifacts)
    required = np.zeros((*shape, files), dtype=bool)
    hot = demand_rng.integers(
        files, size=(replicates, (workload.calls + demand.phase_length - 1) // demand.phase_length)
    )
    hot = np.repeat(hot, demand.phase_length, axis=1)[:, : workload.calls]
    choices = demand_rng.integers(files, size=shape)
    prefer_hot = demand_rng.random(shape) < demand.hot_probability
    used = demand_rng.random(shape) < demand.required_probability
    if demand.mode == "phase":
        choices = np.where(prefer_hot, hot, choices)
    rows, calls = np.indices(shape)
    required[rows, calls, choices] = used
    if demand.mode == "mandatory":
        required[:] = True
    mutations = mutation_rng.random(required.shape) < demand.mutation_probability
    observed = required & (observation_rng.random(required.shape) < demand.observation_probability)
    background = np.full(shape, demand.background_input_tokens, dtype=np.int64)
    return ActionField(background, outputs, gaps, required, mutations, observed)
