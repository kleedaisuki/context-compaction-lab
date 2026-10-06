"""Embed publication plots backed by executed artifacts into the standalone paper.

The mean curves and family comparisons come from portable published results.
The two-dimensional marked price response is regenerated deterministically from
the same pinned empirical law and phase-map grid. No trajectory experiment is
resampled and no price/model performance is inferred. Figure data and source
hashes are saved under .cache/paper for review and reproduction.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from context_compaction_lab.renewal_numerics import (
    RenewalLedger,
    analytic_rates,
    empirical_renewal,
)

BEGIN = "% BEGIN GENERATED FIGURES"
END = "% END GENERATED FIGURES"


def coordinates(xs: list[float], ys: list[float]) -> str:
    """Encode paired numerical observations without presenting extra precision."""
    return " ".join(f"({x:.8g},{y:.8g})" for x, y in zip(xs, ys, strict=True))


def plot(style: str, xs: list[float], ys: list[float], legend: str) -> str:
    """Create an embedded plot with a readable publication legend."""
    return (
        f"\\addplot[{style}] coordinates {{{coordinates(xs, ys)}}};\n\\addlegendentry{{{legend}}}\n"
    )


def cost_curves(results: dict) -> tuple[str, dict]:
    """Use the executed exploratory curves and label them as evaluated means."""
    tex = r"""\newcommand{\PaperCostCurves}{%
\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.25cm},
  width=.44\textwidth,height=4.7cm,xlabel={$H$ (thousand tokens)},
  ylabel={USD / ordinary action},xmin=80,xmax=200,
  legend style={at={(.98,.98)},anchor=north east}]
"""
    data = {}
    for calls in (4000, 32):
        tex += f"\\nextgroupplot[title={{{calls:,} actions}},ymin=.043,ymax=.071]\n"
        for mode, color in (("iid", "inkblue"), ("block", "warmred")):
            row = results["simulations"][f"{mode}/warm_base20k/N{calls}"]
            pairs = [
                (x / 1000, y)
                for x, y in zip(row["thresholds"], row["mean_usd_per_call"], strict=True)
                if x is not None and 80000 <= x <= 200000
            ]
            xs, ys = map(list, zip(*pairs, strict=True))
            tex += plot(f"{color},thick", xs, ys, "IID" if mode == "iid" else "Blocks")
            data[f"{mode}/N{calls}"] = pairs
        tex += (
            r"\addplot[black,dashed,forget plot] coordinates "
            r"{(112.848,.043)(112.848,.071)};" + "\n"
        )
    tex += "\\end{groupplot}\n\\end{tikzpicture}}\n"
    return tex, data


def price_phase(root: Path, results: dict) -> tuple[str, dict]:
    """Regenerate the previously executed marked phase map, recording every cell."""
    pool = dict(np.load(root / ".cache/renewal-calibration/growth-pool.npz"))
    weights = pool["block_marginal_weights"]
    output_mean = float(np.average(pool["previous_output_tokens"], weights=weights))
    renewal = empirical_renewal(pool["values"], weights, 5, 250000)
    grid = results["write_price_cache_phase"]
    qs, factors = grid["q_grid"], grid["write_factor_grid"]
    base = RenewalLedger()
    delta = np.zeros((len(qs), len(factors)))
    for i, q in enumerate(qs):
        for j, factor in enumerate(factors):
            ledger = replace(
                base,
                cache_hit=q,
                prices=replace(base.prices, write=base.prices.write * factor),
            )
            before = analytic_rates(renewal, ledger, output_mean)["marked_minimum_threshold"]
            changed = replace(
                ledger, prices=replace(ledger.prices, write=ledger.prices.write * 1.05)
            )
            after = analytic_rates(renewal, changed, output_mean)["marked_minimum_threshold"]
            delta[i, j] = after - before
    column = int(np.argmin(abs(np.array(factors) - 1)))
    assert np.array_equal(delta[:, column], grid["baseline_write_column_threshold_change"])
    rows = [r"factor q delta\\"]
    for i, q in enumerate(qs):
        for j, factor in enumerate(factors):
            rows.append(f"{factor:.8g} {q:.8g} {delta[i, j]:.8g}" + r"\\")
    tex = r"""\newcommand{\PaperPricePhase}{%
\begin{tikzpicture}
\begin{axis}[width=.80\textwidth,height=5cm,
  xlabel={Write price / baseline write price},ylabel={Hit probability $q$},
  xmin=.475,xmax=2.025,ymin=.645,ymax=1.005,
  colormap={signed}{rgb(0cm)=(.23,.30,.75);rgb(1cm)=(.97,.97,.97);
    rgb(2cm)=(.70,.02,.15)},point meta min=-1500,point meta max=1500,
  colorbar,colorbar style={ylabel={Change in $H$ (tokens)},font=\footnotesize},
  grid=none,legend style={at={(.03,.98)},anchor=north west,fill=white}]
\addplot[matrix plot*,mesh/cols=31,point meta=explicit,forget plot]
table[x=factor,y=q,meta=delta,row sep=\\] {
""" + "\n".join(rows)
    tex += r"""
};
\addplot[black,dashed,thick] coordinates {(.5,.8857444074)(2,.8857444074)};
\addlegendentry{Core $q_w$}
\end{axis}
\end{tikzpicture}}
"""
    return tex, {"q": qs, "write_factor": factors, "threshold_change": delta.tolist()}


def family_curves(results: dict) -> tuple[str, dict]:
    """Present selected controlled price classes and same-q cache-mode expense."""
    cases = results["analytic_cases"]
    qs = [0.8, 0.95, 1.0]
    selected = (
        ("gpt6sol_short", "inkblue,mark=o", "GPT .10 read class"),
        ("gpt61sol_short", "leafgreen,mark=square*", "GPT-6.1 Sol"),
        ("gpt41_short", "gray,mark=triangle*", "GPT-4.1"),
        ("deepseek41flash_offpeak", "warmred,mark=diamond*", "DeepSeek Flash"),
        ("qwen38max_singapore_implicit", "orange!80!black,mark=+", "Qwen Max implicit"),
    )
    tex = r"""\newcommand{\PaperFamilyCurves}{%
\begin{tikzpicture}
\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.3cm},
  width=.44\textwidth,height=5.1cm,xmin=.79,xmax=1.01,
  xlabel={Controlled hit probability $q$},xtick={.8,.95,1}]
