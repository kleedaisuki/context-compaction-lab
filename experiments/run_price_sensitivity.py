"""Execute theory-led price and mechanism sensitivity on pinned community data.

Only prices are varied in price-only groups: token totals are simulated once and
repriced without regenerating stochastic work. Cache/material/timing groups are
separate declared interventions, with common action-index fields and fresh paired
confirmation of analytic versus unchanged thresholds. No paid model calls.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, replace
from pathlib import Path

import matplotlib
import numpy as np
from scipy.optimize import brentq

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from renewal_community_study import fields

from context_compaction_lab.config import Pricing
from context_compaction_lab.price_sensitivity import (
    PRICE_CATEGORIES,
    core_sensitivity,
    expected_category_rates,
    price_array,
    reprice_categories,
)
from context_compaction_lab.renewal_numerics import (
    RenewalLedger,
    analytic_rates,
    empirical_renewal,
    simulate_renewal_ledger,
)


def case_result(renewal: dict, ledger: RenewalLedger, output_mean: float, old_h: float) -> dict:
    """Evaluate one declared intervention, keeping marked minima distinct from core gradients."""
    curve = analytic_rates(renewal, ledger, output_mean)
    basis = expected_category_rates(renewal, ledger, output_mean)
    rates = basis @ price_array(ledger.prices)
    assert np.max(np.abs(rates - curve["rates"])) < 1e-12
    best = int(np.argmin(rates))
    old = int(np.searchsorted(curve["thresholds"], old_h))
    if old_h <= ledger.reset or old >= len(rates):
        raise ValueError("The unchanged threshold must remain feasible in the study domain.")
    usage = basis[best]
    shares = price_array(ledger.prices) * usage / rates[best]
    try:
        sensitivity = asdict(core_sensitivity(renewal, ledger))
    except ValueError as error:
        sensitivity = {"nonsmooth_or_unbracketed": str(error)}
    return {
        "ledger": asdict(ledger),
        "marked_threshold": float(curve["thresholds"][best]),
        "marked_rate": float(rates[best]),
        "core_threshold": float(curve["core_root_threshold"]),
        "old_threshold": old_h,
        "old_policy_rate": float(rates[old]),
        "old_policy_regret_fraction": float(rates[old] / rates[best] - 1),
        "optimized_category_tokens_per_call": dict(
            zip(PRICE_CATEGORIES, usage.tolist(), strict=True)
        ),
        "optimized_bill_price_elasticities": dict(
            zip(PRICE_CATEGORIES, shares.tolist(), strict=True)
        ),
        "core_sensitivity": sensitivity,
        "right_tail_margin": float(curve["global_right_tail_margin"]),
    }


def build_cases(price_metadata: dict) -> list[tuple[str, str, RenewalLedger, float]]:
    """Declare semantic intervention paths before stochastic confirmation."""
    base = RenewalLedger()
    cases = [
        (
            entry["id"],
            "official_price_only",
            replace(base, prices=Pricing(**entry["pricing_per_token"])),
            1.0,
        )
        for entry in price_metadata["official_scenarios"]
    ]
    for component in PRICE_CATEGORIES:
        for factor in (0.8, 1.2):
            prices = replace(base.prices, **{component: getattr(base.prices, component) * factor})
            cases.append(
                (
                    f"price_{component}_{factor:g}",
                    "local_price_only",
                    replace(base, prices=prices),
                    1.0,
                )
            )
    families = {
        "miss20_write": (replace(base, cache_hit=0.8), "write", (0.8, 1.0, 1.2)),
        "stable_heavy_write": (
            replace(base, stable_base=64000, summary=100),
            "write",
            (0.8, 1.0, 1.2),
        ),
        "stable_heavy_precall_write": (
            replace(base, stable_base=64000, summary=100, tail_fraction=0),
            "write",
            (0.8, 1.0, 1.2),
        ),
        "stable_heavy_miss_read": (
            replace(base, stable_base=64000, summary=100, cache_hit=0.5),
            "read",
            (0.5, 1.0, 4.0),
        ),
    }
    for family, (ledger, component, factors) in families.items():
        for factor in factors:
            prices = replace(
                ledger.prices, **{component: getattr(ledger.prices, component) * factor}
            )
            cases.append(
                (
                    f"{family}_{factor:g}",
                    "declared_sign_regime",
                    replace(ledger, prices=prices),
                    1.0,
                )
            )
    interventions = {
        "reclassify_stable20k": replace(base, stable_base=40000),
        "add_stable20k": replace(base, stable_base=40000, reset=85588),
        "add_volatile20k": replace(base, reset=85588),
        "summary20k_preserve": replace(base, summary=20000, reset=81206),
        "all_growth_precall": replace(base, tail_fraction=0),
    }
    cases.extend(
        (name, "material_or_timing_path", ledger, 1.0) for name, ledger in interventions.items()
    )
    cases.append(("growth_scale2", "whole_growth_law_scale", base, 2.0))
    entries = {entry["id"]: entry for entry in price_metadata["official_scenarios"]}
    for name, tariff, q in (
        ("tariff_short_q80", "sonnet55_5m", 0.8),
        ("tariff_long_q80", "sonnet55_1h", 0.8),
        ("tariff_long_q95", "sonnet55_1h", 0.95),
    ):
        price = Pricing(**entries[tariff]["pricing_per_token"])
        cases.append((name, "cache_tariff_joint", replace(base, prices=price, cache_hit=q), 1.0))
    return cases


def cache_break_even(renewal: dict, output_mean: float, price_metadata: dict) -> list[dict]:
    """Solve controlled long-TTL tariff break-even in q, NOT a measured TTL effect."""
    entries = {entry["id"]: entry for entry in price_metadata["official_scenarios"]}
    short = Pricing(**entries["sonnet55_5m"]["pricing_per_token"])
    long = Pricing(**entries["sonnet55_1h"]["pricing_per_token"])
    rows = []
    for q0 in (0.5, 0.8, 0.9, 0.95, 0.98, 1.0):
        ledger = replace(RenewalLedger(), cache_hit=q0, prices=short)
        b0 = expected_category_rates(renewal, ledger, output_mean)
        rates0 = b0 @ price_array(short)
        index = int(np.argmin(rates0))
        target = float(rates0[index])
        # For a fixed H, the physical rate is affine in q. This gives an exact
        # break-even threshold in the declared independent-cache protocol.
        cold = expected_category_rates(
            renewal, replace(ledger, cache_hit=0), output_mean
        ) @ price_array(long)
        warm = expected_category_rates(
            renewal, replace(ledger, cache_hit=1), output_mean
        ) @ price_array(long)
        slope = warm[index] - cold[index]
        fixed_q = q0 + (float(b0[index] @ price_array(long)) - target) / (-slope)

        def optimized_difference(q: float) -> float:
            """Evaluate the reoptimized long-tariff invoice minus the short-tariff target."""
            return float(np.min(cold + q * (warm - cold)) - target)

        feasible = optimized_difference(1) <= 0
        optimal_q = float(brentq(optimized_difference, q0, 1, xtol=1e-12)) if feasible else None
        rows.append(
            {
                "short_q": q0,
                "short_minimum_rate": target,
                "short_threshold": float(renewal["gaps"][index] + ledger.reset),
                "long_q_break_even_fixed_threshold": float(fixed_q) if fixed_q <= 1 else None,
                "long_q_break_even_reoptimized": optimal_q,
                "long_best_rate_at_q1": float(np.min(warm)),
                "meaning": "Required q gain under fixed timing/growth; no actual TTL gain inferred",
            }
        )
    return rows


def price_envelope_checks(renewal: dict, ledger: RenewalLedger, output_mean: float) -> dict:
    """Check exact affine repricing and revealed preference, not workload-fit quality."""
    basis = expected_category_rates(renewal, ledger, output_mean)
    p = price_array(ledger.prices)
    j0 = basis @ p
    scaled = basis @ (2 * p / 3)
    assert np.max(abs(scaled - 2 * j0 / 3)) < 1e-12
    usage_monotone = {}
    for component, name in enumerate(PRICE_CATEGORIES):
        selected = []
        for factor in (0.25, 0.5, 0.8, 1.0, 1.2, 2.0, 4.0):
            changed = p.copy()
            changed[component] *= factor
            selected.append(float(basis[np.argmin(basis @ changed), component]))
        assert np.max(np.diff(selected)) < 1e-6
        usage_monotone[name] = selected
    left, right = p * np.array([1.0, 0.5, 2.0, 1.0]), p * np.array([1.0, 2.0, 0.5, 1.0])
    concavity = []
    for mixing in np.linspace(0, 1, 21):
        gap = np.min(basis @ (mixing * left + (1 - mixing) * right)) - (
            mixing * np.min(basis @ left) + (1 - mixing) * np.min(basis @ right)
        )
        assert gap > -1e-12
        concavity.append(float(gap))
    return {
        "radial_rate_max_error": float(np.max(abs(scaled - 2 * j0 / 3))),
        "scaled_selected_threshold_equal": bool(np.argmin(j0) == np.argmin(scaled)),
        "own_usage_under_increasing_price": usage_monotone,
        "concavity_min_margin": min(concavity),
    }


def confirmation(cases: list, rows: dict, pool: dict, replicates: int, calls: int) -> dict:
    """Confirm analytic retuning savings with shared raw integer token trajectories."""
    results = {}
    # Price-only variants share a mechanism group and therefore a SINGLE
    # simulated ledger. Price changes never generate new stochastic work.
    groups = {}
    for name, _, ledger, growth_scale in cases:
        key = (
            ledger.reset,
            ledger.summary,
            ledger.stable_base,
            ledger.cache_hit,
            ledger.tail_fraction,
            growth_scale,
        )
        groups.setdefault(key, []).append((name, ledger))
    for mode, seed in (("iid", 2026102601), ("block", 2026102602)):
        growth, output, uniform = fields(pool, mode, seed, replicates, calls)
        selected_samples = {}
        for key, group in groups.items():
            common = group[0][1]
            thresholds = np.unique(
                [
                    rows[name][field]
                    for name, _ in group
                    for field in ("marked_threshold", "old_threshold")
                ]
            )
            print(
                f"Confirming {mode}: {len(group)} prices / {len(thresholds)} thresholds", flush=True
            )
            billed = simulate_renewal_ledger(
                growth * key[-1], output, uniform < common.cache_hit, common, thresholds
            )
            categories = np.stack([billed[name] for name in PRICE_CATEGORIES], axis=-1)
            for name, ledger in group:
                prices = reprice_categories(categories, ledger.prices) / calls
                old = int(np.searchsorted(thresholds, rows[name]["old_threshold"]))
                new = int(np.searchsorted(thresholds, rows[name]["marked_threshold"]))
                difference = prices[:, new] - prices[:, old]
                old_mean, new_mean = float(prices[:, old].mean()), float(prices[:, new].mean())
                selected_samples[name] = prices[:, new]
                results[f"{mode}/{name}"] = {
                    "retuned_minus_old_usd_per_call": float(difference.mean()),
                    "paired_mc95_halfwidth": float(
                        1.96 * difference.std(ddof=1) / np.sqrt(replicates)
                    ),
                    "old_rate": old_mean,
                    "retuned_rate": new_mean,
                    "retuning_saving_fraction": 1 - new_mean / old_mean,
                    "price_gradient_at_retuned": dict(
                        zip(PRICE_CATEGORIES, categories[:, new].mean(axis=0).tolist(), strict=True)
                    ),
                    "gradient_unit": (
                        "Expected billed tokens over full finite horizon, conditional pool"
                    ),
                }
        for name in ("tariff_long_q80", "tariff_long_q95"):
            delta = selected_samples[name] - selected_samples["tariff_short_q80"]
            results[f"coupled_tariff/{mode}/{name}"] = {
                "long_minus_short_usd_per_call": float(delta.mean()),
                "paired_mc95_halfwidth": float(1.96 * delta.std(ddof=1) / np.sqrt(replicates)),
                "short_rate": float(selected_samples["tariff_short_q80"].mean()),
                "long_rate": float(selected_samples[name].mean()),
                "meaning": "Total tariff-plus-declared-q effect, not measured real TTL performance",
            }
    return results


def phase_map(renewal: dict, output_mean: float, destination: Path) -> dict:
    """Plot full marked write-price response against cache quality, with explicit finite changes."""
    qs = np.linspace(0.65, 1.0, 36)
    factors = np.linspace(0.5, 2.0, 31)
    thresholds = np.zeros((len(qs), len(factors)))
    direction = np.zeros_like(thresholds)
    base = RenewalLedger()
    for i, q in enumerate(qs):
        for j, factor in enumerate(factors):
            ledger = replace(
                base,
                cache_hit=float(q),
                prices=replace(base.prices, write=base.prices.write * factor),
            )
            curve = analytic_rates(renewal, ledger, output_mean)
            thresholds[i, j] = curve["marked_minimum_threshold"]
            changed = replace(
                ledger, prices=replace(ledger.prices, write=ledger.prices.write * 1.05)
            )
            direction[i, j] = (
                analytic_rates(renewal, changed, output_mean)["marked_minimum_threshold"]
                - thresholds[i, j]
            )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    extent = [factors[0], factors[-1], qs[0], qs[-1]]
    image = axes[0].imshow(thresholds / 1000, origin="lower", aspect="auto", extent=extent)
    fig.colorbar(image, ax=axes[0], label="Threshold (thousand tokens)")
    image = axes[1].imshow(
        direction,
        origin="lower",
        aspect="auto",
        extent=extent,
        cmap="coolwarm",
        vmin=-1500,
        vmax=1500,
    )
    fig.colorbar(image, ax=axes[1], label="Threshold change after +5% write price")
    for ax in axes:
        ax.set(
            xlabel="Write price / baseline write price", ylabel="Independent cache hit probability"
        )
    fig.tight_layout()
    fig.savefig(destination / "write-price-cache-phase.png", dpi=170)
    plt.close(fig)
    default_column = int(np.argmin(abs(factors - 1)))
    return {
        "q_grid": qs.tolist(),
        "write_factor_grid": factors.tolist(),
        "baseline_write_column_threshold_change": direction[:, default_column].tolist(),
        "quantity": "5% finite write-price change, not an ordinary derivative at atomic switches",
    }


def main() -> None:
    """Deliver analytic sensitivities, quoted-price projections and paired confirmations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=512)
    parser.add_argument("--calls", type=int, default=4000)
    args = parser.parse_args()
    if args.replicates < 2 or args.calls < 1:
        parser.error("Use at least two trajectory replicates and positive ordinary calls.")
    root = Path(__file__).resolve().parents[1]
    destination = root / ".cache" / "price-sensitivity"
    destination.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    metadata = json.loads((root / "docs/research/price-scenarios.json").read_text())
    pool = dict(np.load(root / ".cache/renewal-calibration/growth-pool.npz"))
    calibration = json.loads((root / ".cache/renewal-calibration/calibration.json").read_text())
    weights = pool["block_marginal_weights"]
    output_mean = float(np.average(pool["previous_output_tokens"], weights=weights))
    renewals = {
        scale: empirical_renewal(pool["values"] * scale, weights, 5, 250000) for scale in (1.0, 2.0)
    }
    base = RenewalLedger()
    old_h = float(analytic_rates(renewals[1.0], base, output_mean)["marked_minimum_threshold"])
    cases = build_cases(metadata)
    rows = {}
    entries = {entry["id"]: entry for entry in metadata["official_scenarios"]}
    short = Pricing(**entries["sonnet55_5m"]["pricing_per_token"])
    tariff_reference = float(
        analytic_rates(renewals[1.0], replace(base, prices=short, cache_hit=0.8), output_mean)[
            "marked_minimum_threshold"
        ]
    )
    for name, kind, ledger, scale in cases:
        reference = old_h
        if kind == "declared_sign_regime":
            # Price-only comparisons must start from this SAME mechanism's
            # baseline price optimum, not a global reference with different q/B.
            reference = float(
                analytic_rates(renewals[scale], replace(ledger, prices=base.prices), output_mean)[
                    "marked_minimum_threshold"
                ]
            )
        elif kind == "cache_tariff_joint":
            reference = tariff_reference
        rows[name] = case_result(renewals[scale], ledger, output_mean, reference)
    for name, kind, _, scale in cases:
        rows[name]["intervention"] = kind
        rows[name]["growth_scale"] = scale
    checks = price_envelope_checks(renewals[1.0], base, output_mean)
    gradients = rows["sonnet46_5m"]["core_sensitivity"]
    checks["core_gap_price_elasticity_sum"] = sum(gradients["gap_price_elasticity"])
    assert abs(checks["core_gap_price_elasticity_sum"]) < 1e-10
    confirmations = confirmation(cases, rows, pool, args.replicates, args.calls)
    breaks = cache_break_even(renewals[1.0], output_mean, metadata)
    phase = phase_map(renewals[1.0], output_mean, destination)
    result = {
        "source": calibration["source"],
        "price_quote_date": metadata["as_of"],
        "design": {
            "replicates": args.replicates,
            "calls": args.calls,
            "quantum_tokens": 5,
            "seeds": {"iid": 2026102601, "block": 2026102602},
            "price_only": "Simulate one immutable token ledger per mechanism, then reprice",
            "uncertainty": "Paired conditional MC, not population/cross-model uncertainty",
            "cache_tariff": "Price and hypothetical q sensitivity; no measured TTL survival",
        },
        "analytic_cases": rows,
        "independent_confirmation": confirmations,
        "cache_tariff_break_even": breaks,
        "price_envelope_checks": checks,
        "write_price_cache_phase": phase,
        "runtime_seconds": time.perf_counter() - started,
    }
    encoded = json.dumps(result, indent=2, allow_nan=False) + "\n"
    (destination / "results.json").write_text(encoded, encoding="utf-8")
    (root / "docs/research/price-sensitivity-results.json").write_text(encoded, encoding="utf-8")
    print(f"Completed {len(rows)} cases in {result['runtime_seconds']:.2f}s", flush=True)


if __name__ == "__main__":
    main()
