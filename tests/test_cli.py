"""Exercise the installed CLI interfaces with workspace-local test artifacts."""

import json

import pytest

from context_compaction_lab.cli import main


def test_small_sweep_emits_reproducible_manifest(tmp_path) -> None:
    """A real CLI run saves expected costs, paired slopes, and holdout data."""
    main(
        [
            "sweep",
            "--calls",
            "8",
            "--replicates",
            "16",
            "--thresholds",
            "25000:35000:5000",
            "--output",
            str(tmp_path),
        ]
    )
    report = json.loads((tmp_path / "sweep.json").read_text())
    assert len(report["rows"]) == 3
    assert report["independent_validation"]["seed"] == report["seed"] + 1
    assert report["interpretation"]["data_status"] == "synthetic_unvalidated_workload_assumptions"
    assert (tmp_path / "trajectory-costs.npz").exists()
    assert (tmp_path / "sweep.png").exists()


def test_symbolic_command_persists_exact_expressions(tmp_path) -> None:
    """Analytical outputs identify their idealized stochastic scope."""
    path = tmp_path / "symbolic.json"
    main(["symbolic", "--output", str(path)])
    report = json.loads(path.read_text())
    assert "rate_derivative" in report["expressions"]


def test_fit_command_uses_named_csv_column(tmp_path) -> None:
    """Fit diagnostics retain trace identity, not a private absolute path."""
    source, output = tmp_path / "trace.csv", tmp_path / "fit.json"
    source.write_text("growth_tokens\n1\n2\n3\n4\n5\n6\n7\n8\n", encoding="utf-8")
    main(["fit", "--input", str(source), "--column", "growth_tokens", "--output", str(output)])
    report = json.loads(output.read_text())
    assert report["n"] == 8
    assert len(report["source"]["sha256"]) == 64


def test_invalid_threshold_grid_fails(tmp_path) -> None:
    """Malformed grids are rejected before simulation or output writes."""
    with pytest.raises(SystemExit):
        main(["sweep", "--thresholds", "0:30000:5000", "--output", str(tmp_path)])
