# Stochastic threshold economics

Research specification, recorded 2026-10-06. This document supersedes the deterministic interpretation of `compaction-threshold-symbolic.md`; that earlier calculation remains an idealized baseline, not a fitted workload model. Prices below are per token, and all expectations are over a specified workload law, not model-generated prose. The executable v0.1 semantics are specified in [implementation-contract.md](../implementation-contract.md); distinctions from more general theory are explicit below.

## 1. Question and estimands

For a fixed stream of ordinary task requests, choose a compaction threshold `h` to minimize expected API invoice. Task success, task-per-token, subscription quotas, and endogenous behavior changes are outside this first study. Holding the stream fixed is an experimental intervention, not a claim that real agents behave identically after different summaries.

The primary finite-horizon estimand is

\[
J_N(h)=\mathbb E_{\theta}[C_N(h;\omega)],\qquad
C_N=\sum_{a\in\mathcal A_N(h)}(p_iI_a+p_wW_a+p_rR_a+p_oO_a).
\]

`A_N(h)` contains the `N` ordinary requests and every compactor/recovery request required before them. It excludes a pointless compaction after the final ordinary request. `I,W,R` are mutually exclusive input categories; `O` includes all billed output. Provider-reported total input may include cache reads and must be normalized first. Parameters `theta` describe the joint law, and `omega` is the primitive random stream. The optimization is over an explicit admissible integer-token grid `H`, not every imaginable adaptive policy.

A second estimand is the long-run expected dollars per **ordinary request**, not dollars per wall-clock second. A third reporting quantity is a fixed-token finite-difference slope,

\[
D_\delta J_N(h)=\frac{J_N(h+\delta)-J_N(h-\delta)}{2\delta},
\]

with `delta` reported. This is a sensitivity contrast, not automatically a classical derivative.

## 2. State, timing, and a correct ledger

At a normal-request boundary, state must contain at least retained tokens `x`, reusable cached-prefix tokens `w <= x`, time since the latest relevant cache write/read `a`, and any workload regime `z`. A multiple-prefix implementation additionally tracks each surviving prefix boundary and entry age.

1. Advance by the exogenous inter-request interval; compute eligible cache reuse.
2. If `x >= h` and an ordinary request remains, perform compaction. Charge its old-context input and generated summary once. Charge any actual recovery requests once.
3. Replace the mutable context with `S = summary + immediately reread documents`. The changed mutable prefix is cold; a genuinely unchanged earlier prefix may remain warm.
4. Add that request's newly retained input, then issue the ordinary request. Charge eligible old-prefix reads, newly written eligible tokens, uncached suffixes, and output exactly once.
5. Append output, tool observations, and other task additions. These increase the next context, but output appended **after** a request is not retroactively a cached input of that request.

For a single mutable prefix with ephemeral uncached suffix `I`, previously eligible cached length `w`, newly retained input `B`, and new cacheable suffix `x+B-w`, an ideal explicit-cache ledger is

\[
R=Mw,\quad W=x+B-Mw,\quad
\ell=p_iI+p_w(x+B-Mw)+p_rMw+p_oO,
\]

where `M` indicates a surviving matching entry. This simplified equation assumes the normal input reaches the minimum eligible cache length and that a miss rewrites it. Below that minimum, charge `x+B+I` as uncached input and set the available prefix to zero. After an eligible normal request, `w'=x+B` but `x'=x+B+O`. Boundary granularity, multiple TTLs, and routing require a provider adapter. It illustrates why charging both ordinary input and cache write for the same token is wrong.

The v0.1 compactor does not select its old varying context for a new cache write. It reads a surviving `w` and bills `x-w` plus compaction instructions as uncached input (or all `x` on a miss), generates the summary, and replaces the mutable prefix. Documents are inserted and billed on the subsequent normal request; v0.1 does not simulate additional retrieval-model calls. It models one branch-specific prefix and omits stable system content. Ordinary total growth is split into output and newly retained input using a configured fraction; this is a declared synthetic coupling, not a general tokenizer identity.

Use a transition kernel `P_h(s, d ell, d s')` that includes the complete boundary operation and the next ordinary request. The exact policy-evaluation recursion is

