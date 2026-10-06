"""Derive closed renewal thresholds and moment corrections with exact algebra.

This is analytical law evaluation, not path simulation or a fitted synthetic
workload. Dimensionless tables illustrate theorem mechanisms; empirical law
calibration and its dependence checks remain a separate root-owned analysis.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import sympy as sp

from context_compaction_lab.analytic import exponential_benchmark
from context_compaction_lab.config import Pricing
from context_compaction_lab.renewal_analytic import (
    ErlangRenewal,
    HyperexponentialRenewal,
    RenewalFees,
    asymptotic_optimal_gap,
    optimal_gap,
    physical_cache_fees,
    random_reset_exponential_optimum,
    rate,
    rate_derivative,
)


def symbolic_laws() -> dict:
    """Check Laplace inversion, occupation derivative, and terminal-mark closed forms."""
    gap, g, s, c, a = sp.symbols("L g s c A", positive=True)
    kappa, reset, baseline = sp.symbols("kappa S b", nonnegative=True)
    theta = 3 * sp.sqrt(3) * gap / (2 * g)
    durations = {
        1: 1 + gap / g,
        2: gap / g + sp.Rational(3, 4) + sp.exp(-4 * gap / g) / 4,
        3: gap / g
        + sp.Rational(2, 3)
        + sp.exp(-9 * gap / (2 * g)) * (sp.cos(theta) / 3 + sp.sqrt(3) * sp.sin(theta) / 9),
    }
    laws = {}
    for shape, duration in durations.items():
        transform = (1 + g * s / shape) ** shape / (s * ((1 + g * s / shape) ** shape - 1))
        assert sp.simplify(sp.laplace_transform(duration, gap, s, noconds=True) - transform) == 0
        t = sp.Symbol("t", nonnegative=True)
        integrated = sp.simplify(sp.integrate(duration.subs(gap, t), (t, 0, gap)))
        occupation = sp.expand(gap * duration - integrated)
        price = baseline + c * reset + kappa * g + (a + c * occupation) / duration
        derivative = sp.diff(duration, gap) * (c * integrated - a) / duration**2
        assert sp.simplify(sp.diff(price, gap) - derivative) == 0
        if shape == 1:
            terminal = g * (2 - sp.exp(-gap / g))
        elif shape == 2:
            terminal = g * (sp.Rational(3, 2) + sp.exp(-4 * gap / g) / 2 - sp.exp(-2 * gap / g))
        else:
            terminal = g * (
                sp.Rational(4, 3)
                + sp.Rational(2, 3) * sp.exp(-9 * gap / (2 * g)) * sp.cos(theta)
                - sp.exp(-3 * gap / g)
            )
        phi = (1 + g * s / shape) ** (-shape)
        terminal_transform = (g + sp.diff(phi, s)) / (s * (1 - phi))
        assert (
            sp.simplify(sp.laplace_transform(terminal, gap, s, noconds=True) - terminal_transform)
            == 0
        )
        laws[str(shape)] = {
            "U": str(duration),
            "D": str(integrated),
            "M": str(occupation),
            "laplace_U": str(transform),
            "rate": str(price),
            "derivative": str(derivative),
            "terminal_increment": str(terminal),
            "laplace_terminal_increment": str(terminal_transform),
        }
    optimum = sp.sqrt(g**2 + 2 * g * a / c) - g
    assert sp.simplify((gap + gap**2 / (2 * g)).subs(gap, optimum) - a / c) == 0
    old = exponential_benchmark()
    symbols = {str(symbol): symbol for symbol in old["stationary_threshold"].free_symbols}
    rewritten = old["stationary_threshold"].subs(
        symbols["k_0"], a - (symbols["k_1"] + symbols["p_w"] - symbols["p_r"]) * symbols["S"]
    )
    rewritten = rewritten.subs({symbols["S"]: reset, symbols["g"]: g, symbols["p_r"]: c})
    assert sp.simplify(rewritten - reset - optimum) == 0
    return {
        "erlang_laws": laws,
        "exponential_optimal_gap": str(optimum),
        "fluid_optimal_gap": str(sp.sqrt(2 * g * a / c)),
        "existing_exponential_optimal_threshold": str(old["stationary_threshold"]),
        "general_erlang_roots": "r_j=(k/g)*(omega_j-1), omega_j=exp(2*pi*i*j/k)",
        "general_erlang_U": "L/g+(k+1)/(2*k)+sum_j omega_j/(k*(omega_j-1))*exp(r_j*L)",
        "general_erlang_D": "L^2/(2*g)+(k+1)*L/(2*k)+sum_j omega_j/(k*(omega_j-1))"
        "*(exp(r_j*L)-1)/r_j",
        "general_erlang_terminal": "g*(1+1/k)+(g/k)*sum_j exp(r_j*L)-g*exp(-k*L/g)",
    }


def moment_expansion() -> dict:
    """Derive the integrated renewal constant and inverse threshold expansion exactly."""
    s, g, m2, m3, gap, target = sp.symbols("s g m2 m3 L R", positive=True)
    renewal_transform = 1 / (s * (g * s - m2 * s**2 / 2 + m3 * s**3 / 6))
    expansion = sp.series(renewal_transform, s, 0, 1).removeO()
    intercept = m2 / (2 * g**2)
    constant = m2**2 / (4 * g**3) - m3 / (6 * g**2)
    assert sp.simplify(expansion - (1 / (g * s**2) + intercept / s + constant)) == 0
    polynomial = gap**2 / (2 * g) + intercept * gap + constant
    approximation = -intercept * g + sp.sqrt(intercept**2 * g**2 + 2 * g * (target - constant))
    assert sp.simplify(polynomial.subs(gap, approximation) - target) == 0
    forcing_integral = -m3 / (6 * g) + intercept * m2 / 2 - constant * g
    assert sp.simplify(forcing_integral) == 0
    shape = sp.Symbol("k", positive=True, integer=True)
    erlang_constant = sp.simplify(
        constant.subs({m2: g**2 * (1 + 1 / shape), m3: g**3 * (1 + 1 / shape) * (1 + 2 / shape)})
    )
    assert sp.simplify(erlang_constant - g * (1 - 1 / shape**2) / 12) == 0
    return {
        "laplace_U_expansion": str(expansion),
        "a": str(intercept),
        "C0": str(constant),
        "D_quadratic": str(polynomial),
        "large_gap_quadratic_optimum": str(approximation),
        "first_inverse_correction": str(-intercept * g),
        "next_inverse_coefficient": str(m3 / (3 * g) - m2**2 / (4 * g**2)),
        "KRT_forcing_integral": str(forcing_integral),
        "erlang_C0": str(erlang_constant),
    }


def hyperexponential_derivation() -> dict:
    """Verify the high-variance mixture's one-transient-mode renewal and terminal forms."""
    s, gap, fast, slow = sp.symbols("s L lambda1 lambda2", positive=True)
    p = sp.Symbol("p", positive=True)
    mean = p / fast + (1 - p) / slow
    second = 2 * (p / fast**2 + (1 - p) / slow**2)
    decay = (1 - p) * fast + p * slow
    intercept = second / (2 * mean**2)
    duration = gap / mean + intercept + (1 - intercept) * sp.exp(-decay * gap)
    phi = p * fast / (s + fast) + (1 - p) * slow / (s + slow)
    transformed = 1 / (s * (1 - phi))
    candidate_transform = 1 / (mean * s**2) + intercept / s + (1 - intercept) / (s + decay)
    assert sp.cancel(candidate_transform - transformed) == 0
    terminal = (
        second / mean
        + (mean - second / mean + 1 / fast + 1 / slow) * sp.exp(-decay * gap)
        - sp.exp(-fast * gap) / fast
        - sp.exp(-slow * gap) / slow
    )
    terminal_transform = (
        second / (mean * s)
        + (mean - second / mean + 1 / fast + 1 / slow) / (s + decay)
        - 1 / (fast * (s + fast))
        - 1 / (slow * (s + slow))
    )
    assert sp.cancel(terminal_transform - (mean + sp.diff(phi, s)) / (s * (1 - phi))) == 0
    return {
        "mean": str(mean),
        "decay": str(decay),
        "a": str(intercept),
        "U": str(duration),
        "D": str(
            gap**2 / (2 * mean)
            + intercept * gap
            + (1 - intercept) * (1 - sp.exp(-decay * gap)) / decay
        ),
        "terminal_increment": str(terminal),
    }


