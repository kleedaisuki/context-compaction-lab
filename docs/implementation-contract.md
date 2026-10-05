# Stochastic simulator implementation contract

The primary objective is expected total API price for fixed N normal requests.
No task-quality metric, empirical distribution claim, storage rental, context
capacity, long-context price tier, or subscription accounting is implicit.

Shared configuration is src/context_compaction_lab/config.py. PositiveSpec,
Pricing, RecoverySpec, and Workload are the source contracts.

## Exogenous random field

Generate arrays of shape (replicates, calls): growth tokens, request-start gaps,
recovery fractions, and reloaded document tokens. Align marks by ordinary call
index, not compaction count, to use common random numbers across thresholds.
Round growth to nearest integer with minimum one token; outputs are rounded
output_fraction*growth and the remainder is newly retained input. Documents
are rounded nonnegative tokens. No upper-tail clipping is permitted.

Initial first-call gap is zero. Beta fractions are constant at endpoints 0 or
1; otherwise use alpha=mean*concentration and beta=(1-mean)*concentration.
All random-field arrays are immutable by contract and simulator must not
mutate them. Current initial implementation assumes independent marginals.

## Normal request ledger

State per replicate: retained tokens X and available cached prefix P. Initially
X=initial_context and P=X if warm_start and eligible, else P=0.

At a normal request start, the prior prefix can be reused only if P>0 and the
sampled start-to-start gap does not exceed TTL (or TTL is None). A normal
request's cacheable input is X+new_retained_input. If that total reaches the
minimum cache length, a hit reads P and writes the remaining input; a miss
writes the entire cacheable input. Otherwise the entire input is uncached
and the available cache prefix becomes zero. The ephemeral normal input is
always uncached and excluded from retained history. Outputs are billed and
appended to X, but are not yet in P. After the request P equals its cacheable
input when eligible, and X equals that input plus generated output.

## Compaction ledger

Before a normal call, if X>=threshold, run at most one compaction. It reads P
if the old prefix is warm, bills X-P plus instructions as uncached input,
or bills all X plus instructions as uncached on a miss. Do not write old
context: the compressor's varying suffix is not selected for caching. Bill
generated summary tokens and optional fixed non-token overhead.

Summary tokens = round(summary_base + fraction*basis), where basis is either
the nominal threshold or actual X. New X = summary + sampled document tokens.
Set P=0: this branch-specific prefix has changed and must be rebuilt on the
normal request. Document insertion is billed there, not twice on compaction.

Recovery may exceed threshold. Record that event; do not silently cap it.
At most one compaction precedes each ordinary request, so recovery overshoot
cannot cause an infinite reset loop. No compaction occurs after the final
ordinary request. An infinite-threshold policy means no compaction.

The cache is a branch-specific matching prefix. Stable system content is
omitted. Compaction summaries are outputs, reloaded documents are inputs;
normal generated output is newly processed on the next request. TTL tests
use request-start gaps that already incorporate normal generation and tools.
Post-compaction recovery duration cannot salvage the invalidated prefix.

## APIs and ownership

distributions.py: sample_positive(spec, rng, size) -> ndarray.
calibration.py: fit_positive_samples(values) -> JSON-compatible candidate
fits with log-likelihood, AIC, BIC, KS distance, family parameters and warnings.
Use gamma and lognormal MLE with location fixed to zero; reject nonpositive
and nonfinite observations. KS is descriptive, not a calibrated p-value.

simulation.py: RandomField, SimulationResult dataclasses;
draw_random_field(workload, replicates, seed) -> RandomField;
simulate(workload, threshold, random_field) -> SimulationResult. Result arrays
per replicate: costs, input_tokens, write_tokens, read_tokens, output_tokens,
compactions, cache_hits, cache_misses, recovery_above_threshold, max_context.
Input categories are disjoint; costs equal their price-weighted sum plus
fixed compaction overhead. Cache hit/miss counts cover normal requests.

inference.py and cli.py are owned by the root integrator. Statistics use
independent trajectories as units. Paired threshold differences use identical
fields. Interval estimates quantify Monte Carlo error conditional on model,
not empirical uncertainty in assumed workload parameters.
