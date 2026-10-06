"""Verify task/resource ratio identities without inventing a success model.

Success and category occupation are symbolic differentiable functions of a
controller coordinate. Empirical success is intentionally not inferred from
the project's fixed-action usage traces. This script checks algebra, not
attainment or regularity conditions for a particular agent.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    """Check the throughput derivative and implicit price-response identities."""
    h = sp.Symbol("h", real=True)
    prices = sp.symbols("p_i p_w p_r p_o", positive=True)
    occupations = [sp.Function(name)(h) for name in ("m_i", "m_w", "m_r", "m_o")]
    success = sp.Function("s")(h)
    cost = sum(price * usage for price, usage in zip(prices, occupations, strict=True))
    root = sp.diff(success, h) * cost - success * sp.diff(cost, h)
    checks = {
        "quotient_derivative": sp.simplify(sp.diff(success / cost, h) - root / cost**2),
        "root_h_derivative": sp.simplify(
            sp.diff(root, h) - (sp.diff(success, h, 2) * cost - success * sp.diff(cost, h, 2))
        ),
    }
    for price, usage in zip(prices, occupations, strict=True):
        checks[f"root_{price}_derivative"] = sp.simplify(
            sp.diff(root, price) - (sp.diff(success, h) * usage - success * sp.diff(usage, h))
        )
    scale = sp.Symbol("a", positive=True)
    checks["scaling"] = sp.simplify(
        success / cost.subs({p: scale * p for p in prices}, simultaneous=True)
        - success / cost / scale
    )
    assert all(value == 0 for value in checks.values())
    output = {
        "scope": "Symbolic identities; no measured success or task-efficiency optimum",
        "sympy_version": sp.__version__,
        "checks": {key: str(value) for key, value in checks.items()},
        "stationary_balance": str(root),
        "price_response": {str(p): str(-sp.diff(root, p) / sp.diff(root, h)) for p in prices},
        "regularity": "Positive expected resource; smooth active interior root with nonzero F_h",
    }
    root_path = Path(__file__).resolve().parents[1]
    destination = root_path / ".cache/paper/task-efficiency-symbolics.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(checks)} exact symbolic task-efficiency identities.")


if __name__ == "__main__":
    main()
