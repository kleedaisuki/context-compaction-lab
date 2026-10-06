# Initial synthetic expected cost experiments

Recorded on 2026-10-06. These results describe the declared stochastic model,
not a measured production workload or a universal compaction recommendation.
The primary deliverable is a reproducible expected-cost research laboratory.

Historical v0.1 report, source commit a8c38676cc5aad4e7e32bfb2033603367703df17.
Version 0.1.1 replaces the default recovery law with fixed/narrow absolute
sizes following user workload feedback. The commands below refer to that
historical source snapshot; current --scenario legacy reproduces its baseline
law explicitly. Do not carry this report's threshold region into the revised
model. See recovery-premise-refinement.md and the corrected recovery report.

## Experimental design

Each discovery experiment uses 4,096 independent trajectories and 400 normal
requests per trajectory. Candidate policies share exogenous random fields.
Discovery seed is 20261006 and independent confirmation seed is 20261007. The
main threshold grid is 25,000 to 150,000 inclusive, in steps of 5,000 tokens.
Centered secants initially use a 5,000-token step; a 2,000-token step is checked
separately for the baseline. Intervals are approximate 95% pointwise Student-t
Monte Carlo intervals, conditional on the model and price schedule.

The default workload has mean growth 2,000 tokens, Gamma CV 0.8, and output
fraction 0.25. Gaps are start-to-start Lognormal intervals of mean 90 seconds
and CV 1.5; cache TTL is 300 seconds and minimum eligible prefix is 1,024 tokens.
The initial context is 20,000 warm tokens. Normal ephemeral input and compaction
instructions each have 128 tokens. Recovery has 2,000 base summary tokens,
Beta retained fraction with mean 0.03 and concentration 30, and Lognormal
document size of mean 12,000 tokens and CV 0.8. The recovery fraction multiplies
the nominal threshold. Fixed extra compaction fee is zero.

Prices are illustrative USD per million tokens: uncached input 3, cache write
3.75, cache read 0.30, and output 15. Normal generated output is subsequently
charged as newly processed input when it reenters a request. No storage rent,
hard capacity, pricing tiers, or task-quality effects are assumed.

## Policy selection and independent confirmation

| Synthetic scenario | Discovery-grid selected threshold | Independent mean total USD | Conditional 95% interval USD |
| --- | --- | --- | --- |
| Baseline Gamma growth and random gaps | 40,000 | 14.263837 | 14.241362 to 14.286312 |
| Constant growth and gaps, random recovery | 45,000 | 12.490527 | 12.477953 to 12.503101 |
| Burst-mixture growth, baseline gaps | 35,000 | 13.916415 | 13.887168 to 13.945661 |
| Longer random gaps, expanded grid | 26,000 | 23.037659 | 23.003956 to 23.071363 |

The constant scenario changes both growth and gap laws; it is not an isolated
growth-variance causal comparison. Recovery remains stochastic in that control.
The burst law has probability 0.08, component mean multiplier 8, and component
Lognormal CV 0.8. Its component means are normalized so overall growth mean
remains 2,000. This changes dispersion and tail geometry, not just one moment.
The long-gap scenario changes mean gap to 360 seconds at the same CV 1.5.

These are finite-grid minima estimated on discovery marks, not unique global
optima. On the discovery grid, thresholds within one percent of its lowest
sample mean were:

- Baseline: 35,000, 40,000, 45,000.
- Constant growth/gaps: 40,000, 45,000, 50,000, 55,000.
- Burst growth: 35,000, 40,000.
- Expanded long-gap grid: 24,000, 26,000, 28,000.

This is an exploratory near-minimum set, not a confidence region or an
equivalence test. It illustrates why reporting a single exact token threshold
would imply more precision than the study supports.

## Boundary and finite difference probes

The original long-gap grid selected its lower endpoint, 25,000. Rather than
claiming an optimum there, a follow-up grid from 10,000 to 60,000 in 2,000-token
steps was run using the same discovery and confirmation seeds. It selected
26,000; recovery exceeds that threshold an average 5.649170 times per discovery
trajectory. The simulator records these events without clipping or an infinite
reset loop. The result is a broad local region, not an improvement claim over
25,000: the different grids are not nested and the estimated price differences
are very small.

For baseline paired secants, units USD per 1,000 threshold tokens:

| Threshold | Step 5,000 | Step 2,000 |
| --- | --- | --- |
| 35,000 | -0.039003 | -0.036394 |
| 40,000 | 0.004092 | 0.009261 |
| 45,000 | 0.030794 | 0.029187 |

The sign change persists in the coarse neighborhood, while its exact location
and magnitude depend on finite-difference step. Intervals exclude smoothing
bias and cannot establish an exact derivative of the token-rounded objective.

## Interpretation

### Holdout invoice decomposition added for the user briefing

The confirmation trajectories were reproduced at the already-selected policies
using seed 20261007 and 4,096 replicates. Their means exactly matched the
published confirmation estimates. The four disjoint token-category charges are:

