# Independent scientific review of the renewal community study

Recorded 2026-10-06. Scope: `renewal_numerics.py`,
`experiments/renewal_community_study.py`, and `renewal-study-contract.md`.
This review does not alter production implementation. It focuses on physical
invoice timing, renewal crossing, sampling fairness, and uncertainty.

## Findings requiring correction

### R1: block sampling originally matched pooled, not action-index marginals

The original `fields(..., mode="block")` started every trajectory at block
offset zero, sampled intact length-16 moving blocks uniformly, and truncated
the concatenation to `calls`. `block_marginal_weights` matches the marginal
of a uniformly chosen position in a complete block. It does **not** match the
law of every fixed action index in this original sampler. Horizons divisible
by 16 match the pooled marginal; arbitrary accepted `--long-calls` horizons
also distort the pooled marginal through the last partial block.

Concrete deterministic counterexample: one source block `[0,1,...,15]`.
Matched IID mean at *every* action is 7.5, but original block mean on action
1 is 0. Its expected mean over 401 actions is `3000/401 = 7.4812967581`,
not 7.5. This is not sampling noise.

The real growth pool confirms a material positional difference: expected
growth at offsets 0/15 is 1,655.131752/1,470.575569, versus the matched IID
mean 1,532.879396. All 16 offset means decrease across the block. Thus
original short-horizon comparisons mix serial dependence with initialization
phase, even when their overall mean matches. The original 4,000-action
default matches the pooled marginal but does not eliminate this finite
startup distinction. Do not label it pure dependence isolation.

Required correction: uniformly randomize one initial offset in `0..15`
per trajectory, independently of all sampled block starts, draw sufficient
complete blocks, and take the shifted `calls`-long window. For any fixed
action `t`, its offset is `(initial_offset+t) mod 16`, hence uniform; its
containing source block is still uniformly sampled. This gives exactly the
same joint growth/output marginal as the IID weights at *every action*,
including nonmultiple horizons. Keep growth/output paired through the same
index. A shuffled/rotated block individually would have different dependence
semantics; the single initial offset on concatenated intact blocks is the
appropriate minimal correction. Existing main results must be rerun.

The integrator accepted this correction. Final source/probe confirmation is
recorded below rather than rewriting the original defect away.

### R2: the bin-refinement threshold check was one-sided

Original check: `quantum25_vs5_marked_threshold_tokens < 100`. A negative
10,000-token discrepancy would pass. Required correction: `abs(delta)<100`.
The recorded original run has delta **+15 tokens**, so this is a faulty
guard, not evidence that the existing run failed its intended tolerance.

## Checks that passed

### Physical four-category timing and terminal tail

Independently expanding the expected cycle ledger gives

`c=p_w-q(p_w-p_r)`, `kappa=p_i-q(p_i-p_r)`,

ordinary growth coefficient `p_w-c*theta`, compactor growth coefficient
`kappa`, and terminal-tail correction `q*(p_i-p_w)*theta*E[G_T]`.
The terminal mark avoids a normal cache write but is consumed as uncached
compactor input, so `p_i-p_w`, **not** `p_i-p_r`, is correct. The first
post-reset normal request uses the surviving base `B`, not all reconstructed
`S`, giving reset penalty `q*(p_w-p_r)*(S-B)`. Stable base is inside `S`.

`simulate_renewal_ledger` bills the old prefix and uncached tail before
rebuilding, then writes the reconstructed suffix and current pre-call
growth. Output is billed separately and not added into aggregate growth
again. This matches the contract's declared proportional timing model.
It does not identify the real timing split or compulsory recovery rounds;
those restrictions are clearly declared.

### Exact empirical renewal recurrence and >= crossing

The recurrence retains zero growth through the factor `1/(1-p0)`. Duration
and area sum renewal visits **strictly below** the gap. The marked forcing
uses `G >= residual_gap` and therefore correctly includes equality crossings.
Its convolution uses the full terminal increment, not only the overshoot.
The renewal-equation residual checks all computed atoms, not just zero.

