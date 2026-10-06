"""Execute price-regime, parameter-path and marked-tail symbolic derivations.

The sign examples are exact algebraic cases, not simulated workloads or claims
about current provider prices. Common price rescaling does not change H*.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import sympy as sp

from context_compaction_lab.renewal_analytic import ErlangRenewal, RenewalFees, optimal_gap
from context_compaction_lab.sensitivity_symbolics import (
    SensitivitySymbols,
    billed_rate_basis,
    core_sensitivities,
    marked_sensitivities,
)


def serialize(value: object) -> object:
    """Preserve exact symbolic expressions and unambiguous variable names in JSON."""
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(item) for item in value]
    if isinstance(value, (sp.Basic, sp.MatrixBase)):
        return str(value)
    return value


def exact_regime_examples(m: SensitivitySymbols, core: dict, marked: dict) -> dict:
    """Show genuine sign reversals with rational substitutions and valid reset compositions."""
    pi, pw, pr, po = m.prices
    prices = {pi: 3, pw: sp.Rational(15, 4), pr: sp.Rational(3, 10), po: 15}
    write_case = {**prices, m.reset: 100, m.stable: 0, m.summary: 10, m.instruction: 1}
    read_case = {**prices, m.reset: 100, m.stable: 95, m.summary: 1, m.instruction: 1}
    write_boundary = sp.simplify(core["write_hit_crossover"].subs(write_case))
    read_boundary = sp.factor(core["read_hit_crossover"].subs(read_case))
    assert 0 < write_boundary < 1 and read_boundary == sp.Rational(51, 100)
    write_low = core["sign_numerators"][pw].subs({**write_case, m.hit: sp.Rational(1, 2)})
    write_high = core["sign_numerators"][pw].subs({**write_case, m.hit: sp.Rational(99, 100)})
    read_low = core["sign_numerators"][pr].subs({**read_case, m.hit: sp.Rational(1, 10)})
    read_high = core["sign_numerators"][pr].subs({**read_case, m.hit: sp.Rational(9, 10)})
    assert write_low < 0 < write_high and read_high < 0 < read_low
    reverse_hit = {
        pi: 10,
        pw: 3,
        pr: 1,
        po: 1,
        m.reset: 100,
        m.stable: 100,
        m.summary: 0,
        m.instruction: 0,
    }
    hit_numerator = sp.factor(core["sign_numerators"][m.hit].subs(reverse_hit))
    assert hit_numerator == -700
    warm = {**prices, m.hit: 1, m.reset: 100, m.stable: 99, m.summary: 1, m.instruction: 1}
    a = float(m.fee.subs(warm))
    carry, crossing = float(m.carry.subs(warm)), float(m.crossing.subs(warm))
    tail = float(m.tail_coefficient.subs(warm))
    law = ErlangRenewal(1)
    fees = RenewalFees(100, a - crossing * 100, carry, crossing, terminal_coefficient=tail)
    unmarked = optimal_gap(law, fees)
    marked_root = optimal_gap(law, fees, terminal_fraction=1)
    effective_w = 2 - (2 + marked_root) * math.exp(-marked_root)
    core_write = float(core["sign_numerators"][pw].subs(warm))
    w_symbol = next(
        symbol
        for symbol in marked["warm_write_regime_numerator"].free_symbols
        if str(symbol) == "W"
    )
    corrected_write = float(
        marked["warm_write_regime_numerator"].subs({**warm, w_symbol: effective_w})
    )
    assert corrected_write < 0 < core_write
    return {
        "status": "algebraic parameter cases and analytic exponential roots, no simulations",
        "declared_common_price_vector": prices,
        "core_write_hit_boundary": write_boundary,
        "core_write_hit_boundary_numeric": float(write_boundary),
        "core_write_negative_at_q_half": write_low,
        "core_write_positive_at_q_099": write_high,
        "core_read_hit_boundary": read_boundary,
        "core_read_positive_at_q_01": read_low,
        "core_read_negative_at_q_09": read_high,
        "reverse_cache_hit_case": reverse_hit,
        "reverse_cache_hit_numerator": hit_numerator,
        "warm_tail_case": warm,
        "unmarked_gap": unmarked,
        "marked_gap": marked_root,
        "effective_W_at_marked_root": effective_w,
        "warm_core_write_numerator": core_write,
        "warm_marked_write_numerator": corrected_write,
    }


def exponential_chain_check(m: SensitivitySymbols, core: dict) -> dict:
    """Verify the implicit gradient and mixed interaction using the exponential inverse."""
    gap = sp.sqrt(m.growth_mean**2 + 2 * m.growth_mean * m.ratio) - m.growth_mean
    duration = 1 + gap / m.growth_mean
    u = next(
        symbol
        for symbol in core["threshold_gradient"][m.prices[0]].free_symbols
        if str(symbol) == "U_star"
    )
    density = next(
        symbol
        for symbol in core["threshold_mixed_derivatives"][(m.prices[0], m.prices[3])].free_symbols
        if str(symbol) == "u_star"
    )
    for variable in m.prices:
        assert (
            sp.simplify(
                sp.diff(gap, variable) - core["threshold_gradient"][variable].subs(u, duration)
            )
            == 0
        )
    expected = core["threshold_mixed_derivatives"][(m.prices[0], m.prices[3])]
    assert (
        sp.simplify(
            sp.diff(gap, m.prices[0], m.prices[3])
            - expected.subs({u: duration, density: 1 / m.growth_mean})
        )
        == 0
    )
    return {
        "exponential_gap": gap,
        "input_output_mixed_derivative": sp.factor(sp.diff(gap, m.prices[0], m.prices[3])),
    }


def main() -> None:
    """Persist exact pricing geometry and verified sensitivity mechanisms."""
    started = time.perf_counter()
    model = SensitivitySymbols.canonical()
    core, marked = core_sensitivities(model), marked_sensitivities(model)
    assert sp.expand(core["fee"] - core["original_fee_equivalence"]) == 0
    result = {
        "assumptions": "fixed price-independent law, positive prices, 0<=q,theta<=1, S>=B+C",
        "core": core,
        "marked": marked,
        "billed_rate_basis": billed_rate_basis(model),
        "regime_examples": exact_regime_examples(model, core, marked),
        "exponential_chain_check": exponential_chain_check(model, core),
    }
    result["runtime_seconds"] = time.perf_counter() - started
    directory = Path(".cache/price-sensitivity")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "symbolic-results.json").write_text(
        json.dumps(serialize(result), indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            serialize(
                {
                    "runtime_seconds": result["runtime_seconds"],
                    "regime_examples": result["regime_examples"],
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