| Scenario | Uncached input USD | Cache writes USD | Cache reads USD | Output USD | Mean compactions | Normal cache miss fraction |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline, h=40k | 0.416936 | 6.356514 | 3.075195 | 4.415193 | 29.557129 | 0.119404 |
| Constant growth/gaps, h=45k | 0.201714 | 4.416972 | 3.587176 | 4.284664 | 25.538330 | 0.063846 |
| Burst growth, h=35k | 0.516787 | 6.178325 | 2.719633 | 4.501669 | 32.867432 | 0.127422 |
| Long gaps, h=26k | 2.020428 | 14.128720 | 1.501522 | 5.386989 | 57.321045 | 0.445908 |

Normal misses include cold rebuilt prefixes after compaction as well as expiry;
they are not an expiry-only statistic. Outputs include both ordinary outputs
and generated summaries. Cache writes are approximately 45% of baseline cost
and 61% of long-gap cost, so eliminating read tokens alone is not the dominant
economic mechanism in those two configurations. The long-gap case incurs more
compactions at its selected policy and more cold writes; its smaller read bill
does not imply lower total price. The local reproduction probe is
.temp/report_breakdown.py and its generated data .cache/experiments/holdout-breakdown.json.

For a controlled idealized comparison, the earlier affine-cost parameters
s=20,000, g=2,000, k0=0.05, k1=p_r, and the same read/write prices give an exact
exponential-growth stationary threshold 58,873.789483, compared with
60,824.829046 from deterministic mean substitution. This isolates the stochastic
overshoot correction in the analytical benchmark. Neither is the 40k result
of the full simulator, which uses different recovery and overhead assumptions.

The scientific contribution at this stage is separating stochastic first
passage, state recovery, and cache expiry into an auditable invoice model.
Distribution shape and expiry can change the selected region even with a
declared growth mean; the study does not establish a universal direction of
effect, appropriate real-data distribution, or an unconditional 40k recommendation.

The no-compaction policy is included in each report, but its contexts are not
capacity constrained and may be unrealistic for a particular API/model. Do not
advertise its relative savings as an end-to-end production performance result.
Likewise, the earlier deterministic 60.8k example used different recovery and
overhead parameters; comparing it directly with the 40k stochastic result would
confound changes in assumptions with changes in mathematical treatment.

## Reproduction and artifacts

Use the standard root .venv installed with uv sync --locked. Main commands:

```sh
# All raw experiment output stays in the workspace cache.
uv run compaction-lab sweep --scenario baseline --replicates 4096 --calls 400
uv run compaction-lab sweep --scenario constant --replicates 4096 --calls 400
uv run compaction-lab sweep --scenario bursty --replicates 4096 --calls 400
uv run compaction-lab sweep --scenario long-gaps --replicates 4096 --calls 400
uv run compaction-lab sweep --scenario long-gaps --replicates 4096 --calls 400 --thresholds 10000:60000:2000 --difference-step 2000 --output .cache/experiments/long-gaps-expanded
uv run compaction-lab sweep --scenario baseline --replicates 4096 --calls 400 --difference-step 2000 --output .cache/experiments/baseline-step-2000
uv run compaction-lab symbolic
```

Every sweep saves its full workload, seeds, package versions, source hash,
per-grid Monte Carlo intervals, independent confirmation, and interpretive
limits in sweep.json. Paired trajectory prices are stored in trajectory-costs.npz;
plots are in sweep.png. Raw artifacts are regenerated, not committed.

The recorded source SHA256 is
870910fcebb6408f43cc71dd278ce399e6b03d5721c05b5810bf66917f23b30a.
The dependency lock SHA256 is
95c9b79fe2c147cab06bb0bd07bf88114e09afdc143d7ae9cf77a6b7846bf98f.
Environment: CPython 3.14.6, NumPy 2.5.3, SciPy 1.18.1, SymPy 1.14.0,
matplotlib 3.11.2, pytest 9.1.1, and uv 0.12.9 on Windows.

## Verification and remaining research

All 62 maintained tests passed. Ruff passed. Wheel and source distribution
builds succeeded; archive inspection found no .venv, .cache, or .idea contents.
Plots were visually inspected. Independent accounting/math review is recorded
in implementation-review.md and the stochastic analytic control in
stochastic-model.md. These checks support software correctness under stated
contracts, not empirical realism.

The first clean-checkout CI run exposed a test setup issue hidden by the local
workspace: pytest's configured .temp/pytest base directory requires an existing
.temp parent. Test initialization now creates that parent. The 58 non-temporary
tests had already passed remotely; this fix does not alter numerical source or
the recorded experiment source digest.

Next: obtain consented request-level traces, select candidate families using
held-out whole sessions and tail diagnostics, estimate conditional recovery
and temporal dependence, and rerun policy selection without treating model
parameter estimates as exact. Implement capacity/tier behavior before claiming
deployable thresholds for a specific API.
