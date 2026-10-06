# Price vectors, sensitivity regimes and executed community confirmation

Executed 2026-10-06. This milestone follows the
[renewal study](renewal-community-study.md): derive conditional directions and
switching surfaces first, then measure their economic importance on the pinned
community workload. It does not estimate task quality or compare actual model
execution. [Portable results](price-sensitivity-results.json) contain all 35 cases.

## 1. The useful distinction: control response versus invoice response

For a fixed external workload/cache law and feasible policy set, let m(h) be
expected disjoint input/write/read/output token usage. Then

\[
J_p(h)=p\cdot m(h),\qquad J^*(p)=\inf_h p\cdot m(h).
\]

This statement does not require iid growth, a scalar threshold, or an infinite
horizon. The optimized invoice is nondecreasing in each price, concave in the
price vector, and homogeneous of degree one. Uniformly scaling all prices
changes all invoices but not the set of optimal policies. Where differentiable,
the envelope gradient is optimized expected usage. At policy ties, active usage
vectors are supergradients, not a unique ordinary gradient.

The compaction trigger need not be monotone in an individual price. What is
monotone is optimized use of that repriced resource. If old and new optimal
policies have old-price bills b0,b1 and repriced-resource usage u0,u1, then

\[
b_0\le b_1,\qquad b_1+\delta u_1\le b_0+\delta u_0
\quad\Longrightarrow\quad u_1\le u_0\quad(\delta>0).
\]

