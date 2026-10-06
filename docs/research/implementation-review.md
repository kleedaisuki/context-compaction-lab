# Independent implementation review

Recorded 2026-10-06. Scope: config, distributions, calibration, simulation,
inference, analytic, packaging metadata, implementation contract, and stochastic
model. CLI integration and remote GitHub state were not reviewed here.

## Assessment

No demonstrated accounting or statistical-unit defect was found for valid
configured inputs under the explicitly documented v0.1 assumptions. The model
correctly separates the four billing categories, charges generated output again
as input only on a later request, invalidates mutable prefixes after compaction,
retains recovery and growth overshoots, and excludes trailing compactions.
Paired comparisons use independent trajectories as units and do not advertise
finite differences as exact gradients. The full finite simulator is not claimed
to equal the separate exponential renewal benchmark.

## Findings delivered to integrator

1. **P2, config.py: RecoverySpec and Workload validators.** Token-count fields
   only check negativity; NaN and fractional values can bypass the claimed
   validated domain contract. Reproduced `Workload(calls=2,
   initial_context=float("nan"))` and `RecoverySpec(summary_base=float("nan"))`:
   draw two trajectories and simulate at threshold 1; costs become `[nan,nan]`
   without simulator rejection. `calls=1.5` is accepted by construction and
   fails later in NumPy with TypeError. Require nonnegative finite integers for
   counts, positive integer calls, and actual bool warm_start; reject malformed
   assumptions at their configuration boundary. Add parameterized regressions.

2. **P2, inference.py: sweep_thresholds input boundary.** `difference_step=0`
   passes grid validation then divides identical outcomes by zero, emits a
   RuntimeWarning, and fails as nonfinite inference samples. Validate strictly
   positive finite step explicitly before building random fields or policies.
   Negative steps should also be rejected despite algebraic sign cancellation.

3. **Release hygiene, historical symbolic research note.** Reproducibility
   instructions contained machine-specific workspace and Python executable
   paths. Replace them with portable repository-relative uv commands before
   public release, in accordance with project privacy instructions. The old
   script is ignored/nonpackaged; avoid presenting it as an installed package
   command.

These items were reported while integration remained in progress; status must
be updated after fixes rather than treating this snapshot as unresolved proof.

## Independent analytic check

An independently generated Poisson-cycle Monte Carlo probe used seed 8742 and
100,000 cycles. For H=60000, S=20000, mean exponential growth g=2000,
read=0.30e-6, write=3.75e-6, k0=0.05, k1=0.30e-6, and b=0.018:

- Draw n ~ Poisson((H-S)/g); cycle length n+1.
- Conditional arrival locations are n iid Uniform(0,H-S).
- Read area = S*(n+1) + sum(arrival locations).
- Crossed context = H + independent Exponential(g).
- Reward = b*(n+1) + read*area + k0 + k1*crossed + (write-read)*S.
- Estimate using sum(reward)/sum(length), not mean(reward/length).

Observed rate: USD 0.03626771362415654 per ordinary request.
Symbolic rate: USD 0.03626666666666667 per ordinary request.
Relative discrepancy: 2.8868313139751578e-5. This is a stochastic check of the
ideal benchmark, not a calibration of real workload or the full simulator.
Probe ran with repository-local `.venv/Scripts/python.exe`; all marks
were synthesized and no API credentials or private traces were accessed.

## External contract check and limitations

The official Anthropic prompt-cache documentation explicitly measures lifetime
from request start and counts response generation against TTL. It describes
moving cache boundaries where prior assistant output is newly written as input
on the subsequent request. These support the simulator's stated start-gap and
output-tail semantics. Reference consulted 2026-10-06:
https://platform.claude.com/docs/en/build-with-claude/prompt-caching

The current model intentionally omits multiple surviving cache boundaries,
provider routing, actual compaction latency, context capacity, price tiers,
empirical joint dependence, and quality feedback. These are documented scope
limits, not defects in this release. Public release testing must still verify
CLI, build artifacts, clean installation, and tracked-file privacy.

## Integration recheck

The integrator added integer configuration validation and early positive-finite
secant-step validation. The exact NaN initial-state, NaN summary, fractional-call,
and zero-step reproductions above now raise ValueError at their intended
boundaries. Findings 1 and 2 are resolved as of this recheck; the optional bool
warm_start tightening is not a release-blocking finding.

`uv run pytest tests/test_config.py tests/test_inference.py tests/test_simulation.py -q`
completed with **35 passed in 14.07 seconds**. The user's revised setup uses a
standard full root `.venv` and maintained root `tests/`. No production files
were modified by this reviewer.

