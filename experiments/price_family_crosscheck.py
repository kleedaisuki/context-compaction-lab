"""Audit the executed expanded catalog against historical and price-scale controls.

Run after run_price_sensitivity.py with the price-family-results artifact name.
This checks published numerical artifacts, not provider billing or performance.
Identical-ratio and dominated-price claims follow from the fixed usage ledger;
the checks detect catalog/unit/reference mistakes in their instantiated results.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def main() -> None:
    """Check units, same-q reference policies, historical results and scale identities."""
    root = Path(__file__).resolve().parents[1]
    directory = root / "docs/research"
    catalog = json.loads((directory / "price-scenarios.json").read_text(encoding="utf-8"))
    current = json.loads((directory / "price-family-results.json").read_text(encoding="utf-8"))
    previous = json.loads(
        (directory / "price-sensitivity-results.json").read_text(encoding="utf-8")
    )
    entries = catalog["official_scenarios"]
    assert current["design"]["official_price_metadata"] == entries
    assert len(entries) == len({entry["id"] for entry in entries}) == 38
    assert current["source"] == previous["source"]
    cases = current["analytic_cases"]
    assert len(cases) == 143
    categories = ("input", "write", "read", "output")
    for entry in entries:
        for name in categories:
            assert entry["prices_per_million_usd"][name] >= 0
            assert np.isclose(
                entry["pricing_per_token"][name] * 1e6,
                entry["prices_per_million_usd"][name],
                rtol=1e-14,
                atol=0,
            )
        for q in (0.8, 0.95, 1):
            suffix = f"__q{q:g}" if q != 1 else ""
            row = cases[entry["id"] + suffix]
            assert row["ledger"]["cache_hit"] == q
            assert row["ledger"]["prices"] == entry["pricing_per_token"]
            assert row["right_tail_margin"] > 0
            if q != 1:
                assert row["old_threshold"] == cases["sonnet46_5m" + suffix]["marked_threshold"]
    # The original 35-case report stays immutable; an expanded catalog must not
    # alter its analytical scenarios, reference controls or source calibration.
    for name, row in previous["analytic_cases"].items():
        assert cases[name] == row, name

    pairs = (
        ("gpt6astra_short", "gpt6luna_short", 0.01),
        ("gpt6sol_short", "gpt56sol_short", 2),
        ("gpt54_short", "gpt54mini_short", 0.3),
        ("gpt56terra_short", "gpt56luna_short", 0.1),
        ("gpt52_short", "gpt53codex_standard", 1),
        ("deepseek41flash_offpeak", "deepseek41flash_peak", 2),
        ("deepseek4pro_offpeak", "deepseek4pro_peak", 2),
        ("qwen37plus_singapore_short_explicit", "qwen37plus_singapore_long_explicit", 3),
        ("qwen37plus_singapore_short_implicit", "qwen37plus_singapore_long_implicit", 3),
    )
    comparisons = 0
    for first, second, factor in pairs:
        for q in (0.8, 0.95, 1):
            suffix = f"__q{q:g}" if q != 1 else ""
            a, b = cases[first + suffix], cases[second + suffix]
            assert a["marked_threshold"] == b["marked_threshold"]
            assert np.isclose(b["marked_rate"], factor * a["marked_rate"], rtol=1e-13)
            for mode in ("iid", "block"):
                rows = current["independent_confirmation"]
                x, y = rows[f"{mode}/{first}{suffix}"], rows[f"{mode}/{second}{suffix}"]
                assert np.isclose(y["retuned_rate"], factor * x["retuned_rate"], rtol=1e-13)
            comparisons += 1
    for region in ("beijing", "singapore"):
        for q in (0.8, 0.95, 1):
            suffix = f"__q{q:g}" if q != 1 else ""
            a = cases[f"qwen38flash_{region}_explicit{suffix}"]
            b = cases[f"qwen38flash_{region}_implicit{suffix}"]
            assert a["marked_rate"] >= b["marked_rate"]
    result = {
        "catalog_entries": len(entries),
        "executed_cases": len(cases),
        "unchanged_historical_analytic_cases": len(previous["analytic_cases"]),
        "same_ratio_same_threshold_comparisons": comparisons,
        "same_ratio_confirmation_modes": ["iid", "block"],
        "quote_metadata_and_unit_consistency": True,
        "same_q_reference_controls": True,
        "scope": "Conditional repricing artifacts, not provider invoices or tokenization",
    }
    destination = root / ".cache/price-family-crosscheck"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