An independent residual-gap dynamic program, unrelated to the implemented
mass/convolution calculation, used increments `{0,1,3,8}` with probabilities
`{.2,.2,.3,.3}`, gaps `{1,3,8,17,55}`, cache hits `{0,.6,1}`, and timing
fractions `{0,.4,1}`: **45 exact cycle comparisons**. Maximum absolute errors
in duration, area, terminal increment and invoice rate were respectively
`3.55e-15`, `1.71e-13`, `3.55e-15`, and `4.34e-19` USD/action.
This confirms these formulas for the tested finite law, including zero
increments, equality crossings and fractional timing; it is not a fit test.

### Finite horizon and initialization

The simulator tests the crossing before the *next* ordinary action, so no
terminal compaction is billed. An independent four-action probe with
`S=100, G=20, H=180, theta=.4, q=1, ordinary_output=7` gives zero resets and
`(I,W,R,O)=(512,72,496,28)`. The final retained context reaches `H` without a
terminal setup charge. Initial cache availability is the declared warm `S`;
subsequent resets retain only the declared eligible `B`.

Consequently long-run analytic rate is not an exact finite invoice. The
reported `simulation_minus_prediction` must be described as a combination
of finite-boundary effect, raw-versus-binned-law effect and Monte Carlo
variation, not solely prediction error or an invalidated theorem. The current
contract states this restriction; preserve it in the result narrative.

### Prediction and selection uncertainty

Monte Carlo SEs are across independently sampled trajectories; paired
threshold contrasts use common ordinary-action fields. Their uncertainty is
conditional on the fixed empirical pool and scenario, not source/population
uncertainty. Independent confirmation of selected versus analytic candidates
appropriately removes reuse of discovery noise for that contrast.

The discovery grid minimum remains exploratory. Its 1% region is descriptive,
not a simultaneous confidence region for a global optimizer; confirming one
selected candidate does not certify grid/global optimality. Near-optimal
plateaus are more supportable than a population-optimal token threshold.
These are interpretation requirements, not requests for a large test suite.

## Reproducibility

The maintained bounded crosscheck is
`experiments/renewal_ledger_crosscheck.py`; run
`uv run python experiments/renewal_ledger_crosscheck.py` from the repository
root. Its compact aggregate artifact is
`.cache/renewal-ledger-crosscheck/results.json`. It requires no source trace,
network or API call. No pytest suite was added.

The independent DP first computes **four expected token categories**, not
an expected bill via the target renewal formula. Each residual state accounts
for one normal request; zero increments form a self-loop divided out by
`1-p0`; positive increments either move to a smaller residual or cross and
bill an independently calculated compactor input/cache split. A previous
tail transfers tokens from next-request read to write; the initial
reconstructed-base transfer is included once. Prices are applied only to
the final category vector. It calls `analytic_rates` only to obtain the
comparison target and does not call `ledger.coefficients` inside the DP.

The earlier disposable `.temp/renewal_review_probe.py` supplied real-pool
offset measurements and the no-terminal-reset example; that script is not
the maintained source of the category-level crosscheck.

## Final corrected-source status

The integrator changed `fields` to concatenate intact sampled blocks, draw
an independent uniform initial phase, and take a shifted trajectory window.
Its block count `(calls+2*length-2)//length` is sufficient even for the maximum
initial phase. Growth/output still use identical selected indices. The
bin-refinement guard now uses `abs(delta)<100`.

Independent corrected-source probe: with the single `[0,...,15]` source block,
65,536 sampled trajectories and 17 calls, action 1/17 means were both
7.5322113 (finite random-phase sampling error around 7.5). Enumerating all
16 initial phases exactly gives zero per-action marginal-mean discrepancy
for horizons **1, 16, 17 and 401**. The underlying argument also proves full
distribution matching, not just equal mean, because every action samples
every source offset uniformly. No remaining marginal-matching defect was
found in this corrected design.

The 45-case category-level DP reproduced the original numerical discrepancies
after being strengthened to price only independently computed category
counts. Ruff checks passed for the maintained experiment. The integrator
reports the main study rerun completed with corrected random-phase sampling;
that full run is owned by the integration track, not independently replicated
here. Report its corrected output rather than the superseded fixed-phase
block results.

Review recommendation: **physical renewal implementation and corrected block
design pass this bounded audit. R1/R2 are fixed; preserve conditional-uncertainty
and finite-boundary labels when interpreting the rerun.**
