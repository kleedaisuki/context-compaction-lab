"""Immutable contracts for versioned file working sets and shared action fields."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from numbers import Real
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .config import Pricing, _validate_integer


def _validate_seconds(value: float, name: str, *, positive: bool = False) -> None:
    """Reject non-real, boolean, nonfinite, and out-of-domain durations."""
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, Real)
        or not math.isfinite(value)
        or value < 0
        or (positive and value == 0)
    ):
        raise ValueError(f"{name} must be finite and {'positive' if positive else 'nonnegative'}.")


def _validate_boolean(value: bool, name: str) -> None:
    """Keep configuration flags distinct from arbitrary truthy values."""
    if not isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be boolean.")


@dataclass(frozen=True)
class ArtifactSpec:
    """Describe one whole-file payload, excluding its tool wrapper.

    Attributes:
        name: Unique nonempty catalog identifier, not a version identifier.
        tokens: Nonnegative model-visible payload length of each file version.
        requires_read_guard: Whether edits require a qualifying current-version
            observation independently of semantic availability.
    """

    name: str
    tokens: int
    requires_read_guard: bool = True

    def __post_init__(self) -> None:
        """Validate file identity and discrete payload length."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Artifact name must be a nonempty string.")
        _validate_integer(self.tokens, "tokens")
        _validate_boolean(self.requires_read_guard, "requires_read_guard")


@dataclass(frozen=True)
class WorkingSetWorkload:
    """Declare a finite ordinary-action scenario and its four-price ledger.

    Attributes:
        artifacts: Nonempty catalog of uniquely named whole-file payloads.
        base_tokens: Stable instructions present initially and after every reset;
            explicit because no default is an empirical workload measurement.
        summary_tokens: Generated summary length at each reset, explicitly set.
        calls: Fixed number of ordinary actions, excluding additional model calls.
        pricing: Disjoint USD-per-token input, write, read, and output rates.
        minimum_cache_tokens: Smallest eligible cached-prefix boundary.
        cache_ttl_seconds: Positive cache lifetime; None disables expiry.
        normal_uncached_tokens: Ephemeral ordinary-request suffix, not retained.
        compaction_instruction_tokens: Ephemeral compactor input instruction.
        file_wrapper_tokens: Retained tool wrapper added per file observation.
        warm_start: Whether the initial eligible stable base is already warm.
        recovery_command_tokens: Generated output of each recovery model round.
        recovery_instruction_tokens: Ephemeral recovery model instruction input.
        recovery_delay_seconds: Additional elapsed time per batched recovery.
        compaction_delay_seconds: Additional elapsed time per compactor call;
            ordinary-action gaps must exclude these policy-extra durations.
        max_compactions_per_action: Strict-mode retry bound before infeasibility.
    """

    artifacts: tuple[ArtifactSpec, ...]
    base_tokens: int
    summary_tokens: int
    calls: int = 400
    pricing: Pricing = field(default_factory=Pricing)
    minimum_cache_tokens: int = 1_024
    cache_ttl_seconds: float | None = 300.0
    normal_uncached_tokens: int = 128
    compaction_instruction_tokens: int = 128
    file_wrapper_tokens: int = 64
    warm_start: bool = False
    recovery_command_tokens: int = 64
    recovery_instruction_tokens: int = 64
    recovery_delay_seconds: float = 0.0
    compaction_delay_seconds: float = 0.0
    max_compactions_per_action: int = 8

    def __post_init__(self) -> None:
        """Validate before allocation and detach any mutable catalog sequence."""
        try:
            artifacts = tuple(self.artifacts)
        except TypeError as error:
            raise ValueError("artifacts must be a nonempty sequence of ArtifactSpec.") from error
        if not artifacts or any(not isinstance(item, ArtifactSpec) for item in artifacts):
            raise ValueError("artifacts must contain at least one ArtifactSpec.")
        if len({item.name for item in artifacts}) != len(artifacts):
            raise ValueError("Artifact names must be unique.")
        object.__setattr__(self, "artifacts", artifacts)
        for name in (
            "base_tokens",
            "summary_tokens",
            "minimum_cache_tokens",
            "normal_uncached_tokens",
            "compaction_instruction_tokens",
            "file_wrapper_tokens",
            "recovery_command_tokens",
            "recovery_instruction_tokens",
        ):
            _validate_integer(getattr(self, name), name)
        _validate_integer(self.calls, "calls", minimum=1)
        _validate_integer(self.max_compactions_per_action, "max_compactions_per_action", minimum=1)
        _validate_boolean(self.warm_start, "warm_start")
        if not isinstance(self.pricing, Pricing):
            raise ValueError("pricing must be Pricing with USD-per-token rates.")
        if self.cache_ttl_seconds is not None:
            _validate_seconds(self.cache_ttl_seconds, "cache_ttl_seconds", positive=True)
        _validate_seconds(self.recovery_delay_seconds, "recovery_delay_seconds")
        _validate_seconds(self.compaction_delay_seconds, "compaction_delay_seconds")

    def to_dict(self) -> dict[str, object]:
        """Return scenario assumptions suitable for JSON serialization."""
        return asdict(self)


