"""Protect experimental source mapping and the success-efficiency algebra."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]


def load_builder():
    """Load the repository-local artifact builder without changing package paths."""
    spec = importlib.util.spec_from_file_location(
        "paper_exhibits", ROOT / "experiments/build_paper_exhibits.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def aggregate(name: str) -> dict:
    """Read maintained aggregate evidence rather than a private/raw trace."""
    return json.loads((ROOT / "docs/research" / name).read_text(encoding="utf-8"))


def test_all_quoted_configurations_are_printed_once() -> None:
    """Both catalog tables must jointly retain all 38 published configurations."""
    builder = load_builder()
    catalog = aggregate("price-scenarios.json")
    tex = builder.price_exhibits(aggregate("price-family-results.json"), catalog)
    assert len(catalog["official_scenarios"]) == 38
    for quote in catalog["official_scenarios"]:
        label = quote["id"].replace("_", " ").replace("singapore", "SG").replace("beijing", "BJ")
        assert tex.count(label + " & $(") == 1


def test_exhibits_preserve_distinct_workload_denominators() -> None:
    """Bill units and independent horizons must not be pooled across studies."""
    builder = load_builder()
    working = builder.working_exhibits(aggregate("working-set-results.json"))
    renewal = builder.renewal_exhibits(aggregate("renewal-results.json"))
    assert "USD/task" in working
    assert "USD/action" in renewal
    assert "Phase-local & 78 &" in working
    assert "Mandatory & 126 &" in working
    assert "IID & 32 & 150.588" in renewal
    assert "Blocks & 32 & 165.588" in renewal


@pytest.mark.parametrize(
    "cost_a,cost_b,success_a,success_b",
    [
        (8, 10, sp.Rational(1, 2), sp.Rational(9, 10)),
        (8, 10, sp.Rational(9, 10), sp.Rational(9, 10)),
        (8, 10, sp.Rational(18, 25), sp.Rational(9, 10)),
    ],
)
def test_success_loss_boundary(cost_a, cost_b, success_a, success_b) -> None:
    """A bill advantage reverses precisely at the relative success boundary."""
    efficiency_a = success_a / cost_a
    efficiency_b = success_b / cost_b
    assert (efficiency_a < efficiency_b) == (success_a / success_b < sp.Rational(cost_a, cost_b))
