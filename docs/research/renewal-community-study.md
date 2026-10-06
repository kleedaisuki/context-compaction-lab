# What analytic structure survives real community increments?

Executed 2026-10-06. This milestone prioritizes an analytic selection rule and
mechanisms, then uses discrete community-driven trajectories to investigate its
limits. It does not select a synthetic distribution and declare its Monte Carlo
minimum a universal sweet spot. Portable numerical evidence is
[renewal-results.json](renewal-results.json); the executable is
`experiments/renewal_community_study.py`.

## 1. Useful result, before numerical thresholds

For a project phase that must reconstruct a concentrated full working context S
after compaction, let L=H-S and let G be iid nonnegative ordinary context growth,
with g=E[G]>0. This includes prior retained model/tool content, not just billed
output. With Y_n=sum_{j=1}^n G_j, define the renewal measure and two occupations:

\[
U(L)=\sum_{n\ge0}\Pr(Y_n<L)=E[T_L],\quad
M(L)=\sum_{n\ge0}E[Y_n1_{Y_n<L}],
\]

\[
D(L)=LU(L)-M(L)=\sum_{n\ge0}E[(L-Y_n)_+]
                         =\int_0^L U(t)dt.
\]

Under homogeneous carry price c, affine compactor history price kappa, reset
surcharge F and baseline ordinary invoice b, A=F+kappa*S gives

\[
j(L)=b+cS+\kappa g+\frac{A+cM(L)}{U(L)}.
\]

Where a renewal density u exists,