def tail_and_random_reset() -> dict:
    """Check true four-price terminal tails and fresh random reset mean/variance effects."""
    gap, g, c, a = sp.symbols("L g c A", positive=True)
    coefficient = sp.Symbol("d", real=True)
    fraction = sp.Symbol("alpha", nonnegative=True)
    duration, integrated = 1 + gap / g, gap + gap**2 / (2 * g)
    occupation = gap * duration - integrated
    terminal = fraction * g * (2 - sp.exp(-gap / g))
    reduced = (a + c * occupation + coefficient * terminal) / duration
    balance = 2 * g - (2 * g + gap) * sp.exp(-gap / g)
    derivative = (c * integrated - a - coefficient * fraction * balance) / (g * duration**2)
    assert sp.simplify(sp.diff(reduced, gap) - derivative) == 0
    h, mean_reset, variance = sp.symbols("H mu_S var_S", nonnegative=True)
    mean_duration = 1 + (h - mean_reset) / g
    mean_integrated = h - mean_reset + ((h - mean_reset) ** 2 + variance) / (2 * g)
    reset_rate = c * h + (a - c * mean_integrated) / mean_duration
    reset_derivative = (c * mean_integrated - a) / (g * mean_duration**2)
    assert sp.simplify(sp.diff(reset_rate, h) - reset_derivative) == 0
    threshold = mean_reset - g + sp.sqrt(g**2 + 2 * g * a / c - variance)
    assert sp.simplify(mean_integrated.subs(h, threshold) - a / c) == 0
    return {
        "terminal_Z": str(terminal),
        "tail_balance": str(balance),
        "tail_corrected_derivative": str(derivative),
        "random_reset_EU": str(mean_duration),
        "random_reset_ED": str(mean_integrated),
        "random_reset_derivative": str(reset_derivative),
        "random_reset_threshold": str(threshold),
        "reset_variance_derivative": str(sp.diff(threshold, variance)),
    }


