# Research plan: expected invoice-optimal compaction thresholds

Recorded 2026-10-06. Mathematical specification: [stochastic-model.md](stochastic-model.md). Historical deterministic calculator: [compaction-threshold-symbolic.md](compaction-threshold-symbolic.md).

Premise refinement in v0.1.1: the main recovery state uses project-specific
constant or low-dispersion absolute sizes rather than a broad H-proportional
law. H3 below is a legacy/general sensitivity hypothesis, not the primary
assumption. The completed fixed versus small-CV study is recorded in
corrected-recovery-experiments.md; next calibration should estimate retained,
generated-summary, and reread sizes separately before expanding model scope.

## Decision and scoped contribution

**Decision:** select an integer-token compact trigger minimizing expected total API invoice for a declared normal-request horizon and workload law. The initial project delivers a reproducible simulation laboratory, an exact stochastic analytic control, uncertainty estimates, and reusable trace-calibration interfaces. It does not claim to know the user's actual traffic distribution.

Why this matters: holding a prefix is cheap per token but repeated; compacting changes stopping times, invalidates caches, creates additional requests, and induces rereads. Replacing all these quantities by deterministic means can change the selected threshold. A mechanism-based model should show which source of randomness actually changes the decision, not merely add random noise to a previous curve.

### In scope for the first release

- Fixed threshold policy, fixed number of normal calls, declared initial cache state.
- Positive random growth, random compacted/recovered size, random inter-request intervals.
- Disjoint input/write/read/output accounting, including compact calls and cold rebuilt prefixes.
- Synthetic gamma/lognormal/mixture scenarios with explicit parameters; independent marginals initially, correlated controls as a stated follow-up.
- Finite Monte Carlo expected invoice and paired threshold comparisons.
- Exact exponential-growth renewal benchmark and expected-rate derivative.
- Headless machine-readable experiment outputs and a compact report.

### Deliberately deferred

Task quality, learned/adaptive policies, automatic real-model execution, multi-agent shared cache routing, speculative lookahead, every provider's exact caching boundary scheme, and joint TTL-policy optimization. These are potential extensions, not prerequisites to a useful first result.

## Hypotheses and discriminating studies

These are research hypotheses, not conclusions to pre-fill in generated reports.

| ID | Hypothesis | Controlled comparison | Evidence that rejects or narrows it |
| --- | --- | --- | --- |
| H1 | Growth variance/tails can materially move the invoice-optimal region at fixed mean | Deterministic, gamma, lognormal, burst-mixture growth with equal means; optional equal CV pair | Same threshold region and negligible held-out regret over studied parameters |
| H2 | Gap geometry around TTL changes cost and the selected threshold at fixed mean gap | Compare independent gamma/lognormal/pause-mixture gaps, with matched means; correlated latent controls follow later | Paired cost difference indistinguishable from zero or too small to affect choice |
| H3 | Recovery conditional on crossing changes reset frequency and shifts the optimum | `S=s0+U*h` versus `S=s0+U*crossed_context`, same marginal parameter targets where possible | Differences explained entirely by changed mean rather than conditional dependence |
| H4 | Long-run renewal recommendation can be suboptimal for short finite sessions | Horizons 20, 100, 400 and a long-run control; identical initial state | No practically meaningful held-out finite-horizon regret |

Define “material” before the confirmatory run, for example expected invoice regret exceeding a chosen dollar or percentage threshold. Report the threshold itself, optimum-region width, and near-optimal regret, rather than treating a 1k-token shift as automatically important.

## Experimental protocol

### A. Cheap mathematical controls first

1. Run deterministic degenerate laws to recover the previous accounting convention where it applies.
2. Validate cold one-call, warm one-call, all-hit, all-miss, no-terminal-reset, and no-compaction paths with hand invoices.
3. Compare simulated exponential growth cycles with exact `E[T]`, expected retained-token sum, overshoot, renewal rate, and derivative in the analytical benchmark. Keep its ideal warm ledger separate from full-cache results.
4. Demonstrate numerically why `E[cycle_cost/cycle_calls]` is not a correct pooled cost rate.

### B. Threshold sweep with paired randomness

Declare a finite threshold grid, horizon, initial condition, scenario parameters, price configuration, RNG algorithm/version, and seeds in the run manifest. Use the same primitive exogenous stream across candidate thresholds. v0.1 recovery marks are keyed by replication and **ordinary-request index**, not compact-event count; do not let extra compact draws shift future ordinary growth/gap draws. Different policies may use/transform a shared recovery mark differently, which is part of the policy effect. See the immutable random-field contract in [implementation-contract.md](../implementation-contract.md).

For replication `m`, v0.1 records `C_m(h)`, compaction count, normal cache hits/misses, recovery-above-threshold count, maximum context, and token-category totals. Event-level crossed sizes/overshoots, restored sizes, and compact cache hits/misses are useful future diagnostics; do not imply they are present in the aggregate output. Estimate