\[
\boxed{j'(L)=\frac{u(L)}{U(L)^2}[cD(L)-A],\qquad D(L_*)=A/c.}
\]

The renewal function is not replaced by L/g; endogenous crossing and overshoot
remain in the equation. At an atom x of mass w, adding it changes the average
with sign c*(xU-M)-A. D is continuous and strictly increasing even for an integer
growth law, so the same crossing selects an exact optimal plateau. This is a
distribution-class structural theorem, not a density-fitting assumption.

The detailed proof and boundaries are in
[renewal-analytic-control.md](renewal-analytic-control.md). The delivered closed
laws, including Erlang-k and a hyperexponential mixture, are in
[renewal-closed-forms.md](renewal-closed-forms.md). The finite/continuous bridge,
including an exact bounded lattice ripple, is in
[continuum-bridge-theory.md](continuum-bridge-theory.md).

### Mechanisms revealed by the equation

1. **Reset cost versus integrated slack.** A/c is the natural control parameter;
   a larger reset invoice increases the gap. Distributional information enters
   through integrated renewal occupation, not a collection of unrelated means.
2. **Growth scale is not growth dispersion.** Scaling growth up increases the
   optimum sublinearly. At fixed mean, a convex-order spread raises D and lowers
   the optimum. A higher coefficient of variation alone is insufficient; the
   proof note supplies an exact reversal example.
3. **Affine compactor work on new history is an invariant.** Its rate contribution
   kappa*g does not depend on the threshold. Reprocessing the reconstructed S
   does affect A and therefore the optimum. Naively assigning all kappa*H to
   threshold-dependent overhead misses this cancellation.
4. **Ordinary output bills do not move this optimum by themselves.** At a fixed
   ordinary-action count their expected price is a baseline. Generated summaries
   are different: they recur once per reset and alter F and usually S.
5. **Reset randomness is analytically tractable.** For independent bounded reset
   S and H above its support, the core equation becomes
   E[D(H-S)]=E[A(S)]/c, not D(H-E[S])=E[A]/c. With exponential growth this has an
   exact mean/variance formula; concentrated resets need not be modeled as a
   broad independent Gamma variable.

These statements depend on the declared regeneration and ledger. They are not
assertions about arbitrary first-use file restoration, task phases, or TTL.

## 2. Four prices and mandatory re-input, not a hidden scalar fee

The illustrative, fixed price vector is input/write/read/output =
**3 / 3.75 / 0.30 / 15 USD per million tokens**. It is not a current model quote.
The production mechanisms informing this lane are exact-prefix reuse and
separate cache creation/read billing; the
[official caching documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
also makes clear that a stable prefix must have been written and that reuse is
subject to lifetime and breakpoint constraints. Independent Bernoulli hits here
are a controlled reduction of those mechanisms, not a fitted TTL model.

S is the complete reconstructed input, including generated summary C, stable
eligible base B, and mandatory material. **B and C are inside S.** On a live hit,
B survives the reset; the remaining S-B must be written on the next ordinary
request. Thus compulsory re-input is explicitly charged, not assumed to vanish
because a prose summary exists.

Let q be the independent matching-prefix hit probability and let theta split G
into current pre-call input (1-theta)G and a post-call cold tail theta*G. The split
is unidentified in sanitized public usage and is a sensitivity, not an inference
from billed output. With prices pi,pw,pr,po:

\[
c=p_w-q(p_w-p_r),\quad \kappa=p_i-q(p_i-p_r),
\]
\[
A_0=p_iK+p_oC+(p_w-c)(S-B)+\kappa S,\quad d=q(p_i-p_w),
\]
\[
j(L)=p_iI+p_oE[O]+(p_w-c\theta+\kappa)g+cS
       +\frac{A_0+cM(L)+d\theta E[G_{T_L}]}{U(L)}.
\]

K and I are the compactor/ordinary uncached instruction sizes, each 128 tokens
in this scenario. The crossing correction is **pi-pw, not pi-pr**: the final
generated/tool tail is read cold by the compactor before its normal cache write.
The deterministic empirical convolution computes E[G_T] instead of substituting
an average increment. The core root D=A0/c and the corrected minimum are recorded
separately; arbitrary marked laws are not claimed universally unimodal.

No additional model-mediated recovery request is included in this protocol.
The harness is assumed to reconstruct S directly; extra recovery calls, command
output and delays require their own paid transition, available in the existing
stateful working-set engine. Initial S is already warm, and no terminal compact
is charged. These endpoint choices materially affect short tasks.

## 3. Community calibration and fair dependence intervention

The pinned [UW SyFI TraceLab v0.0.2 release](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2)
is attributed to its authors under CC BY 4.0. SHA256, cohort rules and measured
aggregates are in [renewal-community-calibration.md](renewal-community-calibration.md).
We use 297,091 accepted adjacent Claude full-input differences: nonnegative,
consecutive rounds, outside a declared three-transition large-drop recovery
window. Negative changes are excluded, not clipped. This is a policy-conditioned
monotone cohort, not unfiltered counterfactual task growth.

Measured all-accepted mean is 1,836.48 tokens per action. The largest approximately
1% contributes 57.62% of the second raw moment and 95.68% of the third. A third-
moment asymptotic expansion therefore warrants numerical checks rather than
automatic preference over the exact empirical renewal equation.

For the dependence experiment, uniformly sampled intact 16-action moving blocks
have a different cohort weighting from all rows. We weight the IID control by
each observation's number of appearances in eligible blocks. Its mean growth is
1,532.88 and aligned billed-output mean is 848.04. Outputs are kept paired with
growth for invoices and are **never added to growth a second time**.

One independent uniform initial offset in 0..15 makes each block-path action's
marginal exactly equal to the IID control, even for truncated/nonmultiple horizons.
An independent review caught the original fixed-offset design; it was corrected
and the complete study rerun. Without that random phase, offset-specific growth
means ranged from 1,655.13 to 1,470.58, confounding finite-start comparisons.

All thresholds within a scenario see the same immutable action-indexed fields.
Scenarios use common IID growth/output/cache uniforms. The original raw integers
drive finite simulations; deterministic renewal evaluation bins to 5 tokens,
with a 25-token convergence control. There are 512 discovery trajectories per
mode and 512 independently seeded confirmation trajectories, at N=32,400,4000.

## 4. Numerical findings: an analytic prediction, not a magical constant

S=65,588 and C=4,382 are aggregate/summary magnitude anchors from the
[LangWatch single-practitioner case study](https://langwatch.ai/research/finding-the-optimal-context-window),
not a measured joint mean in TraceLab. B=20k is a declared within-S decomposition.
The larger-summary scenario preserves all non-summary material by raising S to
81,206 when C is raised to 20k. q is not inferred from the observed cache-read
token share.

| Declared mechanism | Analytic corrected H, tokens | Analytic USD/call | Raw IID N=4000 USD/call |
| --- | ---: | ---: | ---: |
| q=1, B=20k, C=4,382 | 112,848 | 0.052701 | 0.052619 |
| q=1, B=0, same full S | 119,498 | 0.054696 | 0.054594 |
| q=0.8, B=20k | 91,003 | 0.108699 | 0.108596 |
| q=0.5, B=20k | 83,093 | 0.186518 | 0.186420 |
| C=20k, S=81,206, q=1 | 152,666 | 0.064648 | 0.064525 |
| All growth pre-call, theta=0 | 113,193 | 0.053270 | 0.053184 |

The 5-token lattice determines the numeric representative, not production
precision. Use approximately 113k for the baseline scenario. An all-accepted IID
control, whose cohort differs, predicts approximately 116k; this must not be
misreported as a correlation effect.

**Cache reliability dominates fine threshold tuning.** Moving q from 1 to 0.8
raises the effective history carry price from 0.30 to 0.99 USD/million tokens;
the setup coefficient changes too. The conditional optimum moves earlier and
the rate approximately doubles. This is a sensitivity of the price mechanism,
not evidence that a measured 95% read-token share means q=0.95.

**Mandatory stable material is a useful design lever.** Keeping 20k of the same
S eligible and prefix-identical reduces rewrite expense: compared to B=0, the
analytic optimum moves about 6.65k earlier and the rate drops about 3.65%.
This is prefix preservation, not permission to retain arbitrary content without
matching bytes and a prior cache entry.

**Summary size has an economic price, independent of its quality benefit.**
Preserving more summary increases both output per reset and reconstructed S.
The 20k-summary scenario moves the conditional optimum about 39.8k later and
raises the modeled rate about 22.7%. Task quality is deliberately outside this
objective, so the experiment cannot conclude that larger summaries are bad.

### How much analytical simplification matters

For the matched empirical IID baseline:

| Approximation / exact-law calculation | H, tokens |
| --- | ---: |
| Fluid square-root leading term | 115,428 |
| First moment correction (second raw moment) | 112,780 |
| Third-moment integrated-renewal approximation | 113,511 |
| Exact empirical core crossing, no tail correction | 113,190 |
| Empirical four-price crossing-tail correction | 112,848 |

The fluid answer is about 2.6k later than the corrected empirical optimum.
The first correction is close in this scenario; the third moment is not
automatically better. These approximations cannot be promoted to universally
accurate closures merely because their algebra is more elaborate. The separate
closed-form study demonstrates a 56.8% gap error for a short-gap hyperexponential
moment approximation, versus a tiny error at sufficiently large gaps.

### Correlation: variance can matter more than the mean optimum

The calibration's disjoint 16-action growth sums have 3.16 times the variance
of a matched IID sum. After the corrected random-phase block intervention, the
N=4000 cost-per-call variance at the analytic line is **4.14 times** the IID value.
Observed means are 0.052719 (block) and 0.052619 (IID), but their different realized
output/growth means and Monte Carlo uncertainty do not support a precise causal
mean-cost shift. The curve and its minimum remain very similar in this mechanism.

Both discovery modes picked 113,848 on their exploratory grids. Fresh confirmation
found that point slightly more expensive than the predeclared analytic 112,848:

| N=4000 confirmation | Selected minus analytic USD/call | Approximate paired MC 95% half-width |
| --- | ---: | ---: |
| IID | +0.00001026 | 0.00001155 |
| Random-phase blocks | +0.00000940 | 0.00001375 |

The microscopic optimum is not resolved to 1k by these samples, and the observed
near-flat bottom does not justify aggressively tuning it. Both main long-horizon
grids place all sampled thresholds from about 106k to 126k within 1% of the lowest
full invoice. This grid region is descriptive, not a uniform confidence set.

### Finite remaining work changes the answer more

N=32 discovery selects a much higher threshold: 150,588 for IID and 165,588 for
blocks. Independent paired confirmation gives:

| N=32 confirmation | Higher-threshold rate | Analytic long-run-line rate | Reduction |
| --- | ---: | ---: | ---: |
| IID | 0.045231 | 0.047500 | 4.78% |
| Random-phase blocks | 0.044524 | 0.046348 | 3.94% |

The paired improvements are 0.002269 +/- 0.000268 and 0.001824 +/- 0.000234
USD/call, respectively (approximate conditional MC 95% intervals). At N=400 the
small chosen refinements show no confirmed improvement. At N=4000, above, they
also fail to improve on the analytical line. A no-compaction benchmark is included
without imposing a hard context cap; it lies in the short-horizon 1% grid region,
but not the long-horizon region. This benchmark is infeasible if a real provider
ceiling binds and must then be removed.

The mechanism is not mysterious: initial S is sunk/warm, and the task ends before
enough future carrying is saved to repay a reset. The finite-horizon recursion
in the theory note, rather than a forced terminal compact, is the correct route
when remaining work is predictable or has an estimated stopping hazard.

## 5. What was checked, and what was not

The empirical renewal convolution's whole residual is below 1e-10 (about
floating-point roundoff). Changing quantum from 25 to 5 moves the primary
corrected threshold by 15 tokens and rate by 0.000000411 USD/call. This is a
numerical refinement observation, not a proved universal binning-error bound.
A constant-growth 10,000-action four-category ledger agrees with its analytic
rate to 9.18e-8 USD/call; the difference is the finite start/end effect. A direct
four-action crossing check proves the implementation does not bill a terminal
compact and reconciles input/write/read/output independently.

SymPy checks Laplace transforms, derivative identities, marked-tail formulas,
moment constants and compatibility with the existing exponential model. Lean
checks the atomic renewal-average comparison and lag-advance algebra as well as
the existing uniform-approximation regret law. It does **not** formalize all
renewal integration, the empirical source or Python simulator. Precise scope is
in [lean-structural-verification.md](lean-structural-verification.md). Independent
scientific review and exact cycle crosschecks are in
[renewal-study-review.md](renewal-study-review.md).

No large new parameterized pytest suite was added for this milestone. Existing
accounting/API regression checks remain compatibility protection, not a research
contribution. The useful research evidence is the identities, independent ledger
comparison, actual calibrated curves and mechanism-discriminating comparisons.

### Scope and next high-value investigation

These simulations are counterfactuals under an explicit mechanism and an empirical
cohort, not replay-based estimates of actual policy costs. Changing compaction
may change future growth and file demand. Full mandatory reconstruction is one
project-phase protocol, not an assertion that every document is needed every cycle.
Independent hit marks omit TTL/delay coupling. Random-phase blocks preserve local
dependence but not complete sessions, long phases or policy-dependent recovery.

The community case study reports growth conditional on current context and a
recovery period; our iid reduction deliberately does not import its productive-
step denominator into a fixed-ordinary-call objective. Its 220k result and our
113k scenario optimize different assumptions and objectives, so they are not
competing measurements of one universal constant.

The next most informative extension is to estimate **joint conditional growth,
mandatory restoration and cache survival by project phase**, plus the remaining-
work hazard. That lets the existing controlled-history model decide when a scalar
renewal line suffices and when an adaptive state policy buys material savings.
Neither adding independent random variables nor replacing every large tool jump
with a diffusion is an adequate substitute.

## 6. Reproduction

Standard root `.venv`, `uv`, src layout; no credentials or paid model calls.
Use the pinned trace-download command in the README, then:

```powershell
uv sync --locked
uv run python experiments/calibrate_renewal_trace.py
uv run python experiments/renewal_closed_form_derivation.py
uv run python experiments/finite_continuum_bridge.py
uv run python experiments/renewal_ledger_crosscheck.py
uv run python experiments/renewal_community_study.py
./formal/verify.ps1
```

Recorded study used Python 3.14.6, NumPy 2.5.3, 512 discovery and 512 independent
confirmation trajectories, N=32/400/4000, deterministic seed schedule in the JSON,
and `OPENBLAS_NUM_THREADS=1`; the main study took 19.35 seconds on this execution.
The portable JSON records actual runtime version metadata; that metadata takes
precedence over any environment prose if the runtime is updated. Generated raw
pools, logs and `renewal-vs-community.png` remain under root `.cache`; only compact
aggregates and source/method documents are published. No raw rows or pseudonymous
session identifiers are committed.
