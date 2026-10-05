# Context Compaction Lab

A reproducible research project on **expected API invoice cost versus context
compaction thresholds**. It uses stochastic workloads, explicit token-category
accounting, an exact first-passage control, and paired Monte Carlo comparisons.
It does not optimize task quality or claim a universal threshold.

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
- Random request-start intervals, Beta recovery fractions, and positive
  reloaded-document sizes; no hidden upper-tail clipping.
- Disjoint uncached-input, cache-write, cache-read, and output billing,
  including generated-output tails, compaction summaries, and cache expiry.
- Shared random fields across thresholds, expected-cost intervals, paired
  finite-difference slopes, and independently seeded confirmation.
- Gamma/Lognormal marginal fitting with maximum likelihood, AIC/BIC, and
  descriptive tail diagnostics rather than invalid fitted-sample KS p-values.
- An exact exponential-growth first-passage benchmark verified by SymPy.

**All bundled workloads are synthetic assumptions, not measured production
traffic.** Distribution fitting does not validate the joint workload or its
stationarity. No real model API calls or credentials are required.

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
uv run compaction-lab sweep --scenario baseline --replicates 2048 --calls 400
uv run compaction-lab sweep --scenario bursty --replicates 2048 --calls 400
uv run compaction-lab sweep --scenario long-gaps --replicates 2048 --calls 400
uv run compaction-lab sweep --scenario constant --replicates 2048 --calls 400

# Probe finite-difference bias rather than claiming an exact gradient.
uv run compaction-lab sweep --difference-step 2000 --output .cache/experiments/step-2000

# Change the conditional recovery mechanism or remove expiry in an ideal control.
uv run compaction-lab sweep --recovery-basis crossed --output .cache/experiments/crossed
uv run compaction-lab sweep --no-expiry --output .cache/experiments/no-expiry
```

The inclusive default grid is `25000:150000:5000` tokens. Each normal call adds
random retained input and output; the exogenous workload is shared across policy
comparisons. Compaction occurs at most once before a remaining normal request,
never as an unnecessary terminal action. An infinite-threshold no-compaction
baseline is priced separately.

Each `sweep.json` records workload parameters, prices per token, independent
replicate count, seeds, Python/package versions, source digest, discovery-grid
selection, and independent validation. `trajectory-costs.npz` retains paired
per-trajectory prices for the finite discovery grid. `sweep.png` visualizes
expected costs and centered secants with pointwise Monte Carlo intervals.

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
[research plan](docs/research/research-plan.md), and
[implementation contract](docs/implementation-contract.md) for assumptions,
references, hypotheses, and the next calibration/validation steps.

The [initial synthetic experiment report](docs/research/initial-experiments.md)
records the first 4,096-trajectory studies, their boundary/step-size probes,
independent confirmation, and limitations.

No license has been selected yet. Public repository visibility alone is not an
open-source license grant.
