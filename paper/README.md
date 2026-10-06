# Paying to Remember

**Paying to Remember: Price Geometry and Renewal Control of LLM Context
Compaction** is the publication-style English manuscript for this project.
Author: **moeSegFault Codex**, `codex@mail.moesegfault.dev`.

## Read and edit

- `manuscript.pdf`: compiled two-column reading copy.
- `manuscript.tex`: standalone `acmart` source, using `sigconf,screen,nonacm`.
  The non-ACM-publication option avoids inventing a venue, DOI or acceptance.
  The bibliography and PGFPlots coordinates are embedded, so the document
  does not depend on external figure or bibliography files.
- Open the `.tex` source in the Codex LaTeX editor for editing. The native
  compiler in the recorded authoring session returned a platform-directory
  initialization error; the PDF was exported with the already installed
  TeX Live 2026, without downloading a toolchain.

## Narrative and evidence

The paper's central argument is **amortized state reconstruction**, not token
reduction in isolation. Its three linked findings are the renewal crossing and
price-direction phases, invoice-versus-policy sensitivity and retuning loss,
and the workload-conditioned importance of reliability, reconstruction and
remaining work. Related work positions representation, caching, working sets
and workload characterization around that question.

The main body presents the consequential results and connects the aggregate
renewal lane to separately executed versioned-file restoration experiments.
The expanded reading copy includes eight figures and detailed experimental
tables: restoration policies, retention budgets, exact finite controls,
continuous sensitivities, renewal/horizon contrasts, material interventions
and all 38 quoted price vectors. Appendices preserve their distinct workloads,
denominators, design, uncertainty and interpretation, not only reproduction
commands. Proofs, estimation weights and the evidence map are also included.

Discussion ends with a brief deployment-oriented distinction between
fixed-action cost and verified tasks per billed token/dollar. It does not
introduce another optimization narrative: definitions and derivations remain
in an appendix, and task-level evaluation is a future-work direction in the
Conclusion. No success curve is inferred from usage-only traces. The repository
link remains in the artifact appendix, keeping the main narrative uninterrupted.

The source evidence is the maintained renewal, sensitivity and expanded tariff
studies in `docs/research`. Figures use their executed numerical artifacts;
the heatmap is regenerated deterministically from the same empirical pool and
checked against the published baseline-write column. No new model calls or
resampled Monte Carlo results are invented for presentation.

## Rebuild

With the pinned public growth pool already prepared:

```powershell
uv sync --locked
uv run python experiments/build_paper_figures.py
uv run python experiments/build_paper_exhibits.py
uv run python experiments/task_efficiency_derivation.py
uv run python experiments/compile_paper.py
```

The figure generator updates only the delimited generated block in the source.
The exhibit generator uses the maintained aggregate JSON files, including
`docs/research/paper-supplement-results.json`. This portable supplement exports
already executed finite/continuum and closed-renewal controls; regenerate it
with `experiments/export_paper_supplement.py` after running its documented
input experiments. Rebuilding the paper itself needs no new sampled trajectory.
It saves complete plotted values and evidence hashes under `.cache/paper`.
The exporter uses an existing `pdflatex`, performs three reference/float passes,
and rejects unresolved citations or references. Compiler objects and diagnostic
logs remain in `.cache/paper/tex`; only the reading PDF is copied here.

Visual review uses Poppler to render all pages. The bibliography's primary
sources were inspected during authoring; preprints are identified as arXiv
works rather than assigned an unverified main-track venue.
