# Context Compaction Lab

A reproducible research project on **expected API invoice cost versus context
compaction thresholds**. It uses stochastic workloads, explicit token-category
accounting, analytic renewal laws, and paired discrete trajectory comparisons.
It does not optimize task quality or claim a universal threshold.

## Analytic renewal structure and executed community study

The primary new result is **D(L*)=A/c**, where L=H-S is the gap above compulsory
reconstructed context and D is integrated renewal occupation. It selects the
optimum in a declared regenerative class, including integer growth/plateaus,
without inventing a marginal distribution or scanning Monte Carlo thresholds.
Closed exponential/Erlang/mixture laws, convex-order and growth-scale mechanisms,
random-reset equations, and four-price crossing-tail corrections are derived.

[The integrated report](docs/research/renewal-community-study.md) then instantiates
the theory with 297,091 public TraceLab growth observations. Raw IID and intact
16-action block controls have the same marginal at every action index. Main
findings: local correlation increases invoice variance much more than it moves
the minimum; cache reliability and remaining-task horizon dominate microscopic
threshold tuning. The approximately **113k** analytic line is a conditional
price/reset scenario, not a production recommendation or population estimate.

Read [the full derivation](docs/research/renewal-analytic-control.md),
[closed-form analysis](docs/research/renewal-closed-forms.md),
[community calibration](docs/research/renewal-community-calibration.md),
[portable results](docs/research/renewal-results.json), and
[independent method review](docs/research/renewal-study-review.md).

```powershell
uv sync --locked
# Download the pinned public trace using the command below, then:
uv run python experiments/calibrate_renewal_trace.py
uv run python experiments/renewal_closed_form_derivation.py
uv run python experiments/finite_continuum_bridge.py
uv run python experiments/renewal_ledger_crosscheck.py
uv run python experiments/renewal_community_study.py
./formal/verify.ps1
```

Generated raw pools, figures and logs stay in `.cache`. No credentials, model API
calls or large new parameterized test suite. Existing regression tests protect
established interfaces; the research contribution is the analytic structure,
mechanism comparisons and actual source-calibrated findings.

## Continuum bridge: finite systems do not prohibit continuous analysis

Exact integer accounting is a microscopic reference, not the research endpoint.
The [continuum bridge](docs/research/continuum-bridge-theory.md) explains finite
approximation bounds, derivative-measure limits, decision-boundary coupling,
and the transfer from uniform surrogate error to original decision regret.
Continuous state models retain essential file/reset jumps and discrete contracts.

The [executed continuum analysis](docs/research/continuum-symbolic-results.md)
uses exact original ledger curves to derive Gaussian whole-task budget
responses, local bias bounds, and a separately declared lattice-to-continuum
limit. Randomizing a whole-task budget is not resampling each request's gate,
nor proof that a smoothed minimum solves the original deterministic problem.

```powershell
uv run python experiments/structural_symbolic_analysis.py  # Prepare exact source curves.
uv run python experiments/continuum_threshold_analysis.py
./formal/verify.ps1  # Includes the uniform approximation -> 2*epsilon regret law.
```

## v0.3 theory-first structural analysis

The research foundation is now an arbitrary joint conditional history law,
not a collection of independent fitted marginals. It permits correlated,
nonstationary and action-dependent outputs/requirements. Reduced Markov states
require an explicit sufficiency condition. The fixed ordinary-work horizon
must not advance just because a paid compaction occurred.

Delivered results:

- Exact finite-horizon occupation, adjoint and policy-difference identities;
  threshold sensitivity depends on full future action advantage at the boundary.
- Integer-token thresholds have a signed atomic derivative, not a smooth
  sweet-point equation. Lean checks rational-cell invariance for arbitrary
  finite threshold decision trees and finite correlated task weights.
- Equal-length reachable states can require opposite controls. An exact
  one-stage occupation LP/Bellman certificate proves a scalar-threshold gap.
- SymPy extracts true occupation polynomials from actual simulator paths,
  with exact price-comparison hyperplanes and the global candidate price hull.
- Dependency-free Lean proofs check finite accounting, price-region laws,
  quantization and strict reconstruction-loop obstruction.

Read [the threshold/operator synthesis](docs/research/threshold-operator-theory.md),
[general joint-law control](docs/research/general-stochastic-control-theory.md),
[exact symbolic results](docs/research/structural-symbolic-analysis.md),
[mathematical tool review](docs/research/mathematical-tools-for-compaction.md),
and [Lean proof scope](docs/research/lean-structural-verification.md).

