"""Embed detailed experimental exhibits from maintained research aggregates.

This companion to build_paper_figures.py updates a separate delimited source
block. It reprices already executed ledgers, evaluates existing exact jump
expressions for presentation, and never resamples trajectories or calls a model.
The manuscript remains standalone: tables and vector plots are inline TeX.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.special import ndtr

BEGIN = "% BEGIN GENERATED EXPERIMENT EXHIBITS"
END = "% END GENERATED EXPERIMENT EXHIBITS"


def table(name: str, columns: str, header: str, rows: list[str]) -> str:
    """Encode a small readable booktabs exhibit for an authored table float."""
    body = "\\\\\n".join(rows)
    return (
        f"\\newcommand{{\\{name}}}{{%\n"
        f"\\begin{{tabular}}{{@{{}}{columns}@{{}}}}\\toprule\n"
        + header
        + "\\\\\\midrule\n"
        + body
        + "\\\\\\bottomrule\n\\end{tabular}}\n"
    )


def row(values: list[str]) -> str:
    """Keep table cells distinct from row separators."""
    return " & ".join(values)


def money_interval(estimate: dict) -> str:
    """Show a mean with its reported conditional Monte Carlo halfwidth."""
    width = (estimate["ci_high"] - estimate["ci_low"]) / 2
    return f"${estimate['mean']:.4f}\\pm{width:.4f}$"


def coordinates(xs: list[float], ys: list[float]) -> str:
    """Preserve paired plotted observations while avoiding false precision."""
    return " ".join(f"({x:.8g},{y:.8g})" for x, y in zip(xs, ys, strict=True))


def working_exhibits(working: dict) -> str:
    """Report restoration policies, sensitivities, budgets and fine-grid slopes."""
    labels = {
        "eager_cold": "Eager, cold base",
        "first_use_cold": "First use, cold base",
        "eager_warm": "Eager, warm base",
        "first_use_warm": "First use, warm base",
        "preserve_warm": "Retain files and guards",
        "preserve_guard_lost": "Retain files, lose guards",
        "eager_round": "Eager + recovery model",
        "first_use_round": "First use + recovery model",
    }
    rows = []
    for key, label in labels.items():
        policy = working["coarse_cases"]["phase"]["policies"][key]
        diagnostics = policy["holdout"]["diagnostics"]
        rows.append(
            row(
                [
                    label,
                    f"{policy['threshold'] / 1000:.0f}",
                    money_interval(policy["holdout"]["expected_cost_usd"]),
                    f"{diagnostics['reload_payload_tokens'] / 1000:.1f}",
                ]
            )
        )
    tex = table("PaperWorkingPolicies", "lrrr", "Policy & $H$ (k) & USD/task & Reload (k)", rows)
    rows = []
    for key, label in (
        ("phase", "Phase-local"),
        ("diffuse", "Diffuse demand"),
        ("mandatory", "All files mandatory"),
        ("churn", "Revision churn .02"),
        ("delay", "Both extra delays 360s"),
        ("base0", "Stable base 0"),
        ("base40", "Stable base 40k"),
        ("short", "40 ordinary actions"),
        ("strict", "Strict trigger"),
    ):
        cells = [label]
        for policy_name in ("eager_warm", "first_use_warm"):
            actual_name = policy_name
            if key == "strict":
                actual_name = "strict_eager" if policy_name == "eager_warm" else "strict_first_use"
            policy = working["coarse_cases"][key]["policies"][actual_name]
            cells.extend(
                [
                    f"{policy['threshold'] / 1000:.0f}",
                    f"{policy['holdout']['expected_cost_usd']['mean']:.4f}",
                ]
            )
        rows.append(row(cells))
    tex += table(
        "PaperWorkingMechanisms",
        "lrrrr",
        "Intervention & $H_E$ (k) & USD$_E$ & $H_F$ (k) & USD$_F$",
        rows,
    )
    rows = []
    for budget in (0, 12000, 20000, 40000, 64000):
        cells = [f"{budget / 1000:g}"]
        for delay in (0, 360):
            policy = working["retention_cases"][f"delay_{delay}"]["policies"][f"retain_{budget}"]
            cells.extend(
                [
                    f"{policy['threshold'] / 1000:.0f}",
                    money_interval(policy["holdout"]["expected_cost_usd"]),
                ]
            )
        rows.append(row(cells))
    tex += table(
        "PaperRetentionGrid",
        "rrrrr",
        "Budget (k) & $H_0$ (k) & USD$_0$ & $H_{360}$ (k) & USD$_{360}$",
        rows,
    )
    rows = []
    for name, points in (
        ("phase", (68000, 74000, 78000, 86000)),
        ("mandatory", (116000, 126000, 138000)),
    ):
        curve = working["fine_cases"][name]["policies"]["first_use_warm"]["discovery_curve"]
        for point in points:
            value = next(x for x in curve if x["threshold_tokens"] == point)
            slope = value["paired_secant_usd_per_token"]
            mean, low, high = (1000 * slope[k] for k in ("mean", "ci_low", "ci_high"))
            rows.append(
                row(
                    [
                        "Phase-local" if name == "phase" else "Mandatory",
                        f"{point / 1000:.0f}",
                        f"${mean:+.5f}$",
                        f"$[{low:+.5f},{high:+.5f}]$",
                    ]
                )
            )
    tex += table("PaperWorkingSlopes", "lrrr", "Law & $H$ (k) & USD/1k & MC95 interval", rows)
    tex += r"""\newcommand{\PaperWorkingCurves}{%
\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.35cm},
width=.43\textwidth,height=4.6cm,xlabel={$H$ (thousand tokens)},
ylabel={Expense above own grid minimum (\%)},ymin=0,ymax=5]
"""
    for name, title, color in (
        ("phase", "Phase-local restoration", "inkblue"),
        ("mandatory", "Mandatory restoration", "warmred"),
    ):
        curve = working["fine_cases"][name]["policies"]["first_use_warm"]["discovery_curve"]
        minimum = min(x["expected_cost_usd"]["mean"] for x in curve)
        xs = [x["threshold_tokens"] / 1000 for x in curve]
        ys = [100 * (x["expected_cost_usd"]["mean"] / minimum - 1) for x in curve]
        tex += f"\\nextgroupplot[title={{{title}}}]\n"
        tex += f"\\addplot[{color},thick,mark=*] coordinates {{{coordinates(xs, ys)}}};\n"
        tex += f"\\addplot[black,dashed] coordinates {{({min(xs)},1)({max(xs)},1)}};\n"
    tex += "\\end{groupplot}\n\\end{tikzpicture}}\n"
    tex += r"""\newcommand{\PaperRetentionCurves}{%
\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.3cm},
width=.44\textwidth,height=4.6cm,xlabel={Retained file budget (thousand tokens)},
ylabel={USD / 400-action task},xmin=-2,xmax=66]
"""
    for delay, color in ((0, "inkblue"), (360, "warmred")):
        tex += f"\\nextgroupplot[title={{{delay}s extra recovery delay}}]\n"
        points = []
        for budget in (0, 12000, 20000, 40000, 64000):
            policy = working["retention_cases"][f"delay_{delay}"]["policies"][f"retain_{budget}"]
            estimate = policy["holdout"]["expected_cost_usd"]
            width = (estimate["ci_high"] - estimate["ci_low"]) / 2
            points.append(f"({budget / 1000:g},{estimate['mean']:.8g}) +- (0,{width:.8g})")
        tex += (
            f"\\addplot[{color},thick,mark=*,error bars/.cd,y dir=both,y explicit]"
            " coordinates {" + " ".join(points) + "};\n"
        )
    return tex + "\\end{groupplot}\n\\end{tikzpicture}}\n"


def renewal_exhibits(results: dict) -> str:
    """Separate law approximation, marked accounting and horizon confirmation."""
    base = results["analytic_predictions"]["warm_base20k"]
    rows = [
        row([label, f"{base[key] / 1000:.3f}"])
        for key, label in (
            ("fluid_threshold", "Fluid mean-growth relaxation"),
            ("exponential_core_threshold", "Exponential, matched mean, core"),
            (
                "moment_matched_hyperexponential_core_threshold",
                "Hyperexponential, two moments, core",
            ),
            ("first_moment_correction_threshold", "Second-moment asymptotic, core"),
            ("third_moment_threshold", "Third-moment asymptotic, core"),
            ("core_root_threshold", "Empirical renewal, core"),
            ("marked_minimum_threshold", "Empirical renewal, marked"),
        )
    ]
    tex = table("PaperRenewalMethods", "lr", "Method/accounting & $H$ (k)", rows)
    rows = []
    for key, value in results["independent_confirmation"].items():
        mode, count = key.split("/N")
        delta, width = (
            value[k] for k in ("selected_minus_analytic_usd_per_call", "mc95_halfwidth")
        )
        rows.append(
            row(
                [
                    "IID" if mode == "iid" else "Blocks",
                    count,
                    f"{value['selected_threshold'] / 1000:.3f}",
                    f"{value['selected_rate']:.6f}",
                    f"${delta * 1000:+.5f}\\pm{width * 1000:.5f}$",
                ]
            )
        )
    tex += table(
        "PaperHorizonConfirmation",
        "lrrrr",
        r"Law & $N$ & $H$ (k) & USD/action & $10^3\Delta$ USD/action",
        rows,
    )
    rows = []
    for key, label in (
        ("warm_base20k", "Baseline"),
        ("warm_base0", "No stable base"),
        ("hit80pct", "$q=.8$"),
        ("hit50pct", "$q=.5$"),
        ("summary20k", "Summary 20k"),
        ("pre_call_growth", "$\\theta=0$"),
    ):
        value = results["analytic_predictions"][key]
        rows.append(
            row(
                [
                    label,
                    f"{value['marked_minimum_threshold'] / 1000:.3f}",
                    f"{value['marked_minimum_rate']:.6f}",
                    f"{value['duration_at_minimum']:.2f}",
                    f"{value['terminal_growth_at_minimum']:.1f}",
                ]
            )
        )
    return tex + table(
        "PaperRenewalScenarios",
        "lrrrr",
        "Intervention & $H$ (k) & USD/action & $U$ & $z$ (tokens)",
        rows,
    )


def price_exhibits(results: dict, catalog: dict) -> str:
    """Retain complete quoted-vector selections and mechanism-specific references."""
    base = results["analytic_cases"]["sonnet46_5m"]
    rows = []
    for index, category in enumerate(("input", "write", "read", "output")):
        changed = results["analytic_cases"][f"price_{category}_1.2"]
        rows.append(
            row(
                [
                    category.capitalize(),
                    f"{base['core_sensitivity']['gap_price_elasticity'][index]:+.6f}",
                    f"{base['optimized_bill_price_elasticities'][category]:.6f}",
                    f"{changed['marked_threshold'] / 1000:.3f}",
                ]
            )
        )
    tex = table(
        "PaperPriceElasticities",
        "lrrr",
        r"Price & Core gap elasticity & Bill elasticity & $H_{+20\%}$ (k)",
        rows,
    )
    rows = []
    labels = (
        ("price_input_0.8", "Input $\\times.8$"),
        ("price_input_1.2", "Input $\\times1.2$"),
        ("price_write_0.8", "Write $\\times.8$"),
        ("price_write_1.2", "Write $\\times1.2$"),
        ("price_read_0.8", "Read $\\times.8$"),
        ("price_read_1.2", "Read $\\times1.2$"),
        ("price_output_0.8", "Output $\\times.8$"),
        ("price_output_1.2", "Output $\\times1.2$"),
        ("miss20_write_1.2", "$q=.8$, write $\\times1.2$"),
        ("stable_heavy_write_1.2", "Thin volatile, write $\\times1.2$"),
        ("stable_heavy_precall_write_1.2", "Thin, $\\theta=0$, write $\\times1.2$"),
        ("stable_heavy_miss_read_4", "Thin, $q=.5$, read $\\times4$"),
        ("reclassify_stable20k", "Reclassify stable 20k"),
        ("add_stable20k", "Add stable 20k"),
        ("add_volatile20k", "Add volatile 20k"),
        ("summary20k_preserve", "Summary 20k, preserve material"),
        ("all_growth_precall", "All growth pre-call"),
        ("growth_scale2", "Whole growth law $\\times2$"),
    )
    for key, label in labels:
        value = results["analytic_cases"][key]
        confirm = results["independent_confirmation"][f"block/{key}"]
        delta, width = (
            confirm[k] for k in ("retuned_minus_old_usd_per_call", "paired_mc95_halfwidth")
        )
        rows.append(
            row(
                [
                    label,
                    f"{value['old_threshold'] / 1000:.3f}",
                    f"{value['marked_threshold'] / 1000:.3f}",
                    f"{100 * value['old_policy_regret_fraction']:.4f}",
                    f"${delta * 1000:+.5f}\\pm{width * 1000:.5f}$",
                ]
            )
        )
    tex += table(
        "PaperPriceControls",
        "lrrrr",
        r"Intervention & Old $H$ (k) & New $H$ (k) & Excess (\%) & Block $10^3\Delta$",
        rows,
    )
    rows_gpt, rows_other = [], []
    for quote in catalog["official_scenarios"]:
        key = quote["id"]
        value = results["analytic_cases"][key]
        rates = quote["prices_per_million_usd"]
        prices = ",".join(f"{rates[x]:g}" for x in ("input", "write", "read", "output"))
        label = key.replace("_", " ").replace("singapore", "SG").replace("beijing", "BJ")
        cells = [label, f"$({prices})$"]
        for q in (0.8, 0.95, 1):
            scenario = key + (f"__q{q:g}" if q != 1 else "")
            cells.append(f"{results['analytic_cases'][scenario]['marked_threshold'] / 1000:.3f}")
        confirm = results["independent_confirmation"][f"block/{key}"]
        cells.append(f"{100 * confirm['retuning_saving_fraction']:.3f}")
        (rows_gpt if quote["provider"] == "OpenAI" else rows_other).append(row(cells))
        assert abs(sum(value["optimized_bill_price_elasticities"].values()) - 1) < 1e-9
    header = (
        r"Quoted configuration & USD/M $(i,w,r,o)$ & $H_{.8}$ (k) & $H_{.95}$ (k)"
        r" & $H_1$ (k) & Block saving (\%)"
    )
    tex += table("PaperCatalogGPT", "llrrrr", header, rows_gpt)
    tex += table("PaperCatalogOther", "llrrrr", header, rows_other)
    rows = []
    for value in results["cache_tariff_break_even"]:
        fixed, retuned = (
            value[k]
            for k in (
                "long_q_break_even_fixed_threshold",
                "long_q_break_even_reoptimized",
            )
        )
        rows.append(
            row(
                [
                    f"{value['short_q']:.2f}",
                    "--" if fixed is None else f"{fixed:.6f}",
                    "--" if retuned is None else f"{retuned:.6f}",
                ]
            )
        )
    tex += table(
        "PaperTariffBreakEven",
        "rrr",
        "Short $q$ & Required $q$, old line & Required $q$, retuned",
        rows,
    )
    rows = []
    for model in ("qwen38max_singapore", "qwen38flash_singapore", "qwen37plus_singapore_short"):
        for q in (0.8, 0.95, 1):
            suffix = f"__q{q:g}" if q != 1 else ""
            explicit, implicit = (
                results["analytic_cases"][f"{model}_{mode}{suffix}"]["marked_rate"]
                for mode in ("explicit", "implicit")
            )
            confirm = results["independent_confirmation"][
                f"coupled_cache_mode/block/{model}_explicit{suffix}"
            ]
            # The coupled comparison uses a dedicated total-expense schema.
            total_delta = confirm["explicit_minus_implicit_usd_per_call"]
            rows.append(
                row(
                    [
                        model.replace("_singapore", " SG").replace("_short", " short"),
                        f"{q:g}",
                        f"{100 * (explicit / implicit - 1):+.3f}",
                        f"${total_delta * 1000:+.5f}"
                        f"\\pm{confirm['paired_mc95_halfwidth'] * 1000:.5f}$",
                    ]
                )
            )
    return tex + table(
        "PaperCacheModes",
        "lrrr",
        r"Qwen quoted model & $q$ & Explicit excess (\%) & Block $10^3\Delta$",
        rows,
    )


def finite_exhibits(supplement: dict) -> str:
    """Render exhaustive controls, certified price faces and continuum probes."""
    rows = []
    for value in supplement["closed_law_controls"]["rows"]:
        if value["A_over_cg"] not in (0.2, 2, 500):
            continue
        rows.append(
            row(
                [
                    value["law"].replace("_", " "),
                    f"{value['A_over_cg']:g}",
                    f"{value['CV_squared']:.3f}",
                    f"{value['optimum_L_over_g']:.6f}",
                    f"{value['fluid_L_over_g']:.6f}",
                    f"{100 * value['moment_relative_gap_error']:+.4f}",
                ]
            )
        )
    tex = table(
        "PaperClosedLawControls",
        "lrrrrr",
        r"Law & $A/(cg)$ & CV$^2$ & Exact $L/g$ & Fluid $L/g$ & Moment error (\%)",
        rows,
    )
    exact = supplement["exact_control"]
    rows = []
    for key, label in (
        ("first_use", "First use"),
        ("eager", "Eager"),
        ("preserve_without_guard", "Retain, lose guard"),
        ("preserve_with_guard", "Retain + guard"),
        ("stable_first_use", "Stable first use"),
        ("stable_preserve_with_guard", "Stable retain + guard"),
    ):
        cells = [label]
        for regime in ("default", "read_stress"):
            value = exact["scans"][regime]["summaries"][key]
            interval = value["optimal_integer_intervals"][0]
            bounds = (
                f"$\\ge{interval[0]}$"
                if value["optimal_tail_unbounded"]
                else f"{interval[0]}--{interval[1]}"
            )
            cells.extend([bounds, f"{1000 * value['minimum_usd']:.6f}"])
        rows.append(row(cells))
    tex += table(
        "PaperExactMinima",
        "lrrrr",
        "Policy & Default $H$ & mUSD & Read-stress $H$ & mUSD",
        rows,
    )
    rows = []
    for value in supplement["global_price_phases"]:
        lower = value["ratio_lower_numeric"]
        upper = value["ratio_upper_numeric"]
        optimizer = value["optimizers_inside_interval"][0]
        policy = optimizer["policy"].replace("_", " ")
        upper_h = optimizer["integer_upper"]
        interval = (
            f"$\\ge{optimizer['integer_lower']}$"
            if upper_h is None
            else f"{optimizer['integer_lower']}--{upper_h}"
        )
        bound = "$\\infty$" if upper is None else f"{upper:.6f}"
        rows.append(row([f"{lower:.6f}", bound, policy, interval]))
    tex += table(
        "PaperPriceFaces", "rrlr", "$p_r/p_w$ lower & Upper & Active policy & Integer $H$", rows
    )
    rows = []
    stress = supplement["continuum"]["actual_curve_results"]["read_price_sensitivity"]
    for value in stress["results"]:
        valley = value["best_local_minimum"]
        bias = "Below resolution" if valley["bias_usd"] == 0 else f"${valley['bias_usd']:.5g}$"
        rows.append(
            row(
                [
                    f"{value['sigma_tokens']:g}",
                    f"{valley['center']:.6f}",
                    f"{valley['cost_usd']:.12f}",
                    bias,
                    f"{valley['log10_absolute_curvature']:.2f}",
                ]
            )
        )
    tex += table(
        "PaperSmoothingTable",
        "rrrrr",
        "$\\sigma$ & Valley mean & USD & Bias USD & $\\log_{10}|J''|$",
        rows,
    )
    rows = []
    for value in supplement["continuum"]["uniform_lattice_bridge"]["rows"]:
        rows.append(
            row(
                [
                    str(value["cells"]),
                    f"{value['raw_lattice_cost_uniform_error']:.8f}",
                    f"{value['coarse']['lattice_gradient'][0]:.8f}",
                    f"{value['resolves_lattice']['lattice_gradient'][0]:.8f}",
                    f"{value['resolves_lattice']['lattice_gradient'][1]:.8f}",
                ]
            )
        )
    tex += table(
        "PaperLatticeTable",
        "rrrrr",
        "$m$ & Cost bound & Coarse slope & Fine gap slope & Fine midpoint slope",
        rows,
    )
    tex += r"""\newcommand{\PaperFiniteCurves}{%
\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.3cm},
width=.44\textwidth,height=4.5cm,xlabel={Integer threshold $H$},
ylabel={mUSD / eight-action task},xmin=1,xmax=299]
"""
    for regime, title in (("default", "Default prices"), ("read_stress", "Read-price stress")):
        curve = exact["scans"][regime]["first_use_curve"]
        tex += f"\\nextgroupplot[title={{{title}}}]\n"
        tex += (
            "\\addplot[inkblue,thick,const plot] coordinates {"
            + coordinates(
                [x["threshold"] for x in curve],
                [1000 * x["costs"] for x in curve],
            )
            + "};\n"
        )
    tex += "\\end{groupplot}\n\\end{tikzpicture}}\n"
    boundaries = np.array(stress["boundaries"], dtype=float)
    jumps = np.array([float(Fraction(x)) for x in stress["exact_jumps"]])
    base = float(Fraction(stress["exact_base"]))
    xs = np.linspace(140, 200, 121)
    tex += r"""\newcommand{\PaperContinuumCurves}{%
\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.3cm},
width=.44\textwidth,height=4.7cm,xlabel={Mean task threshold $h$},xmin=140,xmax=200]
\nextgroupplot[ylabel={mUSD / task},legend style={at={(.5,.98)},anchor=north}]
"""
    for sigma, color in ((1, "inkblue"), (4, "leafgreen"), (12, "warmred")):
        normal = (xs[:, None] - boundaries) / sigma
        costs = 1000 * (base + ndtr(normal) @ jumps)
        points = coordinates(xs.tolist(), costs.tolist())
        tex += f"\\addplot[{color},thick] coordinates {{{points}}};\n"
        tex += f"\\addlegendentry{{$\\sigma={sigma}$}}\n"
    tex += "\\nextgroupplot[ylabel={mUSD / additional threshold token}]\n"
    for sigma, color in ((1, "inkblue"), (4, "leafgreen"), (12, "warmred")):
        normal = (xs[:, None] - boundaries) / sigma
        gradients = 1000 * ((np.exp(-(normal**2) / 2) / (sigma * np.sqrt(2 * np.pi))) @ jumps)
        points = coordinates(xs.tolist(), gradients.tolist())
        tex += f"\\addplot[{color},thick] coordinates {{{points}}};\n"
    return tex + "\\end{groupplot}\n\\end{tikzpicture}}\n"


def main() -> None:
    """Update only experimental macros and record every aggregate source digest."""
    root = Path(__file__).resolve().parents[1]
    names = {
        "working": "working-set-results.json",
        "renewal": "renewal-results.json",
        "prices": "price-family-results.json",
        "catalog": "price-scenarios.json",
        "supplement": "paper-supplement-results.json",
    }
    sources = {key: root / "docs/research" / name for key, name in names.items()}
    data = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in sources.items()}
    generated = (
        working_exhibits(data["working"])
        + renewal_exhibits(data["renewal"])
        + price_exhibits(data["prices"], data["catalog"])
        + finite_exhibits(data["supplement"])
    )
    source = root / "paper/manuscript.tex"
    text = source.read_text(encoding="utf-8")
    if BEGIN not in text:
        text = text.replace("\\begin{document}", BEGIN + "\n" + END + "\n\\begin{document}", 1)
    assert text.count(BEGIN) == text.count(END) == 1
    before, remainder = text.split(BEGIN, 1)
    _, after = remainder.split(END, 1)
    source.write_text(before + BEGIN + "\n" + generated + END + after, encoding="utf-8")
    manifest = {
        "source_sha256": {
            key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in sources.items()
        },
        "scope": "Published aggregates and exact jump-law presentation; no resampling",
        "tables": generated.count("\\begin{tabular}"),
        "plot_groups": generated.count("\\begin{groupplot}"),
    }
    (root / ".cache/paper/exhibit-data.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Embedded {manifest['tables']} tables and {manifest['plot_groups']} plot groups.")


if __name__ == "__main__":
    main()
