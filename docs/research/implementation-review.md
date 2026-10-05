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