def dimensionless_results() -> dict:
    """Evaluate analytical comparative statics, with no sample trajectories or fitted laws."""
    laws = {
        "exponential": ErlangRenewal(1),
        "erlang2": ErlangRenewal(1, 2),
        "erlang3": ErlangRenewal(1, 3),
        "erlang8": ErlangRenewal(1, 8),
        "hyperexp_cv2": HyperexponentialRenewal.from_mean_cv(1, 2),
    }
    rows = []
    for fee_ratio in (0.2, 2.0, 50.0, 500.0):
        fees = RenewalFees(0, fee_ratio, 1, 0)
        for name, law in laws.items():
            optimum = optimal_gap(law, fees)
            assert math.isclose(
                law.statistics(optimum).integrated_duration, fee_ratio, rel_tol=1e-10, abs_tol=1e-10
            )
            approximation = asymptotic_optimal_gap(law.moments, fee_ratio)
            delta = max(1e-7, optimum * 1e-4)
            assert rate(law, fees, optimum) <= rate(law, fees, optimum + delta) + 1e-10
            assert rate(law, fees, optimum) <= rate(law, fees, optimum - delta) + 1e-10
            assert abs(rate_derivative(law, fees, optimum)) < 1e-9
            rows.append(
                {
                    "law": name,
                    "A_over_cg": fee_ratio,
                    "CV_squared": law.moments.cv_squared,
                    "optimum_L_over_g": optimum,
                    "fluid_L_over_g": math.sqrt(2 * fee_ratio),
                    "moment_L_over_g": approximation,
                    "moment_relative_gap_error": (approximation - optimum) / optimum,
                    "C0_over_g": law.moments.integrated_constant,
                }
            )
    base_fees = RenewalFees(0, 50, 1, 0, terminal_coefficient=-2.5)
    uncorrected = optimal_gap(laws["exponential"], base_fees)
    corrected = optimal_gap(laws["exponential"], base_fees, terminal_fraction=0.4)
    assert corrected < uncorrected
    assert (
        abs(rate_derivative(laws["exponential"], base_fees, corrected, terminal_fraction=0.4))
        < 1e-9
    )
    zero_law = ErlangRenewal(1, 2, zero_probability=0.2)
    positive_law = ErlangRenewal(1.25, 2)
    for gap in (0.1, 1, 10):
        zero, positive = zero_law.statistics(gap), positive_law.statistics(gap)
        assert math.isclose(zero.duration * 0.8, positive.duration, rel_tol=1e-12)
        assert math.isclose(
            zero.integrated_duration * 0.8, positive.integrated_duration, rel_tol=1e-12
        )
        assert math.isclose(zero.terminal_increment, positive.terminal_increment, rel_tol=1e-12)
    reset_mean = random_reset_exponential_optimum(1, 20, 0, 50, 1, 24)
    reset_variable = random_reset_exponential_optimum(1, 20, 4, 50, 1, 24)
    assert reset_variable < reset_mean
    physical = physical_cache_fees(
        Pricing(),
        reset_tokens=100,
        surviving_base=20,
        summary_tokens=10,
        mean_growth=1,
        mean_output=0.4,
    )
    billed_not_retained = physical_cache_fees(
        Pricing(),
        reset_tokens=100,
        surviving_base=20,
        summary_tokens=10,
        mean_growth=1,
        mean_output=2,
    )
    assert billed_not_retained.ordinary_baseline > physical.ordinary_baseline
    return {
        "status": "dimensionless analytical comparative statics, not workload measurements",
        "rows": rows,
        "tail_uncorrected_gap": uncorrected,
        "tail_corrected_gap": corrected,
        "random_reset_mean_plugin_threshold": reset_mean,
        "random_reset_variable_threshold": reset_variable,
        "physical_four_price_coefficients": vars(physical),
    }


def main() -> None:
    """Persist checkable exact expressions and deterministic numerical law evaluations."""
    started = time.perf_counter()
    result = {
        "symbolic_laws": symbolic_laws(),
        "moment_expansion": moment_expansion(),
        "hyperexponential": hyperexponential_derivation(),
        "tail_and_random_reset": tail_and_random_reset(),
        "dimensionless_comparative_statics": dimensionless_results(),
    }
    result["runtime_seconds"] = time.perf_counter() - started
    directory = Path(".cache/renewal-closed-form")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
