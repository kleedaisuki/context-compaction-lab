"""Validated parameters for stochastic workloads and API token accounting."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from numbers import Integral
from typing import Literal


def _validate_integer(value: int, name: str, minimum: int = 0) -> None:
    """Reject fractional/nonfinite token counts and booleans at the boundary."""
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f"{name} must be an integer greater than or equal to {minimum}.")


@dataclass(frozen=True)
class PositiveSpec:
    """Specify a nonnegative constant or positive continuous distribution.

    Attributes:
        family: Distribution family; burst_lognormal is a two-scale mixture.
        mean: Population mean in the caller's units, not a fitted estimate.
        cv: Component coefficient of variation; ignored for a constant.
        burst_probability: Probability of the larger mixture component.
        burst_multiplier: Ratio of burst to ordinary component means. The
            mixture is normalized to retain the specified overall mean.
    """

    family: Literal["constant", "gamma", "lognormal", "burst_lognormal"] = "gamma"
    mean: float = 2_000.0
    cv: float = 0.8
    burst_probability: float = 0.08
    burst_multiplier: float = 8.0

    def __post_init__(self) -> None:
        """Reject invalid moments instead of silently clipping distributions."""
        if self.family not in {"constant", "gamma", "lognormal", "burst_lognormal"}:
            raise ValueError("Unsupported distribution family.")
        if not math.isfinite(self.mean) or self.mean < 0:
            raise ValueError("Mean must be finite and nonnegative.")
        if self.family != "constant" and (self.mean <= 0 or self.cv <= 0):
            raise ValueError("Continuous positive families require positive mean and CV.")
        if not math.isfinite(self.cv) or self.cv < 0:
            raise ValueError("CV must be finite and nonnegative.")
        if not 0 <= self.burst_probability <= 1 or self.burst_multiplier < 1:
            raise ValueError("Invalid burst-mixture parameters.")
        if not math.isfinite(self.burst_multiplier):
            raise ValueError("Burst multiplier must be finite.")


@dataclass(frozen=True)
class Pricing:
    """Four disjoint token prices in USD per token, not per million.

    Attributes:
        input: Uncached tokens processed without creating a reusable entry.
        write: Tokens newly written to the normal request's cache prefix.
        read: Reused cached-prefix tokens.
        output: Billed generated tokens, including compaction summaries.
    """

    input: float = 3 / 1_000_000
    write: float = 3.75 / 1_000_000
    read: float = 0.30 / 1_000_000
    output: float = 15 / 1_000_000

    def __post_init__(self) -> None:
        """Permit zero-price idealized limits but reject negative/nonfinite rates."""
        if any(not math.isfinite(value) or value < 0 for value in asdict(self).values()):
            raise ValueError("Prices must be finite and nonnegative.")


@dataclass(frozen=True)
class RecoverySpec:
    """Model the state recovered after a compaction event.

    Attributes:
        summary_base: Fixed generated-summary tokens unless summary is supplied.
        fraction_mean: Optional legacy Beta fraction of the basis; zero by
            default so summary length does not grow with the threshold.
        fraction_concentration: Sum of legacy Beta shape parameters.
        documents: Distribution of reloaded document tokens, newly inserted.
        basis: Use the nominal threshold or the actual crossed context.
            The latter generally induces Markov dependence between cycles.
        summary: Optional positive distribution overriding summary_base, for
            tightly concentrated summary-size sensitivity experiments. It
            cannot be combined with a nonzero proportional fraction.
        preserved_tokens: Target verbatim old-context tokens retained without
            generation, capped only by the amount of old context available.
        surviving_prefix_tokens: Leading preserved tokens with an explicitly
            valid unchanged cache boundary. Zero is the conservative default;
            preserving token contents alone does not establish cache reuse.
        restored_input_tokens: Aggregate non-generated recovered payload when
            instructions/tools/history/files cannot be separately identified.
            Mutually exclusive with documents and preserved_tokens to prevent
            counting an aggregate and its components twice. This is not a
            measurement of document rereading or a generated-output budget.
    """

    summary_base: int = 2_000
    fraction_mean: float = 0.0
    fraction_concentration: float = 30.0
    documents: PositiveSpec = field(default_factory=lambda: PositiveSpec("constant", mean=12_000))
    basis: Literal["threshold", "crossed"] = "threshold"
    summary: PositiveSpec | None = None
    preserved_tokens: int = 0
    surviving_prefix_tokens: int = 0
    restored_input_tokens: int = 0

    def __post_init__(self) -> None:
        """Keep retained fractions meaningful without censoring document tails."""
        _validate_integer(self.summary_base, "summary_base")
        _validate_integer(self.preserved_tokens, "preserved_tokens")
        _validate_integer(self.surviving_prefix_tokens, "surviving_prefix_tokens")
        _validate_integer(self.restored_input_tokens, "restored_input_tokens")
        if self.restored_input_tokens and (self.documents.mean or self.preserved_tokens):
            raise ValueError("Aggregate restored input cannot overlap documents or preservation.")
        if self.surviving_prefix_tokens > self.preserved_tokens:
            raise ValueError("A surviving prefix must be part of verbatim preserved context.")
        if self.summary is not None and self.fraction_mean != 0:
            raise ValueError("Distributed summary and proportional summary are alternative laws.")
        if not 0 <= self.fraction_mean <= 1:
            raise ValueError("Invalid summary size or retained fraction.")
        if not math.isfinite(self.fraction_concentration) or self.fraction_concentration <= 0:
            raise ValueError("Beta concentration must be positive and finite.")
        if self.basis not in {"threshold", "crossed"}:
            raise ValueError("Recovery basis must be threshold or crossed.")


@dataclass(frozen=True)
class Workload:
    """Synthetic workload assumptions, held fixed across competing policies.

    Attributes:
        calls: Number of ordinary calls; extra compaction calls are charged.
        growth: Distribution of retained input plus output growth per call.
        gaps: Distribution of start-to-start normal-request gaps in seconds;
            includes generation and tools, not just human waiting time.
        output_fraction: Fraction of growth allocated to generated output;
            the remainder is newly retained input.
        initial_context: Initial retained context tokens.
        warm_start: Whether that initial prefix is already cached.
        cache_ttl_seconds: Prefix lifetime refreshed on reuse; None means no
            expiry, an idealized reference condition.
        minimum_cache_tokens: Minimum length eligible for prefix caching.
        normal_uncached_tokens: Ephemeral per-request suffix input, not retained.
        compaction_instruction_tokens: Extra uncached compaction input.
        compaction_fixed_usd: Non-token compaction/recovery overhead per event.
        recovery: Conditional summary and reloaded-document state model.
        pricing: Fixed API rates, with no context-tier or subscription mapping.
    """

    calls: int = 400
    growth: PositiveSpec = field(default_factory=PositiveSpec)
    gaps: PositiveSpec = field(default_factory=lambda: PositiveSpec("lognormal", mean=90, cv=1.5))
    output_fraction: float = 0.25
    initial_context: int = 20_000
    warm_start: bool = True
    cache_ttl_seconds: float | None = 300.0
    minimum_cache_tokens: int = 1_024
    normal_uncached_tokens: int = 128
    compaction_instruction_tokens: int = 128
    compaction_fixed_usd: float = 0.0
    recovery: RecoverySpec = field(default_factory=RecoverySpec)
    pricing: Pricing = field(default_factory=Pricing)

    def __post_init__(self) -> None:
        """Validate accounting assumptions before drawing any random samples."""
        _validate_integer(self.calls, "calls", minimum=1)
        if self.growth.mean <= 0:
            raise ValueError("A workload needs positive calls and mean growth.")
        if not 0 <= self.output_fraction <= 1:
            raise ValueError("Output fraction must lie in [0, 1].")
        for name in (
            "initial_context",
            "minimum_cache_tokens",
            "normal_uncached_tokens",
            "compaction_instruction_tokens",
        ):
            _validate_integer(getattr(self, name), name)
        if self.cache_ttl_seconds is not None and (
            not math.isfinite(self.cache_ttl_seconds) or self.cache_ttl_seconds <= 0
        ):
            raise ValueError("TTL must be positive and finite, or None.")
        if not math.isfinite(self.compaction_fixed_usd) or self.compaction_fixed_usd < 0:
            raise ValueError("Fixed compaction overhead must be nonnegative and finite.")
        surviving = self.recovery.surviving_prefix_tokens
        if 0 < surviving < self.minimum_cache_tokens:
            raise ValueError("The declared surviving boundary must meet the cache minimum.")

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible assumptions with explicit price units."""
        return asdict(self)
