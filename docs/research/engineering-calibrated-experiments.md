# Engineering-magnitude expected-invoice experiments

Recorded 2026-10-06. These runs replace the arbitrary 2k-summary/12k-document
CLI default with a published-median-anchored engineering scenario. They are
conditional expected-invoice calculations, not estimates of the public study's
population invoice or measurements of this user's private workload.

## Evidence and parameter translation

See [engineering evidence](engineering-context-evidence.md) for primary sources.
The closest observed full recovery magnitude is 65,588 tokens; generated
summary magnitude is 4,382. Both are reported marginal medians from one
engineer's Claude Code records, not fitted means. The scenario constructs
61,206 non-generated recovered tokens to match those two anchors. This residual
is neither a measured residual median nor a documents-only statistic.

Full recovery can contain system/tools/project guidance, preserved history,
summary, and reread files. Under the declared cold-reset accounting, billing
depends on the total recovered input and generated-summary output, so an
unidentified component split is not needed to price this scenario. A known
surviving cache prefix would require a different split/accounting scenario.
Do not add a system/tools prefix again to the full-context anchor.

The source's full-input measurement is used as a retained-reset-state size
proxy. Each next ordinary request still adds new retained input and an ephemeral
128-token suffix. Thus the simulator does not claim its first rebuilt API
request has exactly the measured full-input median. This boundary convention
is unchanged across the tested thresholds.

## Executable assumptions

| Parameter | Value | Status |
| --- | --- | --- |
| Generated summary C | 4,382 fixed tokens | Published median anchor; concentration premise |
| Aggregate non-generated reset A | 61,206 fixed tokens | Constructed residual, unknown component split |
| Rebuilt retained state C+A | 65,588 | Representative full-input magnitude proxy |
| Initial state | Same 65,588, cold | Controlled initialization |
| Normal growth | Gamma, mean 1,470 or 3,200; CV 0.8 | Source band-specific scales; synthetic mean assignment/CV |
| Normal request gaps | Lognormal, mean 90s, CV 1.5 | Unfitted synthetic timing control |
| Ordinary output | Rounded 25% of growth | Unfitted accounting control |
| Cache | Minimum 1,024; TTL 300s | Fixed accounting scenario |
| Input/write/read/output USD per million | 3 / 3.75 / 0.30 / 15 | Illustrative API rates, not subscription quotas |
| Horizon | 400 normal calls; compactor calls extra | Long-horizon fixed-workload control |
| Discovery grid | 75k through 300k, step 5k | Explicit finite policy search |
| Centered difference | 2k tokens | Paired secant, not exact derivative |
| Sampling | 4,096 independent trajectories, each stage | Monte Carlo expectation under assumed laws |
| Seeds | 20261006 discovery; 20261007 confirmation | Independent holdout evaluation |

The study reports growth around 1,470 at context above 200k and 3,200 below
50k. Neither is a universal mean across our entire grid. Using each as a
stationary positive-growth scale is a sensitivity intervention. No measured
recovery CV, joint distribution, or full-context decomposition was available.
The source's rediscovery step-equivalent proxy is not added as extra calls or
extra document tokens; our objective remains a fixed normal-call invoice.

## Results

| Conditional growth scale | Selected discovery grid point | Discovery grid within 1% of best mean | Holdout expected invoice, USD (95% MC interval) | Discovery mean compactions |
| --- | --- | --- | --- | --- |
| 1,470 tokens/call | 110,000 | 100k–120k, step 5k | 25.114124 (25.072087–25.156161) | 12.3862 |
| 3,200 tokens/call | 130,000 | 115k–145k, step 5k | 34.167656 (34.118259–34.217053) | 18.5891 |

The 1% sets compare discovery point estimates and are descriptive plateaus,
not simultaneous confidence regions for an unknown optimum. Confirmation
evaluates the selected point without selecting again. Conditional no-compaction
holdout invoice is 72.111235 for 1,470 growth and 142.031118 for 3,200 growth;
paired differences are -46.997111 and -107.863461 respectively. These are not
task-success savings or proof that keeping normal-call growth fixed matches
endogenous real-agent behavior.

The useful change is the scale: old 35k–45k synthetic regions cannot be reused
when the restored state itself is about 66k. Source medians provide a credible
engineering magnitude; their unavailable variance/decomposition remain
explicit sensitivity parameters rather than secretly fitted observations.

The source's own 220k threshold uses productive-step penalties and a different
cost objective. It is not a validation target for this four-price fixed-call
experiment. No quality penalty or productive-step denominator was introduced.

## Reproduction and environment

```shell
uv run compaction-lab sweep --scenario engineering --thresholds 75000:300000:5000 --replicates 4096 --calls 400 --difference-step 2000 --output .cache/experiments/engineering-anchors
uv run compaction-lab sweep --scenario engineering --thresholds 75000:300000:5000 --replicates 4096 --calls 400 --difference-step 2000 --growth-mean 3200 --output .cache/experiments/engineering-growth-3200
```

Run environment: CPython 3.14.6; package 0.1.1; NumPy 2.5.3; SciPy 1.18.1;
SymPy 1.14.0; Matplotlib 3.11.2; NumPy PCG64. Numerical outputs and plots are
generated under the ignored root .cache tree. Each JSON retains actual workload
parameters separately from published anchors, source digest, seeds, and interval
scope. No private traces, credentials, or live API calls are involved.
Recorded generator source SHA-256:
`6b3139079dc01e1ce1dd894b5135c72729a931187694f381c1921e4da5c34090`.

Next useful probe: hold total restored magnitude fixed and vary the genuinely
surviving eligible cache boundary, then calibrate growth/gaps with this user's
sanitized per-call usage records. That directly resolves price-relevant unknowns
without inventing a documents-only distribution.