```powershell
uv sync --locked
uv run python experiments/threshold_operator_analysis.py
uv run python experiments/structural_symbolic_analysis.py
uv run python experiments/structural_control_counterexample.py
./formal/verify.ps1  # Requires the already installed Lean 4.33.1; downloads nothing.
uv run python experiments/summarize_structural_theory.py
```

The previous numerical 126k/78k selections are controlled v0.2 scenarios,
not theoretical optimality statements or production recommendations. Their
source hash corresponds to historical commit `85aa959`, not the subsequently
expanded symbolic package. No old transition/ledger interfaces were changed.

## v0.2 working-set laboratory (historical controlled experiment)

The implemented model now tracks current file versions, visible snapshots,
qualifying-read state, recent valid observations, exact-prefix reuse and TTL.
It supports eager versus first-use restoration, fixed ordinary observations,
additional billed recovery rounds, and bounded strict read/compact loops.
The older aggregate engine remains a compatibility/control interface.

**Executed results:** with four real whole-file size proxies totaling 61,318
tokens, empirical public output blocks, and explicit controlled task/cache
assumptions, the mandatory-all-files fine-grid selection is **126k** (1% grid
region **116k-138k**). Phase-local first-use selection is **78k** (**68k-86k**).
These are conditional scenario results, not universal production thresholds.
See [implemented experiment report](docs/research/working-set-experiments.md),
[portable results](docs/research/working-set-results.json), and
[exact control](docs/research/working-set-exact-control.md).

After the setup below, download the explicitly pinned public trace into the
project cache. On PowerShell:

```powershell
New-Item -ItemType Directory -Force .cache/community-data | Out-Null
curl.exe -L --fail --output .cache/community-data/syfi-v0.0.2.jsonl.gz https://github.com/uw-syfi/TraceLab/releases/download/v0.0.2/syfi_coding_trace.jsonl.gz
uv run compaction-lab prepare-working-set --trace .cache/community-data/syfi-v0.0.2.jsonl.gz
uv run compaction-lab working-set --demand mandatory --policies first_use_warm
uv run python experiments/run_working_set_study.py --replicates 2048 --jobs 2
```

On Linux/macOS use `mkdir -p .cache/community-data` and `curl` instead of the
first two PowerShell commands. Preparation verifies the public release checksum,
downloads four pinned public source files, measures them with `cl100k_base`,
and saves a local output-only block pool. No model API calls or credentials.
The trace is 100.9 MB compressed; neither it nor source-file bodies are committed.

Do not use measured fresh append as background growth: it includes replay and
file payloads. The new experiment separately samples measured output, controlled
non-file input and explicit compulsory restoration. File-access laws, stable
base, summary size, and timing controls are recorded, not presented as fitted.

Primary modules are `working_set_config.py`, `working_set_simulation.py`,
`working_set_data.py`, `working_set_workloads.py`, `working_set_inference.py`,
and `working_set_cli.py`. The complete environment remains the root `.venv`.

New research milestone: [mandatory restoration synthesis](docs/research/mandatory-reload-synthesis.md)
connects four production systems, community incidents, seven selected papers,
six mathematical tools, a full public TraceLab usage profile, and exact/Monte
Carlo first-use probes. It selects a hybrid working-set model for the next
implementation; it does not silently change the packaged aggregate simulator.
That research-only milestone has now been implemented by v0.2 as described above.

## Research question

When does paying for compression, cache reconstruction, and document recovery
cost less than repeatedly carrying a long context? For a fixed number of normal
requests, the primary objective is

\[
J_N(h)=\mathbb E[C_N(h)].
\]

For genuinely regenerative steady workloads, the cost rate is
\(\mathbb E[Q_h]/\mathbb E[T_h]\), **not**
\(\mathbb E[Q_h/T_h]\). Recovery based on actual crossing state may produce
dependent cycles, so the finite-horizon simulator is the primary experiment.

The initial implementation provides:

- Constant, Gamma, Lognormal, and mean-normalized burst-mixture growth laws.
- Random request-start intervals and fixed or tightly concentrated absolute
  summary/document sizes; proportional Beta recovery is a legacy control.
- Verbatim preservation is separate from generated summaries; a declared
  unchanged warm cache boundary can survive compaction without a full rewrite.
- Disjoint uncached-input, cache-write, cache-read, and output billing,
  including generated-output tails, compaction summaries, and cache expiry.
- Shared random fields across thresholds, expected-cost intervals, paired
  finite-difference slopes, and independently seeded confirmation.
- Gamma/Lognormal marginal fitting with maximum likelihood, AIC/BIC, and
  descriptive tail diagnostics rather than invalid fitted-sample KS p-values.
