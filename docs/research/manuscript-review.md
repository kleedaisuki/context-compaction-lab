# Publication manuscript: evidence organization and authoring review

Recorded 2026-10-06. Maintained document: `paper/manuscript.tex`, with compiled
reading copy `paper/manuscript.pdf`. This records the rationale and completed
review rather than substituting a software test report for the paper.

## Argument and selection

The central claim is that compaction amortizes state reconstruction against
discounted history carrying. The article selects a coherent subset of the
project: renewal occupation and price phases; cold-tail response; envelope
and regret geometry; empirical growth, dependence, material paths, horizons
and tariff classes. The broader finite-state occupation/LP counterexamples,
earlier working-set prototype and every closed distribution formula are not
introduced as competing narratives in the main body.

Introduction motivates the paradox through a coding-agent continuation and
price-reversal example. Related Work connects prompt representations, cache
layout, working sets and workload characterization to the same question.
Model and Theory state the accounting and pivotal results. Evaluation explains
how full-input increments are estimated, why nonparametric renewal calculation
is useful for the observed jumps, and how matched marginals isolate dependence.
Discussion develops representation, regret and budget-risk implications and
contains the limitations. Conclusion identifies the next state-level question.

## Evidence mapping

| Manuscript result | Authoritative project evidence |
| --- | --- |
| Distribution-general crossing and atomic plateaus | `renewal-analytic-control.md`; `renewal-closed-forms.md` |
| Four-price ledger and cold terminal mark | `renewal-study-contract.md`; `renewal_ledger_crosscheck.py` |
| Price directions, mixed sensitivities and local rank-one regret | `price-sensitivity-theory.md`; `price-sensitivity-symbolics.md` |
| Full-input growth extraction and block-weighted marks | `renewal-community-calibration.md`; pinned public pool |
| Mean curves, variance diagnostic and independent short-horizon gains | `renewal-results.json`; `renewal-community-study.md` |
| Material-path and timing contrasts | `price-sensitivity-results.json` |
| 38 quotes, 143 scenarios and same-q Qwen total-expense contrasts | `price-scenarios.json`; `price-family-results.json` |
| Twenty-seven proportional-vector controls and old-scenario preservation | `price_family_crosscheck.py` |

The price-phase heatmap is regenerated deterministically from the same law and
grid; its baseline-write column is asserted identical to the published phase
artifact. Other plot coordinates come from executed results, not a new fit or
resampled trajectory experiment. Complete plotted values and source hashes
are materialized by `build_paper_figures.py` under `.cache/paper`.

## Review decisions

- Mathematical notation is consistent from main body to appendices: S is the
  whole reconstructed floor, B and C are within it, L=H-S, and output billing
  is not another growth component. The regenerative theory uses iid paired
  growth/output marks, allowing within-action dependence.
- The core crossing and full marked selection are distinct; smooth gradients
  require continuity and rank-one curvature uses a positive-density interior
  root. Atomic switches have directional/cell comparisons instead.
- The write-reversal proposition explicitly requires a positive q=0 setup
  quantity, preventing a degenerate zero-price endpoint from being mistaken
  for a sign change. The full cold-tail theorem is stated for the exponential
  law; the empirical study evaluates marked cells directly.
- Estimates, calibrated magnitude anchors and declared cache/material controls
  have different roles. These distinctions are introduced where they define
  the method; broader causal/quality/provider limitations are consolidated in
  Discussion.
- Related-work metadata were checked against first-party papers and proceedings.
  ACL/EMNLP, NeurIPS, CACM and Econometrica items use verified venues; recent
  arXiv works are cited as preprints. Provider-specific Qwen quote conflict is
  recorded rather than reconciled by an invented multiplier.
- The manuscript has all six requested main sections, core proofs and detailed
  execution in appendices, four figures, and the specified author/email. It
  uses `acmart` without fabricated ACM venue/acceptance metadata.

## Rendering and reproducibility

The native editor was opened but its compiler returned a platform-directory
initialization error. The already-installed TeX Live 2026 exported the PDF;
no toolchain was installed. Three successful passes resolve citations,
cross-references and floats. The reading copy has 11 pages and no unresolved
references/citations or horizontally overflowing boxes. Every page was rendered
with Poppler for visual review; the source digest displays as two wrapped
32-character lines, and tables/plots remain within their columns. Figure
regeneration is idempotent. The final build has no overflowing-box diagnostics.
The balance package warns about its invocation in the second column; the final
appendix columns are uneven, with no clipping or overlap in the reviewed pages.

The code environment remains the root uv `.venv`. Compiler objects, logs,
renders and raw evidence stay in `.cache`; only source and final reading PDF
are maintained under `paper`. Existing unrelated Lean-IDE edits remain untouched.
