"""Export executed finite-control and continuum exhibits as portable aggregates.

Regenerate inputs with working_set_exact_control.py, structural_symbolic_analysis.py
and continuum_threshold_analysis.py, plus renewal_closed_form_derivation.py.
This export runs no stochastic experiment;
it preserves the reported numerical results and exact rational jump expressions.
Source digests identify the executed inputs without publishing raw trace rows.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def main() -> None:
    """Publish the finite exhibits needed to rebuild the extended manuscript."""
    root = Path(__file__).resolve().parents[1]
    paths = {
        "exact": root / ".cache/working-set-exact-control/results.json",
        "structure": root / ".cache/structural-symbolic-analysis/results.json",
        "continuum": root / ".cache/continuum-threshold-analysis/results.json",
        "renewal_laws": root / ".cache/renewal-closed-form/results.json",
    }
    inputs = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in paths.items()}
    exact = inputs["exact"]
    scans = {}
    for name, scan in (
        ("default", exact["threshold_scan"]),
        ("read_stress", exact["read_price_sensitivity"]["scan"]),
    ):
        scans[name] = {
            "summaries": scan["summaries"],
            "first_use_curve": [
                {key: row[key] for key in ("threshold", "costs")}
                for row in scan["curves"]["first_use"]
            ],
        }
    continuum = inputs["continuum"]
    output = {
        "schema_version": 1,
        "scope": "Executed exact finite controls; not observed engineering demand",
        "source_sha256": {
            key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()
        },
        "exact_control": {
            "ordinary_actions": exact["ordinary_actions"],
            "path_count": exact["path_count"],
            "demand_probability": exact["demand_probability"],
            "workload": exact["workload"],
            "scans": scans,
            "endogenous_first_cycle": exact["endogenous_first_cycle"],
            "batching_counterexample": exact["batching_counterexample"],
            "paired_monte_carlo": exact["paired_monte_carlo"],
        },
        "global_price_phases": inputs["structure"]["global_price_phases"],
        "closed_law_controls": inputs["renewal_laws"]["dimensionless_comparative_statics"],
        "continuum": {
            "semantics": continuum["semantics"],
            "actual_curve_results": continuum["actual_curve_results"],
            "uniform_lattice_bridge": continuum["uniform_lattice_bridge"],
        },
    }
    destination = root / "docs/research/paper-supplement-results.json"
    destination.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("Exported portable exact-control and continuum exhibits, without resampling.")


if __name__ == "__main__":
    main()