- An exact exponential-growth first-passage benchmark verified by SymPy.

**The default engineering scenario uses published real-workload magnitude
anchors, not a fitted production distribution.** The other bundled controls
are entirely synthetic. Distribution fitting does not validate a joint workload
or its stationarity. No real model API calls or credentials are required.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then use its
standard project environment, `.venv`. The package supports Python 3.12 and
later; `.python-version` selects 3.14 for development.

```powershell
# Windows PowerShell: only caches and generated artifacts use .cache.
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.cache\python'
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD '.cache\pycache'
$env:MPLCONFIGDIR = Join-Path $PWD '.cache\matplotlib'
uv sync --locked
uv run pytest
uv run ruff check src tests
```

```sh
# Linux/macOS: uv creates the complete project environment in .venv.
export UV_PYTHON_INSTALL_DIR="$PWD/.cache/python"
export PYTHONPYCACHEPREFIX="$PWD/.cache/pycache"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
uv sync --locked
uv run pytest
uv run ruff check src tests
```

The project is installed in editable mode through its build backend. Third-party
packages are installed in `.venv`; `src/` is not added through an ad hoc path hack.

## Run an expected-cost experiment

```sh
# Generated JSON, trajectory arrays, and plots stay under .cache/experiments.
uv run compaction-lab sweep --scenario engineering --replicates 4096 --calls 400
# Higher-growth sensitivity; the source's growth scale depends on context band.
uv run compaction-lab sweep --scenario engineering --growth-mean 3200 --output .cache/experiments/engineering-growth-3200

# Historical synthetic controls (not defaults or empirical calibration).
uv run compaction-lab sweep --scenario baseline --replicates 2048 --calls 400
uv run compaction-lab sweep --scenario bursty --replicates 2048 --calls 400
uv run compaction-lab sweep --scenario long-gaps --replicates 2048 --calls 400
uv run compaction-lab sweep --scenario constant --replicates 2048 --calls 400

# Engineering recovery: 4,382 generated summary + 61,206 aggregate input.
# The residual is not a measured documents-only quantity.
uv run compaction-lab sweep --scenario engineering --summary-tokens 4382 --restored-input-tokens 61206

# Synthetic split controls; fixed recovery does not grow with the trigger.
uv run compaction-lab sweep --scenario baseline --summary-tokens 3200 --documents-mean 12000
uv run compaction-lab sweep --recovery-cv 0.05 --output .cache/experiments/narrow-recovery

# Keep old messages without counting them as generated output.
uv run compaction-lab sweep --scenario baseline --preserved-tokens 4000 --summary-tokens 2000

# Only use a surviving prefix when its unchanged eligible cache boundary is known.
uv run compaction-lab sweep --scenario baseline --preserved-tokens 4000 --surviving-prefix-tokens 4000

# Probe finite-difference bias rather than claiming an exact gradient.
uv run compaction-lab sweep --difference-step 2000 --output .cache/experiments/step-2000

# Change the conditional recovery mechanism or remove expiry in an ideal control.
uv run compaction-lab sweep --scenario legacy --recovery-basis crossed --output .cache/experiments/legacy-crossed
uv run compaction-lab sweep --no-expiry --output .cache/experiments/no-expiry
```

The inclusive default grid is `75000:300000:5000` total retained tokens. Each normal call adds
random retained input and output; the exogenous workload is shared across policy
comparisons. Compaction occurs at most once before a remaining normal request,
never as an unnecessary terminal action. An infinite-threshold no-compaction
baseline is priced separately.

