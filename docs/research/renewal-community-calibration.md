# Community calibration for analytical renewal models

Recorded 2026-10-06. This is an executed aggregate-data calibration, not a
synthetic workload fit. Its purpose is to supply measured growth scales,
overshoot-tail diagnostics, and serial-dependence controls for analytical models.

## Source, accounting, and selection

The pinned [UW SyFI TraceLab v0.0.2 release](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2)
contains 665,453 sanitized public model-call records. Attribution: UW SyFI
TraceLab authors; license CC BY 4.0. The compressed JSONL SHA256 is
`11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65`.

We select 305,445 Claude rows, group by provider/project/session ID/session file,
and order by round index then ingestion ordinal. There are 5,320 groups and
300,125 within-group adjacent transitions. For a transition from call t to t+1,
the aggregate growth proxy is

\[
G_t=\mathrm{fullInput}_{t+1}-\mathrm{fullInput}_t.
\]

**This already incorporates intervening model output and tool payloads. Adding
output again would double count it. Newly appended billable input is not used:
cache replay can make billing append differ from physical context growth.**

The primary stratum keeps nonnegative input differences between consecutive
round indices. A difference at most -64,000 marks a candidate large-drop event;
the next three transitions are excluded as a possible recovery window. Every
excluded transition breaks a run. Zeros remain zero, and negative changes are
not clipped to zero. The actual partition is:

| Transition class | Count |
| --- | ---: |
| Accepted | 297,091 |
| Negative input change | 1,041 |
| Nonnegative change within three calls after candidate drop | 1,993 |
| Nonconsecutive round indices | 0 |
| Total | 300,125 |

671 transitions satisfy the large-drop detector. They are **not confirmed
compactions**: input removal, alternate prompts, and transcript boundaries are
not identified. We do not remove quick rebounds with a future-state detector.
The accepted stratum is policy-conditioned and censored, not a policy-independent
distribution of every possible engineering action.

## Measured growth and its implications

| Statistic | Aggregate growth proxy | Output-only robustness proxy |
| --- | ---: | ---: |
| Observations | 297,091 | 305,445 |
| Mean | 1,836.4797 | 840.3106 |
| Standard deviation | 3,425.0803 | 1,517.4067 |
| Coefficient of variation | 1.8650 | 1.8058 |
| Median | 909 | 354 |
| 99th percentile | 14,299.2 | 7,163 |
| 99.9th percentile | 34,385 | 15,071.224 |
| Maximum | 310,365 | 64,000 |
| Zero share | 0.0007035 | 0.0008512 |
| Raw second moment | 15,103,793.1795 | 3,008,637.6357 |
| Raw third moment | 995,622,367,533.4 | 31,756,729,487.1 |

The largest approximately 1% of accepted growth values contribute **12.839% of
the first moment, 57.616% of the second, and 95.683% of the third**. This is a
consequential warning: a high-order diffusion or overshoot expansion can be
dominated by rare large tool payloads. These are empirical finite-sample moments,
not proof that population moments exist or are estimated precisely. A useful
theory must handle jumps or validate its approximation over the intended gap
scale instead of automatically substituting a Gaussian growth law.

The output-only proxy is deliberately an alternative incomplete growth law,
not an additive component of G. It isolates the effect of ignoring tool/user
payloads, without manufacturing a fixed 256-token background.

## Dependence survives removal of run heterogeneity

| Measurement | Growth | Output |
| --- | ---: | ---: |
| Pooled lag-1 correlation | 0.24190 (291,255 pairs) | 0.22958 (300,125 pairs) |
| Pooled lag-5 correlation | 0.12465 (270,665 pairs) | 0.15940 (282,327 pairs) |
| 16-call sum variance / matched IID sum variance | **3.15552** | **3.67691** |

The sum-variance comparisons use **disjoint intact 16-call blocks within runs**:
16,100 growth blocks and 16,925 output blocks. The IID baseline uses the exact
same block cohort's marginal variance, not the different all-row variance. For
growth, block-sum variance is 406,309,894.66 versus an IID reference
128,761,617.16.

Pooled correlation mixes within-run dependence and heterogeneity. Centering
each run of at least 16 observations by its own mean leaves growth lag-1
correlation **0.15981** across 274,844 pairs and lag-5 **0.03250** across 262,656
pairs. This diagnostic is not an unbiased causal estimator; estimated run means
can induce negative correlation. It nevertheless shows that heterogeneity alone
does not remove the observed short-range clustering.

