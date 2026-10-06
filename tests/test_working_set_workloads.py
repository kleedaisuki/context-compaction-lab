"""Protect empirical block integrity and paired controlled-action generation."""

from dataclasses import replace

import numpy as np
import pytest

from context_compaction_lab.working_set_config import ArtifactSpec, WorkingSetWorkload
from context_compaction_lab.working_set_workloads import DemandSpec, draw_actions


def fixture():
    """Provide two distinguishable output blocks without any network dependency."""
    workload = WorkingSetWorkload(
        (ArtifactSpec("a", 10), ArtifactSpec("b", 20)), 100, 10, calls=8, minimum_cache_tokens=1
    )
    return workload, np.arange(16, dtype=np.int64), np.array([0, 4, 8, 12], dtype=np.int64)


def test_empirical_outputs_are_contiguous_valid_blocks() -> None:
    """Resampling does not manufacture token lengths or cross supplied block boundaries."""
    workload, pool, starts = fixture()
    field = draw_actions(workload, DemandSpec(), 32, 17, pool, starts, 4)
    groups = field.output_tokens.reshape(32, 2, 4)
    assert np.all(np.diff(groups, axis=2) == 1)
    assert np.all(np.isin(groups[:, :, 0], starts))
    assert np.all(field.gaps[:, 0] == 0)


def test_mechanism_cases_do_not_change_background_output_or_version_streams() -> None:
    """Separate random streams isolate demand-mode interventions from other events."""
    workload, pool, starts = fixture()
    first = draw_actions(workload, DemandSpec(), 16, 3, pool, starts, 4)
    second = draw_actions(workload, DemandSpec(mode="diffuse"), 16, 3, pool, starts, 4)
    for name in ("output_tokens", "background_input", "mutations", "gaps"):
        np.testing.assert_array_equal(getattr(first, name), getattr(second, name))


def test_mandatory_limit_requires_every_file() -> None:
    """The user's concentrated compulsory-working-set limit is explicit and testable."""
    workload, pool, starts = fixture()
    field = draw_actions(workload, DemandSpec(mode="mandatory"), 16, 3, pool, starts, 4)
    assert np.all(field.required)
    assert not np.any(field.observed)
    changed = draw_actions(
        workload, replace(DemandSpec(), observation_probability=1), 16, 3, pool, starts, 4
    )
    np.testing.assert_array_equal(changed.observed, changed.required)


@pytest.mark.parametrize(
    "keyword,value",
    [
        ("phase_length", 0),
        ("mutation_probability", -1),
        ("required_probability", 2),
        ("gap_mean_seconds", 0),
    ],
)
def test_bad_demand_controls_fail(keyword, value) -> None:
    """Controlled does not mean unvalidated; malformed assumptions fail fast."""
    with pytest.raises(ValueError):
        DemandSpec(**{keyword: value})
