"""Exercise working-set boundaries and unconditionally immutable event snapshots."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from context_compaction_lab.config import Pricing
from context_compaction_lab.working_set_config import (
    ActionField,
    ArtifactSpec,
    WorkingSetPolicy,
    WorkingSetWorkload,
)


def _workload(**overrides) -> WorkingSetWorkload:
    """Construct explicit small scenario sizes while varying one boundary."""
    values = dict(artifacts=(ArtifactSpec("file", 20),), base_tokens=10, summary_tokens=5)
    values.update(overrides)
    return WorkingSetWorkload(**values)


def _field(**overrides) -> ActionField:
    """Construct two actions over one artifact without implicit broadcasting."""
    values = dict(
        background_input=np.array([[2, 3]]),
        output_tokens=np.array([[4, 5]]),
        gaps=np.array([[0.0, 1.0]]),
        required=np.array([[[True], [False]]]),
    )
    values.update(overrides)
    return ActionField(**values)


def test_explicit_scenario_sizes_and_reused_pricing() -> None:
    """Base and summary are declared scenarios rather than measured defaults."""
    with pytest.raises(TypeError):
        WorkingSetWorkload(artifacts=(ArtifactSpec("file", 20),))
    workload = _workload()
    assert workload.pricing == Pricing()
    assert workload.calls == 400
    assert workload.to_dict()["artifacts"] == (
        {"name": "file", "tokens": 20, "requires_read_guard": True},
    )


def test_catalog_detaches_source_and_dataclasses_are_frozen() -> None:
    """Caller-owned catalog lists cannot alter the workload after construction."""
    source = [ArtifactSpec("file", 20)]
    workload = _workload(artifacts=source)
    source.clear()
    assert len(workload.artifacts) == 1
    for instance, name, value in (
        (workload, "calls", 2),
        (workload.artifacts[0], "tokens", 4),
        (WorkingSetPolicy(), "trigger", "strict"),
        (_field(), "gaps", None),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, name, value)


@pytest.mark.parametrize("name", ["", "   ", None, 4])
def test_artifact_names_are_nonempty_strings(name) -> None:
    """Identifiers are preserved exactly but must carry a usable name."""
    with pytest.raises(ValueError):
        ArtifactSpec(name, 1)


@pytest.mark.parametrize("value", [-1, 1.5, True, np.nan, np.inf, "1"])
def test_artifact_tokens_are_discrete_nonnegative(value) -> None:
    """Invalid token units cannot become a silently rounded model bill."""
    with pytest.raises(ValueError):
        ArtifactSpec("file", value)


@pytest.mark.parametrize("catalog", [(), None, ["file"], [ArtifactSpec("a", 1)] * 2])
def test_artifact_catalog_is_nonempty_typed_unique(catalog) -> None:
    """One column corresponds to exactly one uniquely named catalog artifact."""
    with pytest.raises(ValueError):
        _workload(artifacts=catalog)


@pytest.mark.parametrize(
    "name",
    [
        "base_tokens",
        "summary_tokens",
        "minimum_cache_tokens",
        "normal_uncached_tokens",
        "compaction_instruction_tokens",
        "file_wrapper_tokens",
        "recovery_command_tokens",
        "recovery_instruction_tokens",
        "calls",
        "max_compactions_per_action",
    ],
)
@pytest.mark.parametrize("value", [-1, 0.5, True, np.nan, np.inf])
def test_workload_integer_parameters(name, value) -> None:
    """Validate every discrete accounting unit before trajectory allocation."""
    with pytest.raises(ValueError):
        _workload(**{name: value})


@pytest.mark.parametrize("name", ["calls", "max_compactions_per_action"])
def test_positive_action_and_retry_counts(name) -> None:
    """An empty experiment or unbounded zero-attempt loop is not a scenario."""
    with pytest.raises(ValueError):
        _workload(**{name: 0})


@pytest.mark.parametrize(
    "name", ["cache_ttl_seconds", "recovery_delay_seconds", "compaction_delay_seconds"]
)
@pytest.mark.parametrize("value", [-1, True, np.nan, np.inf, "1"])
def test_durations_are_real_finite_nonnegative(name, value) -> None:
    """Reject malformed clocks rather than producing silent cache behavior."""
    with pytest.raises(ValueError):
        _workload(**{name: value})


def test_ttl_none_and_zero_delay_limits() -> None:
    """No expiry and no additional delay are allowed explicit reference limits."""
    assert _workload(cache_ttl_seconds=None).cache_ttl_seconds is None
    assert _workload().recovery_delay_seconds == 0
    with pytest.raises(ValueError):
        _workload(cache_ttl_seconds=0)
    with pytest.raises(ValueError):
        _workload(pricing={"input": 0})


@pytest.mark.parametrize("name", ["preserve_recent_tokens", "surviving_base_tokens"])
@pytest.mark.parametrize("value", [-1, 0.5, True, np.nan, np.inf])
def test_policy_retention_is_nonnegative_integer(name, value) -> None:
    """Retention declarations use the same discrete units as context sizes."""
    with pytest.raises(ValueError):
        WorkingSetPolicy(**{name: value})


@pytest.mark.parametrize(
    "factory, name",
    [
        (lambda **kw: ArtifactSpec("a", 1, **kw), "requires_read_guard"),
        (_workload, "warm_start"),
        (WorkingSetPolicy, "preserve_read_guards"),
        (WorkingSetPolicy, "recovery_model_round"),
    ],
)
@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_configuration_flags_are_boolean(factory, name, value) -> None:
    """Truthy values must not silently enable extra rounds or read guards."""
    with pytest.raises(ValueError):
        factory(**{name: value})


@pytest.mark.parametrize("name", ["restoration", "trigger"])
def test_policy_rejects_unknown_modes(name) -> None:
    """There is no fallback policy for misspelled external configuration."""
    with pytest.raises(ValueError):
        WorkingSetPolicy(**{name: "unknown"})


def test_masks_are_optional_without_implicit_artifact_dimension() -> None:
    """Any supplied mask establishes shape and missing event streams are false."""
    for name in ("required", "mutations", "observed"):
        overrides = {"required": None, name: [[[True], [False]]]}
        field = _field(**overrides)
        assert getattr(field, name)[0, 0, 0]
        for other in {"required", "mutations", "observed"} - {name}:
            assert getattr(field, other).shape == (1, 2, 1)
            assert not getattr(field, other).any()
    with pytest.raises(ValueError):
        _field(required=None)


def test_arrays_are_detached_and_immutable_even_through_base() -> None:
    """Read-only flags alone are insufficient; immutable byte storage is required."""
    source = np.array([[2, 3]])
    source_mask = np.array([[[True], [False]]])
    field = _field(background_input=source, required=source_mask)
    source[:] = 0
    source_mask[:] = False
    np.testing.assert_array_equal(field.background_input, [[2, 3]])
    assert field.required[0, 0, 0]
    for name in ("background_input", "output_tokens", "gaps", "required", "mutations", "observed"):
        array = getattr(field, name)
        with pytest.raises(ValueError):
            array.flat[0] = 0
        with pytest.raises(ValueError):
            array.setflags(write=True)
        with pytest.raises(ValueError):
            array.base.setflags(write=True)


@pytest.mark.parametrize("name", ["background_input", "output_tokens"])
@pytest.mark.parametrize(
    "array",
    [
        [[1.0, 2.0]],
        [[-1, 2]],
        [[True, False]],
        [[np.nan, 1]],
        [[np.inf, 1]],
        [["1", "2"]],
        np.array([[2**63, 1]], dtype=np.uint64),
    ],
)
def test_action_tokens_reject_invalid_types_and_ranges(name, array) -> None:
    """Token arrays cannot round floats, interpret booleans, or overflow int64."""
    with pytest.raises(ValueError):
        _field(**{name: array})


@pytest.mark.parametrize("array", [[[0, -1]], [[0, np.nan]], [[0, np.inf]], [[False, True]]])
def test_action_gaps_reject_bad_durations(array) -> None:
    """Every clock increment is nonnegative, finite, and real."""
    with pytest.raises(ValueError):
        _field(gaps=array)


def test_first_gap_is_zero_for_every_replicate() -> None:
    """Initial state has no exogenous time preceding its first request."""
    with pytest.raises(ValueError):
        _field(gaps=[[1, 0]])
    with pytest.raises(ValueError):
        ActionField([[1], [1]], [[1], [1]], [[0], [1]], required=[[[True]], [[True]]])


@pytest.mark.parametrize(
    "overrides",
    [
        {"background_input": [1, 2]},
        {"background_input": np.zeros((0, 2), dtype=int)},
        {"background_input": np.zeros((1, 0), dtype=int)},
        {"output_tokens": [[1]]},
        {"gaps": [0, 1]},
        {"required": [[True, False]]},
        {"required": np.zeros((1, 2, 0), dtype=bool)},
        {"required": np.zeros((2, 2, 1), dtype=bool)},
        {"mutations": np.zeros((1, 2, 2), dtype=bool)},
        {"observed": [[[1], [0]]]},
    ],
)
def test_event_shapes_are_strict_nonempty_and_boolean(overrides) -> None:
    """No broadcast, empty dimension, or numeric mask may change event identity."""
    with pytest.raises(ValueError):
        _field(**overrides)


def test_noncontiguous_arrays_copy_in_order() -> None:
    """Source strides cannot scramble ordinary-action identity when serialized."""
    field = _field(background_input=np.array([[3, 2]])[:, ::-1])
    np.testing.assert_array_equal(field.background_input, [[2, 3]])
    assert field.background_input.dtype == np.int64
    assert field.gaps.dtype == np.float64
