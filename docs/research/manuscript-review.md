# Publication manuscript: evidence organization and authoring review

Recorded 2026-10-06. Maintained document: `paper/manuscript.tex`, with compiled
reading copy `paper/manuscript.pdf`. This records the rationale and completed
review rather than substituting a software test report for the paper.

## Argument and selection

The central claim is that compaction amortizes state reconstruction against
discounted history carrying. The initial eleven-page article selected renewal
occupation, price phases, cold-tail response, envelope/regret geometry and
community/tariff contrasts. Reader feedback exposed overcompression: stateful
restoration and finite-control findings were reduced to scope sentences and
experimental appendices mainly recorded methodology. The expanded revision
restores those results as complementary evidence for the same argument.
Superseded broad-prior illustrative models remain developmental work, not
additional empirical evidence.

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

## Initial rendering and reproducibility (eleven-page version)

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

## Expanded revision after reader feedback

The reading copy now has 25 pages, eight vector figures, 21 numbered tables,
13 appendix sections and 27 references. All six main sections remain intact.
The main evaluation adds the separately measured/controlled versioned-file
mechanisms. Experimental appendices provide policy matrices, complete horizon
confirmation, joint retention budgets, exact finite curves, paid batching,
global price faces, continuum probes, transient closed-law approximation
errors, marked price/material controls and all 38 quoted vectors.

The mathematical expansion includes the exact demand polynomial/covariance
derivative, reachable-state Bellman/LP certificate and strict length-only gap,
CV-only counterexample, random-reset quotient derivation, renewal remainder
proof and arithmetic-span correction. Discussion alone develops the
fixed-action-cost versus successful-task-efficiency distinction. Its appendix
derives pooled ratios, the success-loss boundary, implicit price response and
fractional-control form, and identifies a success-labeled follow-up as future
work. No synthetic success curve is presented as empirical evidence.

The evidence index precedes detailed experimental appendices; the public
repository URL occurs once in the artifact appendix, not in the main narrative.
Precise coverage and the development-versus-evidence distinction are recorded
in `manuscript-coverage.md`. Portable exact/control exhibits are in
`paper-supplement-results.json`, with source hashes and an export script.

Verification: 29 focused tests passed; seven new task-efficiency SymPy
identities have zero residual. Closed-renewal and finite-continuum derivation
scripts were rerun successfully. Both presentation generators are idempotent.
The final three-pass installed-TeX build has no undefined references/citations
or overflowing boxes. Native compilation was retried and remains unavailable
with the same platform-directory initialization error. All 25 pages were
rendered and reviewed, with detailed checks of the changed tables, curves,
proof displays, Discussion and final artifact pages. The balance package's
second-column warning is harmless in the visibly balanced final page.

This is an evidence/narrative expansion, not a new community simulation.
No paid model request, trace resampling, new CI or production-code/dependency
change was introduced. Initial eleven-page source and PDF remain recoverable
from Git history.