The integrator subsequently sanitized historical workspace/interpreter paths
and marked the old temporary calculator as a historical, unsupported interface.
Finding 3 is resolved by integration cleanup. Whole-package CLI, tests, and
archive checks are recorded separately in the initial experiment report.

## v0.1.1 focused recovery correction review

Recorded 2026-10-06 after the user clarified near-constant recovered context.
Reviewed changed RecoverySpec defaults, optional absolute summary marks,
verbatim preservation and declared cache survival, CLI legacy/narrow controls,
and tests/test_recovery.py. This is a focused executable-contract review, not
an empirical validation of the user's recovery law.

No concrete accounting or backward-constructor-compatibility defect was found:

- Defaults now generate a fixed 2,000-token summary and insert 12,000 document
  tokens, rather than coupling recovery length to threshold.
- Verbatim preserved tokens are capped by available old context and billed as
  subsequent request input, not as newly generated summary output.
- Surviving prefix is at most both the old warm prefix and the declared leading
  preserved boundary. The configuration requires preservation and minimum
  cache eligibility. Expired prefixes remain cold. Algebraically, this keeps
  `0 <= prefix <= recovered context`, so write-token counts stay nonnegative.
- Four-positional-array RandomField construction remains supported; the new
  optional immutable summary field is appended. Distributed summaries require
  explicit marks instead of silently substituting a mean. Legacy proportional
  summary semantics remain available through explicit parameters/CLI scenario.
- Fixed versus narrow recovery draws preserve the same ordinary growth and
  request-gap samples for a common seed. Legacy parameters are reconstructed
  explicitly; changing the default is an intentional premise correction.

Independently ran `uv run pytest tests -q`: **75 passed in 2.86 seconds**.
Existing hand-accounted tests cover surviving/expired prefixes, preservation
without output fees, and unavailable-summary rejection.

One integration documentation discrepancy was reported to the integrator:
implementation-contract.md still stated unconditional `P=0` and recovered
`X=summary+documents`, omitting preservation/cache survival and optional
absolute summary marks at the review snapshot. Update those equations and the
exogenous-mark schema before publishing; the production transition itself is
consistent with the new typed contracts. The integrator subsequently updated
that implementation contract to match all three corrections, resolving the
documentation discrepancy. CLI/build remote publication and empirical recovery
calibration remain outside this focused review.

## Engineering aggregate profile review

Recorded 2026-10-06. Scope: profiles.py, aggregate RecoverySpec field and
simulator billing, engineering CLI defaults, tests/test_profiles.py, and
engineering-context-evidence.md. No production files modified.

The profile consistently distinguishes a reported full-input median (65,588)
and generated-summary median (4,382) from its constructed aggregate residual
(61,206). It does not label subtraction of marginal medians as a measured
residual/document median or a fitted population mean. Initial cold state,
conditional high-context growth scale 1,470, CV/output/gap assumptions, and
unidentified component decomposition are disclosed. Aggregate reset payload
is billed once as input on the next ordinary request and not as output.
No invoice defect was demonstrated under valid inputs. RecoverySpec appends
the new field, preserving old positional parameter order.

**P2 CLI override ordering:** `_scenario` validates the restored-input override
before clearing the original document mean. A valid final requested aggregate
configuration therefore fails at an invalid intermediate state. Reproduction:

```shell
uv run compaction-lab sweep --scenario baseline --restored-input-tokens 61206 --documents-mean 0 --calls 2 --replicates 8 --thresholds 75000:80000:5000 --output .cache/review-aggregate-transition
```

Observed error: `Aggregate restored input cannot overlap documents or
preservation.` The same final RecoverySpec can be constructed directly.
Collect related recovery overrides and validate one final replacement rather
than depending on a sequence of individually valid intermediate dataclasses.
Reported promptly to integrator; correction pending at this snapshot.

Independently ran `uv run pytest tests -q`: **81 passed in 3.25 seconds**.
The suite does not yet cover the CLI transition reproduced above. These checks
validate scenario arithmetic and executable accounting, not public-study raw
traces, joint distributions, or threshold transferability.

Engineering review resolution: `_recovery` now gathers related overrides and
performs one final validated replacement. The exact baseline-to-aggregate CLI
reproduction now completes and writes its artifacts under
`.cache/review-aggregate-transition`. Independent focused recheck:
`uv run pytest tests/test_profiles.py -q` -> **7 passed in 2.21 seconds**,
including the new order-independent override regression. The P2 above is
resolved. No remaining concrete finding in this bounded review.