\nextgroupplot[ylabel={Optimal $H$ (thousand tokens)},ymin=80,ymax=170,
  legend style={at={(.03,.97)},anchor=north west}]
"""
    data = {}
    for name, style, label in selected:
        names = [name + (f"__q{q:g}" if q != 1 else "") for q in qs]
        hs = [cases[n]["marked_threshold"] / 1000 for n in names]
        tex += plot(style + ",thick", qs, hs, label)
        data[name] = hs
    effects = []
    for q in qs:
        suffix = f"__q{q:g}" if q != 1 else ""
        explicit = cases["qwen38max_singapore_explicit" + suffix]["marked_rate"]
        implicit = cases["qwen38max_singapore_implicit" + suffix]["marked_rate"]
        effects.append(100 * (explicit / implicit - 1))
    tex += r"""\nextgroupplot[ylabel={Explicit expense change (\%)},ymin=-19,ymax=11]
\addplot[black,dashed,forget plot] coordinates {(.79,0)(1.01,0)};
"""
    tex += plot("warmred,thick,mark=square*", qs, effects, "Qwen Max, Singapore")
    tex += "\\end{groupplot}\n\\end{tikzpicture}}\n"
    data["qwen_max_explicit_vs_implicit_percent"] = effects
    return tex, data


def main() -> None:
    """Update only the marked figure block and preserve the authored manuscript."""
    root = Path(__file__).resolve().parents[1]
    sources = {
        name: root / "docs/research" / filename
        for name, filename in (
            ("renewal", "renewal-results.json"),
            ("prices", "price-sensitivity-results.json"),
            ("families", "price-family-results.json"),
        )
    }
    loaded = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in sources.items()}
    costs, cost_data = cost_curves(loaded["renewal"])
    phase, phase_data = price_phase(root, loaded["prices"])
    families, family_data = family_curves(loaded["families"])
    generated = costs + phase + families
    source = root / "paper/manuscript.tex"
    text = source.read_text(encoding="utf-8")
    assert text.count(BEGIN) == text.count(END) == 1
    before, remainder = text.split(BEGIN, 1)
    _, after = remainder.split(END, 1)
    source.write_text(before + BEGIN + "\n" + generated + END + after, encoding="utf-8")
    destination = root / ".cache/paper"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "figure-snippets.tex").write_text(generated, encoding="utf-8")
    manifest = {
        "source_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sources.items()
        },
        "cost_curves": cost_data,
        "price_phase": phase_data,
        "family_curves": family_data,
        "scope": "Published evaluated curves and deterministic regeneration, no new MC sample",
    }
    (destination / "figure-data.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print("Embedded three evidence-backed publication plot groups in paper/manuscript.tex")


if __name__ == "__main__":
    main()