\[
V_{0,h}(s)=0,\quad
V_{n,h}(s)=\int[\ell+V_{n-1,h}(s')]P_h(s,d\ell,ds'),\quad
J_N(h)=\int V_{N,h}(s)\nu_0(ds).
\]

This covers dependence and a nonstationary first cycle. Fix and report `nu_0` (initial context, warm/cold status, initial age), rather than choosing a favorable initial state per threshold.

### Growth and overshoot

Starting at reset length `S < h`, let `G_k > 0` be ordinary-request context increments and

\[
X_0=S,\quad X_k=S+\sum_{i=1}^kG_i,\quad
T_h=\inf\{k\ge1:X_k\ge h\},\quad B_h=X_{T_h}-h.
\]

`B_h` is the overshoot. The compactor receives the crossed context `h+B_h`, not exactly `h`. Trigger convention is post-growth/before-next-request: last ordinary pre-call length is `X_{T_h-1}` in the ideal cumulative-growth model. New retained input added on the actual normal request can exceed a trigger checked immediately before that addition. A threshold is not a hard context-window guarantee. Unbounded growth distributions have positive probability of crossing any finite capacity; a future capacity-aware study must report overflow probability, use a declared bounded workload, or implement a separate safeguard. v0.1 has no context-capacity or long-context-price-tier model; `max_context` is diagnostic, not a feasibility certificate. Do not silently discard extreme samples.

For iid increments with mean `mu` and the integrability assumptions for Wald's identity,

\[
\mu\,\mathbb E[T_h]=h-\mathbb E[S]+\mathbb E[B_h].
\]

Thus `(h-E[S])/E[G]` misses overshoot even before cache and recovery randomness enter. For positive iid increments with finite second moment, Lorden's classical overshoot bound provides a useful control proportional to `E[G^2]/E[G]`; it is not an equality or a substitute for estimating the overshoot law [1]. This is one mechanism by which equal-mean, different-tail workloads change costs.

## 3. Cycle averages: use the correct ratio, with the correct assumptions

Let `Q_h` be the complete invoice over a cycle, including one compaction and appropriate first-cold-prefix accounting, and `T_h` its ordinary-request count. If reset states are freshly sampled from the same distribution independent of past cycles, and `(Q_j,T_j)` are iid with `0 < E[T] < infinity` and `E[abs(Q)] < infinity`, renewal reward theory gives

\[
r(h)=\frac{\mathbb E[Q_h]}{\mathbb E[T_h]}.
\]

**Do not use `E[Q_h/T_h]`.** For two equally likely cycle types `(T,Q)=(1,10),(9,18)`, the invoice rate is `14/5 = 2.8`, while averaging per-cycle rates gives `6`. Short cycles are overrepresented in the latter quantity. The ratio-of-expectations claim follows established renewal reward results, not an original theorem [2,3].

Conditional recovery is an important complication. If

\[
S_{j+1}\sim F_S(\cdot\mid X_{T_j},z_j,\text{recovery marks}),
\]

then the terminal crossing can influence the next cycle; compaction does **not** automatically regenerate iid state. Use the finite transition model directly. For a stationary ergodic reset-state chain with invariant distribution `pi_h`, an appropriate long-run ratio is

\[
r(h)=\frac{\int\mathbb E[Q_h\mid s]\pi_h(ds)}
{\int\mathbb E[T_h\mid s]\pi_h(ds)}.
\]

Existence, integrability, and convergence to `pi_h` must be checked or assumed explicitly. Burn-in reduces initialization effects in an estimator; it does not prove regeneration. The derivative also involves `pi_h` changing with `h`.

### Derivative of the expected rate

For `A(h)=E[Q_h]` and `B(h)=E[T_h]`, if these expectations are differentiable and `B>0`,

\[
r'(h)=\frac{A'(h)B(h)-A(h)B'(h)}{B(h)^2}.
\]

A stationary point equates marginal cost per marginal cycle extension to average cost: `A'/B' = A/B` when `B'` is nonzero. It does **not** generally reduce to replacing deterministic growth and recovery with their means.

If a dominated joint cycle density `f_h(q,t)` exists and differentiation under its integral is justified, then

\[
A'=\int q\,\partial_h f_h(q,t)\,dq\,dt,\qquad
B'=\int t\,\partial_h f_h(q,t)\,dq\,dt.
\]

Where support moves, boundary terms are required. A score-function expression `A'=E[Q * partial_h log f_h]` is valid only under those regularity conditions; state-dependent rewards add their direct derivative. Integer token laws can instead produce a staircase expected objective. Even a continuous growth law does not justify differentiating an individual threshold-crossing sample: stopping times jump as `h` changes. Treat analytic smooth special cases and common-random-number finite differences as distinct tools.

## 4. An exact stochastic benchmark with a closed-form derivative

This solvable benchmark isolates randomness and overshoot before the full cache simulation. It is **not** the production cache ledger in Section 2.

Assumptions: fixed reset length `s`; iid exponential increments of mean `g`; always-warm retained-context read cost `p_r X_j`; fixed ordinary baseline `b`; compactor processing charge `K(x)=k_0+k_1 x`; and incremental reset rewrite surcharge `(p_w-p_r)s` (the baseline already counted the first read). Every cycle receives an identical reset and fresh increments. No finite-horizon terminal effects or capacity limit are included.

Let `d=h-s>0`. Exponential renewal points form a Poisson process in cumulative token length, so

\[
T_h\ \overset d=\ 1+\mathrm{Poisson}(d/g),\quad
\mathbb E[T_h]=1+d/g,\quad
\mathbb E[X_{T_h}]=h+g.
\]

Integrating the intensity `1/g` of pre-crossing renewal points gives

\[
\mathbb E\!\left[\sum_{j=0}^{T_h-1}X_j\right]
=s+\frac{sd+d^2/2}{g}.
\]

Consequently,

\[
r(h)=b+
\frac{p_r\{gs+sd+d^2/2\}
+g\{k_0+k_1(s+d+g)+(p_w-p_r)s\}}{d+g}.
\]

Writing `A = k_0 + (k_1 + p_w - p_r)s`, the derivative and curvature are

\[
\boxed{r'(h)=\frac{p_r}{2}
-\frac{gA+p_rg^2/2}{(h-s+g)^2}},\qquad
r''(h)=\frac{2gA+p_rg^2}{(h-s+g)^3}.
\]

For `p_r>0` and `A>0`, the interior optimum is

\[
\boxed{h_*=s-g+\sqrt{g^2+2gA/p_r}}.
\]

The deterministic expression was `s + sqrt(2gA/p_r)`. These are different despite identical mean growth. If `A <= 0`, this benchmark has no positive-gap interior minimum (its derivative for `d>0` is positive); enforce physical minimum-gap constraints. For a fixed normal-call horizon, `N*r(h)` is a long-run approximation, not `J_N(h)` exactly. The analytical benchmark verifies quotient differentiation and first-passage accounting without claiming a universal distribution.

Independent symbolic check on 2026-10-06: the existing workspace-local `uv` Python environment with SymPy verified three exact identities: derivative of the displayed ratio, derivative of that derivative, and zero derivative at the displayed stationary point. The checks simplified the differences to zero, rather than comparing floating-point examples. The production package's `analytic.py` and its tests provide the durable runnable version; this algebra check alone does not validate the full finite simulator or its workload law.

## 5. Cache TTL and dependence

For a stylized refresh-on-use TTL `tau`, let `Delta_t` be the start-to-start interval and `M_t = 1{Delta_t <= tau}` combined with matching-prefix/routing survival. Streaming time counts within the interval. Claude documents fixed 5-minute/1-hour choices and refresh on reuse; OpenAI's behavior depends on model and retention configuration [4,5]. Do not equate a provider's guaranteed minimum retention with a deterministic actual expiry.

Even when a single-prefix old length is `X`, an effective price `q p_r+(1-q)p_w` is justified only if the hit event is independent of that length. In general,

\[
\mathbb E[\text{old-prefix cost}]
=p_w\mathbb E[X]-(p_w-p_r)\mathbb E[MX].
\]

`E[MX]` is not `P(M=1)E[X]` when large tool observations coincide with slow commands, long responses, or task pauses. A regression or empirical joint resampling should preserve this dependence. Compaction itself consumes time and changes prefix identity; its cache effect must be represented rather than inserted as a universal reset fee.

## 6. Synthetic reference laws, not an empirical workload fit

The first release has no measured traces. Named distributions are controlled reference families with reproducible parameters and uncertainty analyses, **not** estimates of actual coding-agent traffic.

| Variable | Reference family | Mechanism and limitation |
| --- | --- | --- |
| Growth `G` | Gamma with mean `mu`, coefficient of variation `cv`; shape `cv^-2`, scale `mu*cv^2` | Positive increments, tunable dispersion; not automatically heavy-tailed |
| Growth tail stress | Lognormal with `sigma^2=log(1+cv^2)`, log-location `log(mu)-sigma^2/2` | Same mean/CV but a different tail; all moments finite, large empirical tail variance possible |
| Bursty observations | Bernoulli mixture of small and large positive components | Distinguishes rare file/log loads; independent mixture is not temporal burst autocorrelation |
| Recovery fraction `U` | Beta with shape parameters `u*kappa`, `(1-u)*kappa` | Bounded fraction, tunable variation; never assert fitted shapes without observations |
| Restored context | `S=s0+U*crossed_context + D` with `D>=0` | Includes reread material and dependence on overshoot; may create non-iid cycles |
| Request interval `Delta` | Lognormal; alternatively short/long-pause mixture | Captures skew and TTL crossings; exponential is only a memoryless analytic control |
| Correlation control | Shared latent normal driving growth/gap quantiles | Controlled dependence study, not proof of real correlation; transformations need stated parameters |

The simple first-passage formula beginning at `S < h` requires that inequality. The v0.1 finite simulator deliberately does **not** guarantee it: summary plus reloaded documents may exceed the threshold, and each boundary performs at most one compaction before proceeding with its ordinary request. `recovery_above_threshold` records the event. No upper-tail clipping, repeated-until-small reset loop, or implicit failure exclusion is permitted. This makes the finite transition well-defined without altering the proposed recovery distribution. The alternative iid theoretical benchmark uses `S=s0+U*h` with support constrained below `h`, so reset laws depend on policy but not on the previous overshoot; it is not interchangeable with the v0.1 simulation.

v0.1 implements independent marginals, gamma/lognormal positive laws, and a burst-mixture stress law. Correlated growth-gap controls and empirical resampling are proposed experiments, not already-implemented claims. A descriptive fitting interface estimates gamma/lognormal MLE with location fixed at zero and reports likelihood, AIC, BIC, and KS distance; it does not provide a valid fitted-distribution KS p-value or establish that either family fits real traffic.

Growth and ordinary billed output are related but not identical: tools add context without model-output charges, and billed reasoning can be hidden from later visible context. Do not infer output charge from growth alone. A fixed ordinary output stream is acceptable for the present intervention; declare it.

### Calibration once traces exist

Collect session ID, event type, request timestamps, pre-call retained tokens, disjoint usage counts, visible/output token counts, append sizes by source, cache boundary/TTL settings, compaction input/output, summary size, reread size, and post-recovery retained size. Anonymized token counts suffice; repository content is not required.

1. Validate timestamps, unit consistency, billing conservation, and tokenizer version.
2. Split by complete session/repository/time block, not random individual requests.
3. Compare empirical/bootstrap, gamma, lognormal, and mixture predictive laws using held-out log scores, quantile calibration, tail exceedances, and autocorrelation.
4. Fit recovery conditional on crossed size, phase, and mechanism; inspect failures and censoring at capacity.
5. Validate conditional hit probability using elapsed time, eligible prefix size, and routing settings.
6. Test whether selected thresholds transfer on held-out sessions. A good marginal fit is insufficient if it destroys cost-relevant dependence.

Until then, deliver scenario-specific optimal regions and sensitivity, not a universal `60k` answer.

## References and relation to prior work

1. Lorden (1970), *On excess over the boundary*, Annals of Mathematical Statistics 41(2), 520-527. [Author archive](https://authors.library.caltech.edu/records/8eyxa-q6789), [DOI](https://doi.org/10.1214/aoms/1177697092). Peer-reviewed primary basis for overshoot control; no new overshoot theorem is claimed.
2. Vlasiou, *Renewal Processes with Costs and Rewards*, [author manuscript](https://arxiv.org/abs/1404.5601), [published reference text](https://ris.utwente.nl/ws/portalfiles/portal/249488824/10.1002_9780470400531.eorms0722.pdf). Standard ratio-of-expectations result and integrability conditions.
3. Sigman, [Renewal Theory lecture notes](https://www.columbia.edu/~ks20/4106-18-Fall/Notes-Renewal-Theory.pdf). Supporting primary teaching exposition, not an independent research contribution.
4. Anthropic, [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Production source for disjoint token categories, prefix matching, and TTL semantics. Consulted 2026-10-06; prices and supported models remain configurable.
5. OpenAI, [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Production source for cache lifetime, prefix invalidation, and provider-specific usage normalization. Consulted 2026-10-06.
6. Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Production motivation for combining working context with structured external state; it does not supply a workload distribution.
7. Lindenbauer et al. (2025), [The Complexity Trap](https://arxiv.org/abs/2508.21433), NeurIPS 2025 workshop paper. Shows a simple observation-masking alternative deserves comparison. Its task-quality and aggregate cost findings do not establish the optimal four-rate threshold here.
8. Tirmazi et al. (2026), [Context Compaction Theory](https://arxiv.org/abs/2608.01326). Recent preprint relating preservation budgets to communication complexity; addresses retained information, not this invoice stopping problem.
9. Zhang et al. (2026), [AutoCompact](https://arxiv.org/abs/2610.02163). Recent preprint on learning when/what to compact jointly with coding behavior. Relevant future policy direction, not evidence for the present fixed-stream stochastic parameters.

The proposed contribution is an auditable stopping-time invoice model and uncertainty-aware threshold selection protocol that accounts for overshoot, cold rebuilds, conditional recovery, and finite termination. It is an investigation to perform, not a claim of empirical superiority or mathematical novelty.