@dataclass(frozen=True)
class WorkingSetPolicy:
    """Choose reset retention and restoration without changing ordinary actions.

    Attributes:
        restoration: Eagerly reload the catalog or defer until first required use.
        preserve_recent_tokens: Budget for the latest valid whole-file
            observations, including payload and wrapper, after reset; generic
            recent turns are not retained by this file-specific policy.
        preserve_read_guards: Keep valid qualifying reads for retained files.
        surviving_base_tokens: Explicit unchanged warm prefix surviving reset;
            simulator checks it against workload base and cache minimum.
        recovery_model_round: Charge an additional model round per recovery batch.
        trigger: Atomic read/edit units or diagnostic strict pre-request rechecks.
    """

    restoration: Literal["eager", "first_use"] = "first_use"
    preserve_recent_tokens: int = 0
    preserve_read_guards: bool = False
    surviving_base_tokens: int = 0
    recovery_model_round: bool = False
    trigger: Literal["atomic", "strict"] = "atomic"

    def __post_init__(self) -> None:
        """Reject unsupported policy modes and invalid retention declarations."""
        if self.restoration not in ("eager", "first_use"):
            raise ValueError("restoration must be eager or first_use.")
        if self.trigger not in ("atomic", "strict"):
            raise ValueError("trigger must be atomic or strict.")
        _validate_integer(self.preserve_recent_tokens, "preserve_recent_tokens")
        _validate_integer(self.surviving_base_tokens, "surviving_base_tokens")
        _validate_boolean(self.preserve_read_guards, "preserve_read_guards")
        _validate_boolean(self.recovery_model_round, "recovery_model_round")


def _immutable_array(value: object, name: str, kind: str) -> NDArray:
    """Copy validated values into a bytes-backed array that cannot become writable."""
    array = np.asarray(value)
    if kind == "integer":
        if array.dtype.kind not in "iu" or np.any(array < 0):
            raise ValueError(f"{name} must contain nonnegative integer token counts.")
        if np.any(array > np.iinfo(np.int64).max):
            raise ValueError(f"{name} exceeds the supported int64 token range.")
        dtype = np.int64
    elif kind == "boolean":
        if array.dtype.kind != "b":
            raise ValueError(f"{name} must contain boolean values.")
        dtype = np.bool_
    else:
        if array.dtype.kind not in "iuf" or np.any(~np.isfinite(array)) or np.any(array < 0):
            raise ValueError(f"{name} must contain finite nonnegative seconds.")
        dtype = np.float64
    copied = np.asarray(array, dtype=dtype, order="C")
    if kind == "seconds" and np.any(~np.isfinite(copied)):
        raise ValueError(f"{name} exceeds the supported float64 seconds range.")
    return np.frombuffer(copied.tobytes(), dtype=dtype).reshape(copied.shape)


@dataclass(frozen=True, eq=False)
class ActionField:
    """Share immutable exogenous events indexed by replicate and ordinary action.

    Attributes:
        background_input: Retained non-file input tokens, shape (replicates, calls).
        output_tokens: Ordinary generated tokens with the same shape.
        gaps: Nonnegative elapsed seconds, same shape; first action gap is zero.
        required: Current-version prerequisites, shape (replicates, calls, artifacts).
        mutations: External version changes applied before the ordinary action.
        observed: Automatic current-version file observations appended afterward.

    At least one boolean mask establishes the nonempty artifact dimension.
    Omitted masks become false arrays of exactly that shape; all three dimensions
    must be positive. Every array is detached from its source and bytes-backed,
    including its base, so setting NumPy's writable flag cannot mutate the field.

    Example:
        field = ActionField([[10]], [[5]], [[0]], required=[[[True]]])
    """

    background_input: NDArray[np.int64]
    output_tokens: NDArray[np.int64]
    gaps: NDArray[np.float64]
    required: NDArray[np.bool_] | None = None
    mutations: NDArray[np.bool_] | None = None
    observed: NDArray[np.bool_] | None = None

    def __post_init__(self) -> None:
        """Validate strict event shapes without broadcasting or numeric coercion."""
        for name, kind in (
            ("background_input", "integer"),
            ("output_tokens", "integer"),
            ("gaps", "seconds"),
        ):
            object.__setattr__(self, name, _immutable_array(getattr(self, name), name, kind))
        shape = self.background_input.shape
        if len(shape) != 2 or min(shape) < 1:
            raise ValueError("Action token arrays need nonempty (replicates, calls) shape.")
        if self.output_tokens.shape != shape or self.gaps.shape != shape:
            raise ValueError("Token arrays and gaps must have exactly the same shape.")
        if np.any(self.gaps[:, 0] != 0):
            raise ValueError("The first action gap must be zero in every replicate.")
        masks = (self.required, self.mutations, self.observed)
        supplied = next((mask for mask in masks if mask is not None), None)
        if supplied is None:
            raise ValueError("At least one artifact mask must establish the artifact dimension.")
        mask_shape = np.asarray(supplied).shape
        if len(mask_shape) != 3 or mask_shape[:2] != shape or mask_shape[2] < 1:
            raise ValueError("Artifact masks need nonempty (replicates, calls, artifacts) shape.")
        for name in ("required", "mutations", "observed"):
            value = getattr(self, name)
            if value is None:
                value = np.zeros(mask_shape, dtype=np.bool_)
            mask = _immutable_array(value, name, "boolean")
            if mask.shape != mask_shape:
                raise ValueError("All artifact masks must have exactly the same shape.")
            object.__setattr__(self, name, mask)
