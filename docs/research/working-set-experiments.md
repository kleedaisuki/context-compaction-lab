# Working-set compaction economics: implemented experiment results

Recorded 2026-10-06; package v0.2.0. This milestone replaces research-only
recommendations with an executable versioned-working-set simulator, empirical
output-block resampling, actual source-file size measurements, paired policy
experiments, exact controls and independent validation.

## 1. Decision result

For the user's concentrated compulsory-working-set premise, use the **mandatory
limit**, not the phase-local alternative: the fine-grid selected threshold is
**126,000 tokens**, and the 2k-spaced discovery points within 1% of the best
expected invoice span **116k-138k**. This is conditional on the declared 61.3k
whole-file catalog, 20k stable base, 4,382 summary, fees and task law below.

When only part of that catalog is needed at each action, first-use restoration
changes the event law. The phase-local fine-grid selection is **78k**, with a
1% region **68k-86k**. A single universal 100k-120k recommendation is therefore
not supported across these mechanisms. These regions are descriptive discovery
plateaus, not confidence sets for a global optimum or production advice.

## 2. What is measured versus controlled

Four complete real source files were fetched at fixed commits and counted with
`tiktoken` 0.14.0 / `cl100k_base`. Their bytes and SHA-256 are recorded in the
portable [result metadata](working-set-results.json). Source bodies remain in
ignored .cache and are not redistributed with the project.