`repriced_optimal_usage` is now kernel-checked in
[Lean](lean-structural-verification.md). This is an exact structural law, not
a fitted trend. The envelope interpretation connects to Milgrom and Segal's
peer-reviewed [Econometrica paper](https://doi.org/10.1111/1468-0262.00296);
our price-linear specialization has the self-contained argument above.

## 2. Derivation of the threshold response

Keep the regenerative lane explicit: ordinary nonnegative iid retained growth G;
fixed full reconstructed context S, stable eligible prefix B, generated summary
C, compactor instructions K, independent ordinary-boundary hit probability q.
Let L=H-S, T be the first cumulative growth crossing L, U(L)=E[T], and
M(L) the expected sum of pre-call cumulative growth. Integrated renewal lag is
D(L)=LU(L)-M(L), with D'=U wherever U is continuous.

For p=(p_i,p_w,p_r,p_o), define

\[
c=(1-q)p_w+qp_r,\quad
A=p_i[K+(1-q)S]+qp_w(S-B)+qp_rB+p_oC.
\]

The canonical core optimum solves D(L*)=A/c. With
a=(K+(1-q)S,q(S-B),qB,C), v=(0,1-q,q,0), R=A/c,

\[
\boxed{\partial_{p_j}H_*={a_j-Rv_j\over cU_*}},\qquad
\epsilon_{L,p_j}={D\over LU}
 \left({p_ja_j\over A}-{p_jv_j\over c}\right).
\]

The price delays compaction exactly when its setup-cost share exceeds its
history-carry share. All four gap/threshold price elasticities sum to zero;
optimized invoice price elasticities sum to one and equal expenditure shares.
These are different vectors answering different questions.

The [full theory](price-sensitivity-theory.md) includes mixed derivatives,
material-path derivatives, boundary cases and proofs. In particular,

\[
\operatorname{sign}\partial_{p_w}H_*
=\operatorname{sign}\left[q p_r(qS-B)
 -(1-q)\{p_i[K+(1-q)S]+p_oC\}\right].
\]

Under positive read price and nonempty volatile reset material, the numerator
has a unique q crossover. Its sign is independent of the growth-law family and
of p_w itself; that law changes the location and magnitude of the response.
The main anchors give **q_w=0.8857444074**. Below it expensive writes favor
earlier compacting of miss-written history; above it expensive mandatory
reconstruction writes favor delaying compact. Read-price increases normally
favor earlier compact, but the opposite core regime is possible when
p_w B > p_i(K+S)+p_o C and q is sufficiently low.

### Retaining the crossing-tail mechanism

The core reduction must not erase the uncached tail generated just before a
compact. Let theta be the post-call retained share, zeta(L)=E[G_T],
kappa=(1-q)p_i+qp_r and d=q(p_i-p_w). The full rate is

\[
j(L)=p_i I+p_o E[O]+(p_w-c\theta+\kappa)E[G]+cS
 +{A+cM(L)+d\theta\zeta(L)\over U(L)}.
\]

Where the renewal measure has a density u, its stationarity equation is
cD-A-d theta chi=0, with chi=zeta-U zeta'/u. For exponential growth,
chi=g[2-(2+L/g)exp(-L/g)] and chi'>0. At q=1, the full write-price
direction has numerator **S-B-theta*chi**, not just S-B. A thin volatile
reset can therefore reverse the core direction even with perfect hits.

The empirical lane is atomic: it evaluates the full marked ledger on 5-token
renewal cells, with an unbounded-right-tail certificate for every case.
Canonical D-inverse derivatives are only returned away from positive renewal
atoms. Grid switches use finite contrasts; they are not fabricated smooth
derivatives. The empirical finite +5% write-price transition is around q=.90,
not an exact derivative theorem or the same number as the core .885744 boundary.

### Why optimizing every tiny price change is usually unnecessary

At a smooth core interior optimum, let u=U', w=a-Rv. The local optimized-price
Hessian and old-policy retuning regret are

\[
\nabla_p^2 j^*=-{u\over cU^3}ww^T,\qquad
\mathrm{regret}\simeq {u\over2cU^3}(w\cdot\delta p)^2.
\]

Only one price direction affects this scalar control locally: the Hessian has
rank at most one and is negative semidefinite. Uniform scaling is in its null
space. A visibly moving optimum can still have negligible retuning benefit,
because near-optimum loss is second order. These formulas apply to a smooth
active core branch, not to atomic switches, constraints or the global marked
price surface. At policy switches use exact price-linear margins instead.

## 3. Data, fixed assumptions and executed procedure

- Source: public [UW SyFI TraceLab v0.0.2](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2),
  CC BY 4.0, attributed to its authors. SHA-256:
  `11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65`.
- The previously calibrated pool has 297,091 nonnegative full-input growth
  observations outside three-call recovery windows after large-drop candidates.
  The matched 16-action block marginal has mean retained growth 1,532.8794 and
  aligned ordinary billed output 848.0400 tokens. These are not an identified
  causal decomposition of retained output, files and cache state.
- Main controlled anchors: S=65,588; B=20,000; C=4,382; K=I=128; q=1;
  theta=1. These are declared/calibrated scenario anchors, not a joint fit.
- Deterministic renewal evaluation selects the policies first. Confirmation
  then uses 512 fresh trajectories of 4,000 ordinary calls under both matched
  iid and intact 16-action blocks, with a random initial block phase.
  Seeds: 2026102601 and 2026102602. Normal output is billed once and not added
  to retained growth a second time. Initial reset is warm; no terminal compact
  or separate paid model-mediated recovery round is invented.
- Price-only groups simulate one immutable four-category ledger and reprice
  it. Mechanism groups share action-index fields but separately update q,
  material or timing. Price-sign controls use their OWN same-mechanism
  old-price optimum; comparing them to the global 113k policy would confound
  price effects with cache/reset effects.
- Paired intervals are conditional Monte Carlo uncertainty given this pool
  and scenario, not population, corpus-selection or actual-provider uncertainty.
  Long-run analytic choices are not asserted to optimize finite/block invoices.

## 4. Actual tariff projections on the same workload

Official first-party prices verified 2026-10-06, USD per million tokens, ordered
(input,write,read,output). Full marked H, rounded here to the nearest token:

| Price projection | Vector | Selected H | Long-run USD/ordinary action | Old 112,848 policy excess over new optimum |
| --- | --- | ---: | ---: | ---: |
| Sonnet 4.6 / 5m | (3,3.75,.30,15) | 112,848 | .052701 | 0 |
| Sonnet 5.5 / 5m | (2,2.50,.20,10) | 112,848 | .035134 | 0 |
| Opus 5.5 / 5m | (4,5,.20,20) | 132,838 | .051699 | 1.560% |
| Fable 5.1 / 5m | (10,12.50,.25,50) | 161,263 | .103148 | 5.731% |
| Sonnet 5.5 / 1h tariff ONLY | (2,4,.20,10) | 121,578 | .039170 | .393% |
| GPT-5.3-Codex / effective write | (1.75,1.75,.175,14) | 113,728 | .034681 | .004% |

Sources and semantics: [price-vector evidence](price-vector-evidence.md),
[machine-readable rates](price-scenarios.json),
[Anthropic official pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[OpenAI official pricing](https://developers.openai.com/api/docs/pricing).
The GPT-5.3 effective write=input convention is specific to that earlier caching
schedule, not a claim about all current OpenAI models. Storage-hour charges
cannot be represented by these four token rates alone.

Changing a quoted vector here does NOT change tokenization, model behavior,
summary quality, reset size, eligibility or cache lifetime. In particular the
1h row holds q fixed: it isolates its write tariff, not actual TTL survival.
The Sonnet 4.6/5.5 pair proves common scaling: identical thresholds/categories,
pathwise costs times 2/3 and variances times 4/9.

Fresh block confirmation gives retuning savings relative to old-policy expense
of **1.566%** (Opus), **5.470%** (Fable), and **.430%** (Sonnet 1h tariff).
GPT's .015% finite estimate is unresolved: the paired difference is
-0.0000052490 +/-0.0000079980 USD/action at conditional 95% coverage.
The analytic percentage column uses NEW optimum expense as denominator;
simulation savings use OLD expense. They should not be silently equated.

## 5. Which variables move what, and when?

### Local main-scenario price sensitivities

| Coordinate | Core gap price elasticity | Optimized physical invoice price elasticity | Full marked H after +20% price |
| --- | ---: | ---: | ---: |
| Input | +.000824 | .015823 | 113,133 (+285) |
| Write | +.366752 | .198757 | 115,923 (+3,075) |
| Read | -.508587 | .505569 | 108,668 (-4,180) |
| Output | +.141011 | .279850 | 114,183 (+1,335) |

The core gap elasticities sum to zero; bill elasticities sum to one. Core
absolute-H elasticities are smaller by L/H. Input price has almost no core
effect at q=1 because only K enters A, but the full cold-tail correction makes
its H shift much larger: +20% gives about +8 tokens core versus +285 marked.
Ordinary output mean held separate from G changes the invoice baseline, not
the optimum; recurring summary output C does change it.

### Existence and size of sign reversals

| SAME-mechanism price contrast | Old H | New H | Explanation |
| --- | ---: | ---: | --- |
| Main q=1, write +20% | 112,848 | 115,923 | Repeated cheap reads versus compulsory reset writes |
| Main q=.8, write +20% | 91,003 | 90,403 | Miss-written history dominates |
| Thin volatile: S=65,588,B=64,000,C=100,q=1,theta=1; write +20% | 79,368 | 78,893 | Cold terminal tail reverses the core sign |
| Same thin mechanism, theta=0; write +20% | 80,248 | 80,603 | Removing cold-tail timing restores the core direction |
| Thin stable-heavy q=.5; read x4 | 76,703 | 76,883 | Stable compactor read expense can dominate ordinary carry |

These controls show mechanisms, not typical workload frequencies. Their
economic effect is often small: q=.8 write +20% old-policy excess is only
.0061%; thin theta=1 write +20% .0052%; thin read x4 .0015%. A valid sign
reversal is not automatically an important production optimization.

### Material interventions must specify what stays fixed

| Intervention from main anchors | Full marked H | Block retuning savings from unchanged 112,848 |
| --- | ---: | ---: |
| Reclassify existing 20k as stable; S fixed, B 20k->40k | 105,158 | .350% |
| ADD 20k stable; S and B both +20k | 133,463 | 3.549% |
| ADD 20k volatile; only S +20k | 140,038 | 5.846% |
| Summary 4,382->20k, preserve non-summary material; S also grows | 152,666 | 9.824% |
| Scale whole retained-growth law x2; billed output unchanged | 130,803 | 1.496% |

For core control at main anchors, one added stable token raises H by about
1.031, whereas reclassifying one existing token stable lowers H by .352.
One added volatile token raises H by 1.383; one extra summary token preserving
other material raises it by 2.915. Growth-gap scale elasticity is .479, not
one. These derivative paths explain why an undifferentiated "more context"
parameter would hide opposite directions.

## 6. When is a higher-write long-lifetime tariff worthwhile?

Under the SAME timing/growth/reset mechanism, compare Sonnet 5.5 5m and 1h
price vectors while declaring q separately. Solving the full optimized invoice
break-even, not just shifting H, gives:

| Short-tariff q | Required long-tariff q after reoptimization |
| ---: | ---: |
| .50 | .714243 |
| .80 | .895035 |
| .90 | .953985 |
| .95 | .982977 |
| .98 | No feasible q<=1 in this lane |
| 1.00 | No feasible q<=1 in this lane |

At short q=.8, keeping its old threshold instead requires q=.896281; letting
the long tariff retune only slightly relaxes the needed gain. Fresh block
TOTAL invoice comparisons, separately reoptimizing each declared scenario:

- Long q=.8 minus short q=.8: **+.0278259834 +/- .0000634353 USD/action**.
- Long q=.95 minus short q=.8: **-.0169031452 +/- .0001051715 USD/action**,
  approximately **23.3% savings** against the short scenario.

Thus cache reliability can outweigh microscopic threshold tuning. These are
required/hypothetical q gains, NOT measured gains caused by a real 1h TTL.
At short q=.98 the failure-to-break-even margin is only about .107%; that tiny
conditional margin is not a robust recommendation to reject a provider tier.

## 7. Reproduction, validation and actionable next experiment

From the root `.venv`, with the pinned public pool prepared as described in the
renewal calibration note:

```powershell
uv sync --locked
uv run python experiments/price_sensitivity_derivation.py
uv run python experiments/price_sensitivity_crosscheck.py
$env:OPENBLAS_NUM_THREADS='1'
uv run python experiments/run_price_sensitivity.py --replicates 512 --calls 4000
./formal/verify.ps1
uv run python experiments/summarize_structural_theory.py
```

The main study executed in 14.69 seconds; generated figures/logs/raw arrays
remain under `.cache`. SymPy verified exact price sign factors, radial
identities, material paths, full marked-tail reversal and envelope/regret
identities. The independent category-level DP checked 45 basis cases with
maximum error 8.53e-14 tokens/action; nonatom finite contrasts matched price
gradients to 2.44e-10 relative error, and the smooth rank-one price Hessian to
3.32e-7. [Independent review](price-sensitivity-review.md) caught and closed
atom-gradient and same-mechanism-reference mistakes before the final study.
Lean verifies the new revealed-preference law; it does not certify the entire
continuous or empirical pipeline.

The high-value next measurement is a joint conditional trace of exact eligible
prefix length, hit/miss, request gaps, compulsory reconstruction and crossing
tail timing. Estimate q conditional on age/phase/prefix rather than from billed
cache-read fraction, then price the real TTL intervention using those changed
occupations. This can resolve whether the large hypothetical reliability gain
actually exists. More independent parameter noise or a generic Sobol ranking
with invented price priors would not answer that question.

The durable contribution is a map from relative prices to control phases,
resource-use ordering and retuning regret, plus measured conditional importance.
It is not a universal compact line or a claim that scalar thresholds exhaust
the general history-dependent policy space.