Version 0.1.1 separates generated summaries from non-generated recovery. The
default CLI `engineering` scenario anchors total reset size at **65,588** and
generated summary at **4,382** tokens, the separate medians reported across
873 compactions in a [single-engineer Claude Code case study](https://langwatch.ai/research/finding-the-optimal-context-window).
The constructed difference **61,206** is aggregate non-summary recovered input,
not a measured residual median or document volume. Unknown component fields
are zero placeholders because their volume is included in this aggregate;
zero does not assert no documents or retained history existed. Do not add a
system/tools prefix again. Recovery is cold in this explicit scenario, not in
every real agent. The study's 1,470-token high-context growth scale anchors a
Gamma control with **unfitted CV 0.8**. Gaps, output fraction, horizon, and prices
also remain declared controls; medians are not substituted for empirical means.
See [engineering evidence](docs/research/engineering-context-evidence.md).

The Python `Workload()` and named `baseline` retain the 2k/12k illustrative
control for compatibility; neither is the CLI's engineering default. A recovery
CV of 0.05 gives small independent Lognormal summary/document variations where
those quantities are positive; aggregate restored input remains fixed. This is
a sensitivity assumption, not an empirically fitted dispersion.
`--scenario legacy` explicitly restores the old 2,000+Beta*h summary and
12,000-mean document CV 0.8 so the previous baseline remains reproducible.

All retained tokens are charged when processed as input; only newly generated
summary tokens incur compactor output charges. Verbatim preservation does not
automatically imply cache reuse. The surviving-prefix option assumes an
actually matching, previously eligible leading cache boundary; it is not
inferred from filenames or token counts.

Each `sweep.json` records workload parameters, prices per token, independent
replicate count, seeds, Python/package versions, source digest, discovery-grid
selection, and independent validation. `trajectory-costs.npz` retains paired
per-trajectory prices for the finite discovery grid. `sweep.png` visualizes
expected costs and centered secants with pointwise Monte Carlo intervals.
Engineering reports additionally retain source anchors and the unmeasured
assumptions separately; overrides change the workload, not the source's claims.

Intervals are conditional on the specified model. They do not include workload
parameter uncertainty, finite-difference bias, or a simultaneous guarantee for
the selected minimum. Independent confirmation evaluates the selected policy
against no compaction without selecting again on the confirmation sample.

## Fit a measured marginal

Place a CSV trace under `.temp` or `.cache` and select a positive numeric column:

```sh
# This fits a marginal; it does not silently change the simulator's workload.
uv run compaction-lab fit --input .temp/trace.csv --column growth_tokens --units tokens
```

The report includes location-zero Gamma and Lognormal fits, log-likelihood,
AIC/BIC, descriptive KS distance, and fitted versus empirical tail quantiles.
Zero, missing, censored, or dependent observations require an explicit data model
instead of automatic dropping. Trace provenance is represented by a digest,
not exported private machine paths.

## Exact stochastic symbolic control

```sh
uv run compaction-lab symbolic
```

With fixed recovered length \(s\), independent exponential growth of mean \(g\),
ideal warm reads, and affine compaction processing, the crossing time is
\(T_h=1+\operatorname{Poisson}((h-s)/g)\) and the expected crossing size is
\(h+g\). For \(A=k_0+(k_1+p_w-p_r)s\), SymPy verifies

\[
r'(h)=\frac{p_r}{2}
-\frac{gA+p_rg^2/2}{(h-s+g)^2},
\qquad
h_*=s-g+\sqrt{g^2+\frac{2gA}{p_r}}.
\]

This is an exact stochastic control under its assumptions, not the solution to
the full TTL/recovery simulator. It demonstrates that plugging mean growth into
the earlier deterministic threshold misses first-passage overshoot geometry.

## Project layout

```text
src/context_compaction_lab/   # Packaged source and installed CLI
tests/                       # Maintained tests
docs/research/               # Theory, research plan, reviews, experiment findings
.github/workflows/ci.yml      # Locked tests and wheel/sdist build on Python 3.12/3.14
pyproject.toml                # Dependencies, build backend, tooling, entry point
uv.lock                      # Reproducible dependency resolution
.venv/                       # Standard complete project environment, ignored
.cache/                      # uv cache and regenerated experiment artifacts, ignored
.temp/                       # Temporary traces and probes, ignored
```

## Scope and next research

The v0.1 simulator assumes independent exogenous marginals and fixed prices.
It does not enforce a hard context capacity, context-tier pricing, or provider
routing and cache-boundary details. It records maximum context and recovery
above threshold; an unbounded law is not a capacity-safety guarantee. It models
API token invoices, not subscription usage quotas. Normal-call count and growth
are held fixed across policies, so savings are not task-success evidence.

See the [stochastic model](docs/research/stochastic-model.md),
[engineering evidence](docs/research/engineering-context-evidence.md),
[engineering-magnitude results](docs/research/engineering-calibrated-experiments.md),
[research plan](docs/research/research-plan.md), and
[implementation contract](docs/implementation-contract.md) for assumptions,
references, hypotheses, and the next calibration/validation steps.

The [initial synthetic experiment report](docs/research/initial-experiments.md)
records the historical v0.1 high-dispersion studies. Its threshold findings
must not be applied to the corrected fixed/narrow recovery model.

The [corrected recovery report](docs/research/corrected-recovery-experiments.md)
records constant versus CV 0.05 controls, preserved-message accounting, and
independent confirmation. Under the same illustrative prices, the fixed and
small-noise cost curves are practically close; absolute recovery sizes remain
unmeasured project parameters rather than a universal recommendation.

No license has been selected yet. Public repository visibility alone is not an
open-source license grant.