| File | Proxy tokens | Pinned source |
| --- | ---: | --- |
| Jinja filters.py | 13,876 | [source](https://github.com/pallets/jinja/blob/15206881c006c79667fe5154fe80c01c65410679/src/jinja2/filters.py) |
| Rich text.py | 10,417 | [source](https://github.com/Textualize/rich/blob/72e3bb33d44fd96881f7742b77137983907a942f/rich/text.py) |
| CPython asyncio/base_events.py | 15,836 | [source](https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Lib/asyncio/base_events.py) |
| Django query.py | 21,189 | [source](https://github.com/django/django/blob/9e7cc2b628fe8fd3895986af9b7fc9525034c1b0/django/db/models/query.py) |
| Total | **61,318** | Cross-repository corpus, not a measured typical task's required set |

This tokenizer is a reproducible size proxy, not the exact Claude tokenizer.
Whole-file requirements are an explicit workload intervention; partial reads
or patch-derived facts can require much less input. A 64-token wrapper is
added per supplied file observation. With the controlled base/summary, eager
post-reset state is `20,000 + 4,382 + 61,318 + 4*64 = 85,956` tokens.

Ordinary output lengths are resampled from the pinned sanitized UW SyFI
TraceLab v0.0.2 public release, provider=claude, preserving released rows and
within-session chronological order. There are 305,445 output observations;
descriptive mean=840.310639, SD=1,517.406737, median=354, p99=7,163. Zero
outputs are retained. The moving-block pool has 250,166 eligible 16-call starts.
Uniform sampling of valid starts is a declared call-weighted block bootstrap;
its marginal is not identical to uniformly sampling all released rows because
short sessions and boundary weights differ. This preserves dependence within
blocks, not the complete joint behavior of actual agents.

Attribution: UW SyFI TraceLab authors, dataset CC BY 4.0.
[Release](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2).
Digest: `11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65`.

We do **not** add measured fresh-append or positive-context-delta samples to
explicit file restoration: those already contain cache replay/file input and
would double count. Measured output-only blocks and controlled non-file input
are cleanly separated from restored payloads.

| Unmeasured controlled component | Primary setting |
| --- | --- |
| Stable base / generated summary | 20,000 / 4,382 tokens; base is not a measured system-prompt share |
| Ordinary non-file input | 256 retained tokens plus 128 ephemeral suffix |
| Ordinary work | 400 fixed actions; short sensitivity 40 |
| Demand | At most one file required with probability .85; .9 hot-file preference; 25-action hot phases |
| External version changes | Independent probability .002 per file/action; churn sensitivity .02 |
| Automatic qualifying observations | None in main experiments; supported and tested separately |
| Ordinary request gaps | Lognormal mean 90s, CV 1.5; policy-extra delays excluded |
| Cache / trigger | Minimum 1,024, TTL 300s; atomic default; strict diagnostic alternative |
| Fees USD / million input-write-read-output | **3 / 3.75 / 0.30 / 15**, illustrative fixed prices |
| Optional recovery model round | 64 generated command tokens, 64 uncached instruction tokens; whole existing context billed |
| Retention control | Latest valid whole-file observations fitting 20k, not generic recent-turn retention |

The **mandatory** case requires all four files at every ordinary action. It
tests the fast-saturating concentrated recovery limit, rather than asserting
that every real engineering operation needs every old file. File-version sizes
stay constant; obsolete prompt text is billed until actual compaction removes it.

## 3. Production refactor and protocols

The new engine keeps separate current versions, valid resident snapshots,
qualifying-read versions, snapshot recency, matching-prefix length/age, retained
context, and remaining ordinary work. It prices normal requests, compactors,
and optional recovery-model requests with one disjoint four-category ledger.
Payloads are input, never summary output. Ordinary observations remain fixed
even when a separate prerequisite read occurs before the operation.

`atomic` permits a complete prerequisite-read/operation unit after one reset.
`strict` rechecks the threshold after restoration and can recreate the missing
prerequisite. Bounded repeated attempts stop as infeasible: their partial bills
are never averaged as completed-task savings. There is no terminal compact.
Stable prefix survival requires a previously warm eligible matching boundary;
expired entries cannot be resurrected by retaining identical text.

Old `sweep`, `fit`, `symbolic`, Workload and legacy recovery interfaces remain
available. The packaged new entry points are `prepare-working-set` and
`working-set`, not temporary sys.path scripts or an alternate interpreter.
See [contract](../working-set-contract.md) and [independent validation](working-set-validation.md).

## 4. Primary paired experiment

Coarse grid 40k-240k, step 10k; paired centered contrasts at +/-5k. Each case
uses 2,048 discovery trajectories (seed 20261006) and 2,048 independent
confirmation trajectories (20261007). Every policy/threshold within a case
uses the same immutable ordinary action field. Output, gap and mutation RNG
streams are separated from demand controls. Fees and ordinary count are fixed.

Each policy's threshold, including the no-compaction alternative, is selected
on discovery data and then frozen for confirmation. Loops reject a complete
policy point rather than censoring failed trajectories. The intervals below
are conditional pointwise Monte Carlo uncertainty, not parameter/tokenizer
error or simultaneous selection coverage.

| Phase-local policy | Selected h | Confirmed USD (95% MC interval) |
| --- | ---: | --- |
| Eager, rebuilt base cold | 130k | 31.2434 (31.1448-31.3420) |
| First use, rebuilt base cold | 90k | 24.2897 (24.2122-24.3673) |
| Eager, stable 20k boundary survives | 130k | 30.6022 (30.5060-30.6985) |
| First use, stable boundary survives | 80k | **22.9665 (22.8934-23.0396)** |
| Retain 20k file observations and guards | 90k | 24.4286 (24.3492-24.5080) |
| Retain 20k text but clear read guards | 100k | 26.3346 (26.2529-26.4164) |
| Eager plus real recovery model round | 130k | 30.7680 (30.6713-30.8647) |
| First use plus recovery model round | 80k | 23.7356 (23.6603-23.8110) |

At their discovery-selected thresholds, eager-warm minus first-use-warm is
**USD 7.635728**, paired confirmation interval **7.592276-7.679180**;
first-use is about **24.95%** cheaper. First-use no-compaction benchmark is
68.0502 (67.6330-68.4673), within this abstract unconstrained-capacity model.

Crucially, optimized first use restores **801,484 payload tokens**, more than
eager's **690,421**, yet costs less. Retention restores fewer (**587,475**), yet
costs more than first use. Total reload tokens are not a sufficient statistic.

| Optimized phase policy | Uncached USD | Write USD | Read USD | Output USD |
| --- | ---: | ---: | ---: | ---: |
| Eager warm | .4356 | 12.1026 | 12.1855 | 5.8786 |
| First use warm | .5145 | 9.0952 | 6.8057 | 6.5511 |
| Retention warm | .5064 | 9.7765 | 7.7633 | 6.3824 |

Earlier cleanup spends more summary-output money but reduces full-prefix
rewrites and repeated carries. Retained tail text is cold after the rewritten
conversation boundary; it is still input and its future repetitions are paid.

## 5. Mechanism sensitivities

| Case | Eager warm selected h / USD | First-use warm selected h / USD | Interpretation |
| --- | --- | --- | --- |
| Phase local | 130k / 30.6022 | 80k / 22.9665 | Delayed working-set arrival matters |
| Diffuse uniform demand | 130k / 30.7454 | 120k / 29.2017 | Rapid saturation narrows the benefit |
| All files mandatory each action | 130k / 30.8170 | 130k / 30.8170 | Concentrated-constant recovery is a valid limit |
| High external revision churn | 130k / 32.2947 | 80k / 23.6580 | Stale text is not evicted free |
| Both compact/recovery extra delay 360s | 130k / 31.8971 | 90k / 30.1490 | Cache expiry erodes lazy restoration's advantage |
| Stable base 0 | 100k / 26.6669 | 60k / 18.9630 | Physical threshold depends on prompt overhead |
| Stable base 40k | 150k / 34.5201 | 100k / 26.9701 | Same primitive task, larger stable base |

In the mandatory case, eager, first-use and valid-guard retention have **exactly
identical complete invoices** in this model: the same full payload must be in
the next ordinary input, regardless of whether supplied by a new read or a cold
copied snapshot. Retention reduces measured reloads without eliminating input
charges. Clearing retained read guards instead raises optimized invoice to
33.6510. This equality does not claim that actual network I/O, recovery models
or provider-specific tail caching are universally free.

Strict eager restoration fails for every sampled trajectory at grid thresholds
40k-80k: its 85,956-token required reset cannot fit below the strict line.
Strict first-use fails at 40k. Those points have null expected completed-task
cost. The strict first-use selected 80k bill is 23.5539 versus atomic 22.9665,
demonstrating extra reset/recovery costs even above the loop boundary.

The 40-action sensitivity is not forced to compact. Eager selects 190k with
only .0073 mean compactions; many near-equivalent high thresholds are effectively
no compaction. First use selects 80k with 1.4165 mean compactions. Do not turn
the exact eight-action no-compaction control into a universal short-task rule.

### Joint retention-budget and threshold experiment

Retention was also optimized jointly with the threshold rather than judged
only at one arbitrary 20k budget. Five whole-file budgets (0, 12k, 20k, 40k,
64k) were compared on the phase-local workload with a real batched recovery
model round enabled. Every budget preserves qualifying read guards and the
same 20k stable base boundary. Threshold grid=60k-160k by 10k, 1,024 discovery
and 1,024 independent confirmation trajectories, seeds 20261010/20261011.
The joint budget/threshold selection uses discovery data only.

| File-retention budget | Recovery delay 0: selected h / confirmed USD | Recovery delay 360s: selected h / confirmed USD |
| --- | --- | --- |
| 0 | **80k / 23.7657** | **90k / 31.4377** |
| 12k | 90k / 25.0624 | 100k / 31.7911 |
| 20k | 90k / 25.1175 | 100k / 31.9174 |
| 40k | 100k / 26.8237 | 110k / 32.3302 |
| 64k | 120k / 29.7522 | 120k / 31.4437 |

Discovery selected zero file retention in both conditions. With zero extra
delay, retaining more costs substantially more. With 360s recovery delay,
the entire catalog fits the 64k budget and avoids many real recovery requests:
it almost ties zero retention. The paired confirmed difference, zero minus
64k, is -0.006029 USD (95% interval -0.100050 to 0.087993), so these data do
not establish which is cheaper. Intermediate budgets remain more costly;
for example zero minus 20k is -0.479665 (-0.543733 to -0.415597).
Thus retention's response is not monotone in this delay stress case, and
partial retention can be worse than either dropping files or keeping all.
This condition changes ONLY extra recovery delay, with compactor delay zero;
it is distinct from the earlier sensitivity delaying both by 360s. Neither
360s value is a measured production latency. The experiment prices API bills,
not the user's wall-clock delay or tooling/network I/O costs.

## 6. Independent fine-grid confirmation

After coarse exploration, preselected first-use-warm policies were refined
using NEW discovery/confirmation seeds 20261008/20261009 and 4,096 trajectories
per stage. Phase grid=60k-110k, step 2k; mandatory=100k-160k, step 2k; contrast
step=2k. No re-selection on confirmation outcomes.

| Required-file law | Selected h | 1% discovery grid region | Confirmed USD (95% MC interval) |
| --- | ---: | --- | --- |
| Phase local | **78k** | **68k-86k**, step 2k | **22.954254 (22.903439-23.005068)** |
| All files mandatory | **126k** | **116k-138k**, step 2k | **30.778354 (30.711815-30.844894)** |

### Expected-cost slope, not a deterministic derivative shortcut

The fixed-work objective is `J_N(h, pi) = E[C_N(h, pi)]`. Each path uses the
disjoint ledger `C = p_i I + p_w W + p_r R + p_o O`, including ordinary,
compactor and real recovery requests. Expected total category counts depend
on the endogenous threshold crossings, restored versions and cache state.
Consequently, fixed recovery-size means alone cannot determine the optimum.

The implemented threshold is integer-valued and the trigger law is discontinuous.
We estimate the scale-dependent centered secant
`[J_N(h + delta, pi) - J_N(h - delta, pi)] / (2 delta)` with paired common
ordinary task paths, rather than asserting an exact ordinary partial derivative.
For the fine grids, delta=2k. Below, values are USD per additional 1,000 threshold
tokens, for all 400 actions, with paired 95% Monte Carlo intervals:

| Required-file law | h | Paired centered slope / 1k tokens |
| --- | ---: | --- |
| Phase local | 68k | -0.058233 (-0.060949 to -0.055517) |
| Phase local | 74k | -0.013985 (-0.016852 to -0.011118) |
| Phase local | 78k | +0.003410 (+0.000365 to +0.006455) |
| Phase local | 86k | +0.028200 (+0.024837 to +0.031563) |
| All mandatory | 116k | -0.062441 (-0.064969 to -0.059912) |
| All mandatory | 126k | -0.001141 (-0.004113 to +0.001832) |
| All mandatory | 138k | +0.035499 (+0.031692 to +0.039306) |

Both scenarios exhibit a sign change consistent with their empirically selected
sweet regions. A discrete grid minimum does not require its centered secant to
be exactly zero: the phase 78k example illustrates that distinction. Portable
metadata contains every evaluated discovery-grid cost and paired secant,
including failed points, not only the selected minima.

The actual integer/discrete reward law need not be smooth or unimodal.
The [exact 256-path control](working-set-exact-control.md) scans all 1..299
integer thresholds, checks true-probability expectations and Monte Carlo,
demonstrates a finite-horizon no-compaction optimum, a finite interval optimum
under an explicit read-price stress case, independent-clock bias and a real
recovery-batching reversal. We therefore use paired differences for large
experiments, not an unjustified continuous pathwise gradient or golden-section
unimodal search. All new engine and legacy tests currently pass: 284 tests.

## 7. Reproduction and boundaries

Prepare the pinned public JSONL.gz in `.cache/community-data` (publisher URL
and digest above), then use the standard root .venv:

```shell
uv sync --locked
uv run compaction-lab prepare-working-set --trace .cache/community-data/syfi-v0.0.2.jsonl.gz
uv run python experiments/run_working_set_study.py --replicates 2048 --jobs 2
uv run compaction-lab working-set --policies first_use_warm --replicates 4096 --seed 20261008 --thresholds 60000:110000:2000 --difference-step 2000 --output .cache/experiments/working-set-fine-phase
uv run compaction-lab working-set --demand mandatory --policies first_use_warm --replicates 4096 --seed 20261008 --thresholds 100000:160000:2000 --difference-step 2000 --output .cache/experiments/working-set-fine-mandatory
uv run python experiments/working_set_retention_sensitivity.py
uv run python experiments/summarize_working_set_study.py
uv run python experiments/working_set_exact_control.py
```

The original main seven cases and separately executed base sensitivities are
retained in the lightweight result metadata; default study runner now executes
all nine. Full JSON, trajectory costs, logs and figures stay under .cache.
The generator source SHA-256 for these numerical runs is
`1b7da9784717449dc78bb877ee56607bfa7b94496067f458e9f3eef252e74cac`.
CPython 3.14.6, NumPy 2.5.3, SciPy 1.18.1, SymPy 1.14.0, Matplotlib 3.11.2,
tiktoken 0.14.0; package 0.2.0; independent NumPy SeedSequence streams.

No real model API was called. These experiments combine real size/output
measurements with explicit synthetic prerequisites/timing; they are not replay
of complete observed engineering tasks or estimates of this user's quota.
Whole-file snapshots and qualifying automatic observations are supported;
partial/range/patch-derived facts and unobserved provider routing/eviction are
not inferred. Prices are flat, compressor shares them, hard model context
capacity is not enforced, and maximum retained context is diagnostic rather
than a provider-capacity certificate. Those limitations do not invalidate the
within-model paired mechanisms, but they limit literal production threshold
recommendations. The concentrated mandatory limit is the relevant result when
the user's fixed working set truly saturates immediately.