There are 2,346 sessions with at least 16 accepted growth observations. Their
unweighted session means have median 1,838.37, p10 1,009.19, p90 3,572.54 and
coefficient of variation 0.55057. This is another reason to avoid presenting the
all-call mean as a universal engineering-task constant.

Growth and preceding output have pooled correlation **0.38822**. The explicit
dependence, and the fact that output is already included in G, rule out an
unexamined factorization into independent growth and output distributions.

## IID and block controls must have the same one-step marginal

Local pools live under `.cache/renewal-calibration/`:

- `growth-pool.npz`: 297,091 values, 5,836 uninterrupted runs, 232,186 eligible
  moving-block starts of length 16.
- `output-pool.npz`: 305,445 values, 5,320 session sequences, 250,166 eligible
  moving-block starts.
- `calibration.json`: aggregate metadata and exact measurements.

Each pool stores `values`, `block_starts`, `run_offsets`, `block_length`, and
`block_marginal_weights`. The growth pool additionally stores
`previous_output_tokens`, the billed output of the call immediately preceding
each input difference. Alignment with chronological growth runs is checked
exactly, including across excluded transitions. Its all-accepted mean is
**817.6686**, and its block-weighted mean **848.0400**. Previous output exceeds
the following accepted growth in **1.05052%** of all accepted transitions and
**1.07037%** under block weighting. This mark supports an ordinary-output invoice
baseline at fixed action count; it is **not** a retained terminal-tail size.
Hidden output, rewriting, and context retention are not identified, so setting a
terminal tail equal to billed output is an additional assumption, not measurement.

A uniform random moving-block start weights the middle
of long runs more heavily than run edges and excludes runs shorter than 16.
The resulting growth mean is **1,532.8794**, not the all-accepted mean 1,836.4797;
for output it is **871.3964**, not 840.3106.

To isolate serial dependence, compare uniformly sampled intact blocks to IID
sampling from `values` with probabilities proportional to
`block_marginal_weights`. Then both controls have exactly the same one-step
marginal. Comparing uniform IID over all values with uniform blocks without
this correction confounds dependence with cohort weighting.

## What reset and cache measurements do not identify

Candidate large-drop post-input has median **51,113**, p10 **30,952**, p90
**69,484**, and mean 59,242.34. It is total observed postdrop input, **not summary
length, mandatory reload amount, or the fully restored reset baseline**. Its
extreme upper tail confirms that a drop detector alone is not a clean reset
classifier. The four-file measured corpus,
[LangWatch's 65,588 aggregate example](https://langwatch.ai/research/finding-the-optimal-context-window),
or an assumed retained base plus 4,382 summary tokens can be
explicit scenario anchors; none identifies the hidden file-level reload process
from this sanitized dataset.

The token-weighted billed cache-read share is **0.9521736**, and creation share
**0.0471470**. Call-weighted mean shares are 0.9372561 and 0.0601302 respectively.
These are measurable **invoice exposure proxies**, not prefix-survival
probabilities or TTL estimates. Large fresh input can have low read share even
when every eligible old prefix survives. The illustrative four-price vector
(3, 3.75, 0.30, 15 USD per million tokens) remains a controlled pricing scenario,
not an inferred account/model quote.

## Recovery-window robustness

Removing the three-call exclusion, while still rejecting all negative changes,
yields 299,084 observations, mean **1,856.5863**, SD 3,502.0983, CV 1.88631,
and pooled lag-1 correlation 0.24529. The mean changes by about 1.1%; substantial
variance and dependence persist. This sensitivity does not validate the drop
detector as a compaction classifier.

## Reproduction and executed checks

```powershell
uv run python experiments/calibrate_renewal_trace.py
uv run python experiments/calibrate_renewal_trace.py --recovery-calls 0 --output .cache/renewal-calibration/recovery0
```

Both runs completed on the pinned full source, not a sample. Source digest,
complete transition partition, nonnegative retained growth, and the exact identity
`sum(block_marginal_weights) == 16 * len(block_starts)` were checked directly.
Ruff passes for the new calibration module and command. No new giant test suite
was introduced; these checks protect the measured cohort and fair comparison.
Raw rows, pseudonymous session identifiers, and source payloads are not published.
