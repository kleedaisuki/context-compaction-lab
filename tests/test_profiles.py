"""Protect measured anchors, residual semantics, and aggregate reset billing."""

import json
from dataclasses import replace

import numpy as np
import pytest

from context_compaction_lab.cli import main
from context_compaction_lab.config import PositiveSpec, RecoverySpec
from context_compaction_lab.profiles import engineering_evidence, engineering_workload
from context_compaction_lab.simulation import draw_random_field, simulate


def test_engineering_profile_uses_full_reset_not_summary_only() -> None:
    """The published medians anchor a scenario, not two fitted means."""
    workload = engineering_workload(1)
    recovery = workload.recovery
    assert recovery.summary_base == 4_382
    assert recovery.restored_input_tokens == 61_206
    assert recovery.documents.mean == 0
    assert recovery.preserved_tokens == 0
    assert workload.initial_context == 65_588
    assert workload.growth.mean == 1_470
    assert not workload.warm_start
    assert "difference_of_medians" in engineering_evidence()["residual_status"]


def test_aggregate_is_input_and_not_generated_output() -> None:
    """Only 4,382 reset tokens are output, while the full payload becomes input."""
    workload = replace(engineering_workload(1), output_fraction=0)
    marks = draw_random_field(workload, 8, 3)
    result = simulate(workload, 60_000, marks)
    np.testing.assert_array_equal(result.output_tokens, np.full(8, 4_382))
    np.testing.assert_array_equal(result.write_tokens, 65_588 + marks.growth[:, 0])
    assert np.all(result.recovery_above_threshold == 1)


@pytest.mark.parametrize("preserved,documents", [(1, 0), (0, 1)])
def test_aggregate_and_components_cannot_be_double_counted(preserved, documents) -> None:
    """Reject an unidentified total plus an asserted constituent volume."""
    with pytest.raises(ValueError, match="overlap"):
        RecoverySpec(
            restored_input_tokens=10, preserved_tokens=preserved,
            documents=PositiveSpec("constant", documents),
        )


def test_default_cli_serializes_evidence_and_scenario_separately(tmp_path) -> None:
    """The default is engineering scale without a claim of trace-fitted distributions."""
    main([
        "sweep", "--calls", "3", "--replicates", "8",
        "--thresholds", "75000:85000:5000", "--output", str(tmp_path),
    ])
    report = json.loads((tmp_path / "sweep.json").read_text())
    assert report["scenario_name"] == "engineering"
    assert report["workload"]["recovery"]["restored_input_tokens"] == 61_206
    assert report["engineering_evidence"]["published_anchors"]
    assert report["interpretation"]["data_status"].endswith("not_trace_fit")


def test_engineering_small_summary_noise_keeps_zero_unknown_documents(tmp_path) -> None:
    """A zero placeholder is not converted to an invalid positive Lognormal law."""
    main([
        "sweep", "--calls", "2", "--replicates", "8", "--recovery-cv", "0.05",
        "--thresholds", "75000:80000:5000", "--output", str(tmp_path),
    ])
    recovery = json.loads((tmp_path / "sweep.json").read_text())["workload"]["recovery"]
    assert recovery["documents"]["family"] == "constant"
    assert recovery["summary"]["cv"] == 0.05
    assert recovery["restored_input_tokens"] == 61_206


def test_simultaneous_split_to_aggregate_overrides_are_order_independent(tmp_path) -> None:
    """A valid final state must not fail because an intermediate state overlaps."""
    main([
        "sweep", "--scenario", "baseline", "--calls", "2", "--replicates", "8",
        "--restored-input-tokens", "61206", "--documents-mean", "0",
        "--thresholds", "75000:80000:5000", "--output", str(tmp_path),
    ])
    recovery = json.loads((tmp_path / "sweep.json").read_text())["workload"]["recovery"]
    assert recovery["documents"]["mean"] == 0
    assert recovery["restored_input_tokens"] == 61_206