\[
\widehat J_N(h)=M^{-1}\sum_m C_m(h),\qquad
\widehat{\mathrm{SE}}(\widehat J)=s_C/\sqrt M.
\]

Confidence intervals should state their method and are conditional on the scenario law. A normal approximation is a first diagnostic, not guaranteed coverage under a rare-burst law; increase independent replications or bootstrap complete trajectories. For costs differences and finite-difference sensitivities, use the sample variance of paired trajectory differences, not the sum of separate marginal variances.

Common random numbers reduce variance only when the pairing helps; check rather than assume. A finite-difference step `delta` is explicit, and multiple steps distinguish sampling noise from smoothing bias. A derivative of sample stopping times is not used as an unbiased pathwise gradient.

### C. Selection without winner's-curse reporting

Use discovery seeds to select a candidate/near-optimal region, then evaluate that frozen choice and predeclared baselines on separate confirmation seeds. Independent holdout evaluation estimates the selected policy's expected cost without the minimum-of-noisy-estimates optimism. If the “reference optimum” is estimated on the same confirmation sample, comparisons to it still have selection bias; either use an independently selected reference or report simultaneous/full-grid uncertainty without claiming exact regret.

The deterministic mean-plugin threshold, a sensible fixed fraction baseline, and the no-compaction policy (when capacity-feasible) are initial comparators. A robust sweet region can be defined as all thresholds whose supported excess cost is below a declared tolerance; do not silently equate overlapping pointwise confidence intervals with an equivalence test.

### D. Sensitivity before realism claims

Vary one mechanism at a time: growth dispersion/tail, restored fraction, reread base, and gap mass around TTL. Growth-gap correlation is a follow-up once the independent-marginal controls are validated. Use a small factorial design only after individual mechanisms are understood. Scenario weights must be declared if aggregating; equally averaging arbitrary scenarios is not an estimate of actual workload expectation. Do not assume increasing variance universally raises cost or universally moves the optimum in one direction; both are scenario-specific results to measure.

Do not label this study a measured production benchmark. Synthetic outcomes support statements about the model and its mechanisms. Once traces exist, fit and validate as specified in `stochastic-model.md`, and then repeat held-out policy selection on whole sessions.

## Units, invariants, and interpretation

- Money is USD or an explicitly configured currency; token prices always state per-token versus per-million conversion.
- Cache write is a replacement category, not an add-on input charge.
- Summary output charged once can subsequently appear as cache-written input; those are two different API events and legitimately two charges.
- Restored context contains reread documents; reread tokens cannot disappear from subsequent calls by definition.
- Output appended after an ordinary call is not cached for free before its next input use.
- The workload stream is fixed across policies; a price saving under this intervention is not a task-success claim.
- Fixed threshold is separate from hard capacity. v0.1 omits capacity and price tiers and reports maximum context; a capacity-aware follow-up must report safety behavior and failure probability under unbounded growth.
- Finite-horizon estimation and stationary-cycle estimation are separately named commands/results; do not call every correlated reset simulation “renewal.”

## Durable run artifacts and reproducibility

Keep generated experiment files under repository-root `.cache` and temporary probes under `.temp`. Commit lightweight scenario configurations, source/tests, lockfile, mathematical notes, and an illustrative **synthetic** report only after checking it. Do not commit virtual environments, API secrets, or large/generated traces. A release report records source commit, `uv.lock`, Python/package versions, configuration, seeds, replication count, runtime, and output paths.

An experiment must be repeatable through the project's `uv run` CLI; exact spelling is owned by the implementation and documented in the root README. Preserve raw per-replication results when practical so uncertainty can be recomputed. Record failed alternatives when they change the interpretation (for example a clipped recovery law, missed capacity safeguard, or derivative estimate dominated by step size).

## Acceptance and next decision

The first release is useful when:

1. The src-layout package builds and the CLI recreates a threshold sweep from a saved configuration.
2. Ledger and boundary tests pass, plus exact stochastic controls under their own assumptions.
3. The report gives expected cost with uncertainty, selected threshold/near-optimal region, and paired comparisons, clearly marked synthetic.
4. The source and docs agree about what is simulated, including cache timing, recovery projection, and finite termination.
5. A GitHub repository contains the environment lock, package, tests, mathematical model, research plan, and an explicit limitations statement.

The next valuable research decision is which observed variable most affects threshold regret: growth tails, reread size, or cache-age/context-size correlation. Collect minimal token/timestamp traces to discriminate them. The preliminary gamma/lognormal location-zero MLE interface reports likelihood/AIC/BIC and descriptive KS distance; it is a calibration starting point, not a validated empirical fit or a distribution hypothesis test. More distribution families or a sophisticated learned policy are not substitutes for the decision-relevant evidence.
