# Selecting a mathematical model for mandatory restoration

The timing replay is maintained at `experiments/replay_first_use_timing.py`:
run `uv run python experiments/replay_first_use_timing.py` from the project root.
Aggregate output is written under `.cache/experiments/first-use-reload`.

Recorded 2026-10-06. This is the decision-alternatives track of
[mandatory-reload-research-plan.md](mandatory-reload-research-plan.md).
It extends, rather than overwrites, [stochastic-model.md](stochastic-model.md)
and [engineering-context-evidence.md](engineering-context-evidence.md).
The complementary exact derivations are in
[mandatory-reload-theory.md](mandatory-reload-theory.md), especially Sections
3-5 (fact contracts, occupancy and threshold-dependent stopping) and Section
7 (finite-horizon evaluation). This note selects tools and a discriminating
experiment rather than reproducing those derivations.

## 1. Decision first

**Next method: a finite-horizon, versioned-file first-use reward model, with a
separate matching-prefix cache state.** Use exact enumeration on a small
scripted workload before fitting distributions. Retain the existing iid
aggregate recovery experiment as a named control, not the mechanism model.

The useful question is not which positive marginal family fits reset size. It
is which information disappears, which subsequent fixed ordinary action
requires that information, when its restoration occurs, and how long the new
payload is subsequently billed. A median aggregate cannot answer these.

The objective stays

`J_N(h) = E[sum_a (p_i I_a + p_w W_a + p_r R_a + p_o O_a)]`,

where `N` counts the fixed ordinary requests; `a` includes every necessary
compactor/recovery request. Ordinary actions and ordinary output are fixed by
the intervention. Compulsory recovery output/rounds may depend on `h` and are
additional invoiced events. Do not replace this objective with solve rate,
tokens per task, latency, or wall-clock throughput.

The recommendation changes the *state representation and event law*, not
the prices or objective. No production implementation was changed here.

## 2. Six useful tools, ranked by immediate decision value

| Tool | What it exposes | Assumptions that matter | Small next computation | Recommendation |
| --- | --- | --- | --- | --- |
| Working-set / renewal-reward / Markov-renewal analysis | Locality, repeated residency losses, cost per ordinary action rather than per cycle | Logical residency is not provider caching; iid renewal cycles require actual regeneration; otherwise carry the reset-state chain | Compare first-use timing and repeat-file bursts under a fixed demand stream | Use working-set state now; renewal only as a justified reduction |
| Finite Markov reward process; optionally MDP / optimal stopping | Dependence on retained versions, cache age, phase, remaining horizon; whether a scalar threshold can be sufficient | State must be sufficient for conditional future law; numerical state aggregation needs error checks; online policy cannot use future scripted demands | Exact finite-horizon policy evaluation for 4 files and 8-12 actions; optionally compare threshold to a phase-aware stop/continue decision | Primary computational tool; no reinforcement-learning machinery needed |
| Survival / discrete hazard / competing risks | Delayed mandatory first use, never reused files, phase-specific restoration | Event is *required current-version use*, not any observed reread; terminal/next-compaction censoring is policy-dependent | Tabulate first-use probabilities at action indices, stratified by declared phase | Parameterize event timing after mechanism selection; do not assume exponential arrivals |
| Setup/holding-cost and lot-sizing analogue | Compaction setup versus the area under retained-context length; why first-use delay has invoice value | Exact classical lot-sizing theorems do not transfer when context grows rather than depletes, reset depends on prior state, or prefix cost is nonlinear | Compute exact segment invoice on a fixed trace; shortest-path segmentation if reset is history-independent | Excellent intuition and an offline benchmark, not an imported universal square-root rule |
| Common-random-number sensitivity, IPA/score estimators, stochastic approximation | How to optimize a noisy integer-threshold objective without falsely differentiating crossing times | Threshold sample paths jump; support-changing likelihoods need boundary terms; a workload score is not a threshold gradient | Paired threshold contrasts on a small grid with the same primitive stream; exact derivatives only in a regular smooth special case | Paired contrasts now; gradients only after a valid estimator is established |
| Partial identification / distributionally robust optimization | Which threshold recommendations survive unidentified payload splits, hazards, cache survival, and dependence | Median alone does not bound expectation; finite ambiguity sets need explicit support/mechanism assumptions; generic Wasserstein guarantees need sample and loss regularity | Enumerate mechanism-consistent scenarios; report robust dominance or minimax expected-invoice regret | Do this before fitting Gamma/lognormal to invented recovery data |

### 2.1 Working sets explain why regeneration may fail

Denning's working-set model identifies recently referenced pages as a
behavioral memory-demand object [R1]. For this project, the analogous object
is required **versioned file extents**: file identity, current revision, and
the ranges needed by the next edit/read. The analogy is not an assertion that
LLM context is OS page memory or that a whole-file LRU rule is optimal.

Let `A_t` denote demanded extents and `R_t` the logically usable extents in
context. A mandatory restoration condition is a declared harness contract
requiring `A_t` at a particular version, together with `A_t` not covered by
`R_t`. Compaction changes `R_t`; it need not change on-disk availability.
An external mutation can invalidate usability even when old text remains.

The same project, recently active file, unfinished edit, or stable cache entry
can survive successive cycles. Therefore a threshold crossing is not by
itself a regeneration point. Iid renewal-reward is valid only under the
reset-independence assumptions already stated in stochastic-model.md.
Otherwise use a finite-horizon model, or a stationary Markov-renewal ratio
with invariant reset-state distribution and stated ergodicity assumptions.
Changing the marginal Gamma to lognormal does not repair this issue.

### 2.2 Finite state is a tool for structure, not a demand for a huge model

An illustrative sufficient state is

`s_t = (x_t, prefix_identity_t, cache_age_t, R_t, current_versions_t, z_t, n_t)`.

Here `x_t` is retained token length, `z_t` is a declared workload phase,
and `n_t` is remaining ordinary work. For a scripted replay, action index
itself determines the future workload, so no fitted latent phase is needed.
For a stochastic model, this tuple is Markov only if its conditional transition
law depends on no omitted history. A 4-file bitset gives only 16 residency
patterns before versions/extent information; start with exact states, not an
elaborate neural state encoder.

For a fixed threshold, ordinary-boundary policy evaluation uses the existing
`V_n(s) = E[ell_h(s, xi) + V_(n-1)(F_h(s, xi))]` recursion. Exact enumeration
provides a checkable invoice baseline and handles terminal effects without
forcing a long-run ratio. Bellman/Puterman supply the standard dynamic
programming foundations [R2,R3], not a new result claimed by this note.

Optional extension: permit `a` in `{continue, compact}` while holding ordinary
actions fixed, and compare the scalar-threshold policy with the finite-horizon
MDP optimum. This can test *whether a threshold is a good restriction*.
Do not silently replace the original threshold-selection problem with this
larger policy class. For online comparisons, reveal no future demands to
the controller; an offline clairvoyant optimum is only a lower bound.
Do not assume a monotone threshold theorem: two states with the same `x` can
have different high-value live files or cache survival, and thus different
compact-versus-continue costs.

### 2.3 Hazard models encode restoration timing directly

For file/version extent `i`, define `U_i` as its first required use after
compaction, and set `U_i = infinity` if never used before the declared horizon.
The discrete hazard is `lambda_i(k) = P(U_i=k | U_i>=k, z, covariates)`.
This is the directly relevant timing law. Files that do not reappear are
not missing observations to be discarded; they have zero restoration cost
on that horizon. Joint phase dependence matters when several files are
needed together.

Kaplan-Meier provides a classical nonparametric starting point for censored
event times [R4]; Cox is a possible covariate model [R5], not a requirement
or a reason to impose proportional hazards. A small deterministic replay
does not need either estimator: its event law is known exactly. Later, use
per-action empirical hazards or piecewise hazards by task phase before a
high-dimensional survival model.

Competing events include next compaction, external version replacement, and
session termination. Next compaction is *policy-generated*, and session
termination may be *behavior-generated*. Treating them as independent
censoring without justification can bias first-use incidence. Fixed scripted
`N` avoids endogenous session length; stochastic analysis should model the
competing event explicitly or stratify by a predetermined horizon. Existing
theory-track derivations belong in mandatory-reload-theory.md rather than
being duplicated here.

### 2.4 Setup/holding analysis supplies a mechanistic economic analogy

Compaction incurs setup-like charges: old-context processing, summary output,
and compulsory reconstruction rounds. Keeping tokens incurs holding-like
charges on later calls: input/cache-read exposure. Wagner-Whitin analyzes
known-demand, time-varying setup and inventory holding costs [R6].

Our model is not that inventory model: context usually accumulates rather
than being depleted by demand; stale content may stay billed; cache writes
and TTL affect marginal prices. Its zero-inventory ordering property and
linear-time algorithms therefore do not automatically apply. The safe
transfer is to make the retained-token **area** and reset setup explicit.

With a fixed trace and history-independent reset, precompute the invoice
`c(i,j)` for one segment and use a DAG shortest path / segmentation dynamic
program to find an offline compaction schedule. If reset depends on live
files, carry that state or abandon the segment-only shortcut. This comparison
can reveal whether phase-aware boundaries materially improve on thresholds;
it must not be reported as an attainable online policy.

### 2.5 Gradient tools must respect threshold discontinuities

The current integer-token objective can have plateaus and jumps. A sampled
path's compaction count changes discontinuously with `h`, so differentiating
its ordinary arithmetic while ignoring event changes is not a justified
infinitesimal perturbation analysis (IPA) estimator. Glasserman gives
structural conditions for IPA validity [R7]. Glynn develops likelihood-ratio
gradient estimators [R8], but they require an actual parameterized law and
regularity, not merely differentiable notation.

In particular, if primitive workload density `f_theta(xi)` is independent of
the chosen threshold, its score can estimate sensitivity to `theta` (subject
to integrability); it supplies no `h`-score for threshold-triggered stopping.
The crossing law's support can change with `h`. A finite-state transition
matrix can be differentiated where differentiable; integer-grid policy
changes still require contrasts, not a fictitious continuous derivative.

Recommended now: align randomness by ordinary action index; evaluate paired
`J(h+delta)-J(h-delta)` and report `delta`. With a small grid, evaluate all
candidates and confirm selected near-optimal candidates independently. Only
consider stochastic approximation when repeated exact/paired evaluation is
actually too expensive, and supply a valid gradient/subgradient or specified
finite-difference update. No such complexity is warranted for the tiny probe.

### 2.6 Partial identification comes before ambitious DRO

Let `Theta` contain mechanisms and parameters consistent with explicit
assumptions: stable-prefix split, mandatory file set, first-use timing,
versions, and extra recovery rounds. Compute `J(h;theta)` for each scenario,
not a single fitted answer from an unidentified median residual. The
expected-invoice regret is

`Regret(h;theta) = J(h;theta) - min_g J(g;theta)`.

Select `min_h max_theta Regret(h;theta)` only if that robust decision
criterion is requested/declared. The inner performance metric remains the
same expected four-price invoice. More simply, report whether one threshold
dominates another over all enumerated scenarios. Failure of dominance tells
us which unknown mechanism to measure next.

Esfahani-Kuhn gives data-driven Wasserstein DRO constructions and tractable
reformulations under stated loss/data assumptions [R9]. A discontinuous
multi-cycle stopping ledger is not automatically one of those convex losses;
iid empirical-sample concentration is not justified for correlated session
events. Do not advertise its finite-sample guarantee without checking those
conditions. At our current evidence level, a small mechanism-consistent
scenario set is more defensible and tractable than a nominal Wasserstein ball
around synthetic Gamma samples. With many complete independent sessions,
block-based uncertainty and a suitably bounded/Lipschitz surrogate could
make that frontier method worth revisiting.

## 3. What the current aggregate evidence cannot identify

The engineering note correctly treats 65,588 and 4,382 as marginal-median
anchors, and 61,206 as a constructed aggregate residual. Four further
distinctions matter for the next model:

1. **No expected reload from a median.** A nonnegative distribution with
   mass 0.51 at `m` and 0.49 at `L>m` has median `m` but expectation
   `0.51m+0.49L`, unbounded as `L` grows. Thus median-only evidence supplies
   neither an expected restoration size nor an invoice upper bound. A
   declared finite capacity/support or measured moments changes this.
2. **Versions and extents, not just paths.** Two reads of the same path
   can be the same version, disjoint ranges, or different revisions.
   Logical deduplication should identify required coverage and freshness.
   Billing counts *every actual prompt occurrence*: if the same bytes occur
   twice in the prompt, both are billed. Never deduplicate real input tokens
   merely because their semantic content is repeated.
3. **Tool result versus stable prompt.** Removing an old tool result is a
   logical residency change. A stable project-guidance/tool-schema prefix
   may still be injected and cached. Conversely a file can be logically
   known but reside after a modified prefix, so its provider cache is cold.
   A stable semantic prefix is not enough: it needs an actual matching
   eligible previously written boundary [P1].
4. **Observed reread versus compulsory read.** A reread can be demanded by
   read-before-edit, be newly necessary after a version update, repeat an
   already scheduled ordinary read, or be discretionary rediscovery. Only
   the incremental compulsory event enters restoration. The relevant
   harness contract must declare which surviving representations satisfy
   it; a summary should not be assumed to satisfy a verbatim-current-file
   requirement.
5. **Endogenous stopping and selection.** Real agents can stop earlier,
   take different actions, or prolong work after compaction. Conditioning on
   observed long sessions or surviving post-compaction windows selects on
   this behavior. Keep `N` and ordinary action sequence fixed in the present
   intervention, log every extra compulsory round, and do not infer an
   exogenous hazard from post-compaction sessions without this distinction.

## 4. Industry and frontier signals: implications, not borrowed parameters

Production context engineering combines summaries with recent files and
external persistent information [P2]. That is evidence for several state
components and locality, not evidence that all historical files must always
be reread. Provider prefix caching distinguishes matching cached prefixes
from fresh suffixes [P1]. Therefore the minimum useful architecture separates
file usability/residency from eligible KV/prompt-cache state.

Marconi (MLSys 2025, peer-reviewed) bases hybrid-model prefix-cache admission
and eviction on reuse opportunities and compute savings [R10]. Its importance
here is the interaction between reuse probability, resource footprint, and
cache representation. It does **not** establish hosted API billing savings
or our workload hazard. That distinction keeps a systems frontier from being
misapplied as a four-price cost coefficient.

The Complexity Trap (NeurIPS 2025 workshop, not main-conference evidence)
compares observation masking with LLM summarization in a coding benchmark
[R11]. It motivates a simple masking control and warns that compression
policy complexity is not automatically beneficial. Its free-running solve
rates/costs do not estimate this fixed-action causal intervention. Start
with the simple stateful ledger; add adaptive policies only if the small
test shows cost-relevant dependence that a scalar threshold misses.

## 5. A small discriminating experiment, already computationally probed

### 5.1 Fixed controlled workload

One known compaction followed by **8 ordinary calls** is sufficient to
discriminate immediate-all-files restoration from mandatory-first-use
restoration. This is a constructed accounting probe, not an empirical claim
about any production harness. It deliberately does not optimize `h` yet.

- Stable prefix `B=8,000`, generated summary `C=1,000` tokens. Landing
  retained base is 9,000. Cache eligibility minimum is 1,024; TTL is infinite.
- Previously available files A/B/C/D have payloads 2,000/3,000/5,000/7,000
  tokens. Each restore adds a 64-token wrapper. None is in the generated
  summary as usable verbatim current-version content.
- Early stream requires A at call 1, B at 2, C at 3, A at 7. Late stream
  requires A at 1, B at 6, A at 7, C at 8. D is never required. A is externally
  changed from version 1 to version 2 immediately before call 7 in both.
  Each stream has fixed actions; changing demand timing is a *second controlled
  workload*, not changing task behavior under a compaction policy.
- Each ordinary call adds 200 retained-input tokens before its request,
  bills 128 ephemeral uncached-input tokens, and generates/appends 100 output
  tokens afterward. Tool restores are scripted, with no additional model
  invocation output. A real harness that requires recovery model calls must
  invoice those separately; their absence is an explicit probe assumption.
- Old compactor input is fixed at 80,000, including 75,000 cache-read tokens
  and 5,000 uncached tokens; summary output is the 1,000 above. After that
  request, either the stable 8,000 prefix survives or no prefix survives.
  The two stable-prefix branches need not imply the old compactor was cold.
- Rates in USD per million tokens are `p_i=3, p_w=3.75, p_r=0.30, p_o=15`.
  These are the project's illustrative scenario rates, not newly quoted
  current-market prices. All four categories are exercised.

Immediate mode restores all four version-1 files at landing, then A version
2 on call 7. First-use mode restores only demanded current versions. Old
versions remain physically retained/billed; usability and billing are separate.
New file payloads are cache-written on the next ordinary request exactly once,
then billed as prefix reads on subsequent calls. There is no second
compaction in this diagnostic window.

### 5.2 Actual local probe results

Executed on 2026-10-06 with `uv run python .temp/model_selection_probe.py`
in the existing project environment. The durable Python block in Section 6
was separately extracted to `.temp/model_selection_embedded.py` and run with
`uv run`; all eight landing sizes, token areas and invoices matched.
All values below are deterministic
constructed-model arithmetic, not Monte Carlo, observed tokenization, or
provider measurements.

| Mechanism | Stream | Landing tokens | Restored payload tokens | Ordinary cacheable token-calls | USD, stable prefix survives | USD, stable prefix cold |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Immediate all-files | Early | 26,256 | 19,000 | 224,176 | 0.2128638 | 0.2404638 |
| Immediate all-files | Late | 26,256 | 19,000 | 224,176 | 0.2128638 | 0.2404638 |
| Mandatory first-use | Early | 9,000 | 12,000 | 154,472 | 0.1675818 | 0.1951818 |
| Mandatory first-use | Late | 9,000 | 12,000 | 116,896 | 0.1563090 | 0.1839090 |

Interpretation:

- The immediate control is invariant to B/C demand timing. First-use has
  identical total restored payload but 37,576 fewer token-calls when B/C use
  is delayed, reducing invoice by `0.30*37,576/1e6 = 0.0112728` USD.
  Equal payload totals do not imply equal invoices.
- The unused D is never restored under first-use. Current A version 2 adds
  another 2,000 payload tokens; path-only deduplication would miss it.
- Losing the stable prefix adds exactly `(3.75-0.30)*8,000/1e6 = 0.0276` USD
  in every row. This is a different mechanism from file rereading.
- The complete early-first-use warm ledger is
  `(I,W,R,O)=(6,024,15,556,213,916,1,800)`; no input token is charged both as
  uncached input and a cache write. The early-immediate warm ledger is
  `(6,024,22,620,276,556,1,800)`.

### 5.3 Turn the probe into model selection, not a large collection campaign

Replay these two 8-action sequences through the target harness with one
forced compaction and an explicit current-file requirement. Use synthetic
files; save only token/category counts and synthetic identities. Three
branches are enough: early cold reset, late cold reset, early surviving
stable-prefix reset. Record pre-first-use landing content, each restoration
event/current version, each actual request's disjoint usage categories, and
whether the harness adds a model/tool round. No private session corpus or
task-success benchmark is needed.

| Diagnostic outcome | Model selected / correction |
| --- | --- |
| All four file payloads appear before any demand; early/late landing and ledgers match | Immediate recovery kernel is justified for this configured mechanism; use aggregate renewal control only if cycle independence also holds |
| Only demanded versions appear; late stream lowers retained-token area | Delayed first-use working-set reward model; hazard/event timing is essential |
| Restoring A version 2 is required despite version 1 still in context | Carry freshness/version state; a path bitset alone is insufficient |
| Rereads occur although current required extents are resident | Inspect read-before-edit invalidation or extra-round contract; add that state/event, not an arbitrary reset-size tail |
| Stable prefix is billed warm while file content is missing | Separate provider prefix-cache state from logical file residency |
| A summary satisfies the configured file-use contract and no restore occurs | Mandatory set must be revised for that contract; do not force an invented reread |

The direct event pattern selects a *mechanism class*, not a population
distribution. A deterministic replay proves neither universal behavior nor
future empirical hazard calibration. It can nevertheless reject the wrong
immediate-reset structure before a large implementation is built. Next,
evaluate a small threshold grid on one fixed 12-action, two-compaction trace
to see whether residency survives across cycles; stop there unless the result
requires a Markov phase/version extension. Do not start with a broad roadmap.

## 6. Durable reproduction of the arithmetic

The disposable `.temp/model_selection_probe.py` contains a typed runnable
probe. The following compact reconstruction is sufficient if that temporary
file has been removed. Save under the root `.temp`, then run with `uv run`.

```python
"""Reconstruct the deterministic eight-call first-use invoice probe."""

def replay(immediate: bool, late: bool, warm: bool) -> tuple[int, int, float]:
    """Return landing size, input-token area, and four-price invoice."""
    sizes = {"A": 2000, "B": 3000, "C": 5000, "D": 7000}
    demand = {1: "A", 6: "B", 7: "A", 8: "C"} if late else {
        1: "A", 2: "B", 3: "C", 7: "A"
    }
    seen = {(name, 1) for name in sizes} if immediate else set()
    x = 9000 + (sum(sizes.values()) + 4 * 64 if immediate else 0)
    landing = x
    w = 8000 if warm else 0
    i, write, read, out, area = 5000, 0, 75000, 1000, 0
    for k in range(1, 9):
        if k in demand:
            name = demand[k]
            version = 2 if name == "A" and k >= 7 else 1
            if (name, version) not in seen:
                seen.add((name, version))
                x += sizes[name] + 64
        input_length = x + 200
        i += 128
        write += input_length - w
        read += w
        out += 100
        area += input_length
        w, x = input_length, input_length + 100
    dollars = (3 * i + 3.75 * write + .30 * read + 15 * out) / 1e6
    return landing, area, dollars

for warm in (True, False):
    for late in (False, True):
        for immediate in (True, False):
            print(immediate, late, warm, replay(immediate, late, warm))
```

## References

All links were consulted on 2026-10-06. Primary sources are preferred. Paper
results are not measurements of this project's workload.

- [R1] Denning (1968), *The working set model for program behavior*,
  Communications of the ACM 11(5), 323-333, peer-reviewed.
  [DOI](https://doi.org/10.1145/363095.363141),
  [author PDF](https://denninginstitute.com/pjd/PUBS/WSModel_1968.pdf).
- [R2] Bellman (1957), *A Markovian Decision Process*, Journal of Mathematics
  and Mechanics 6, 679-684, peer-reviewed.
  [journal record](https://iumj.org/article/1116/).
- [R3] Puterman (1994), *Markov Decision Processes*, Chapter 4, authoritative
  mathematical monograph. [Finite-horizon chapter](https://doi.org/10.1002/9780470316887.ch4).
- [R4] Kaplan and Meier (1958), *Nonparametric Estimation from Incomplete
  Observations*, JASA 53(282), 457-481, peer-reviewed.
  [DOI](https://doi.org/10.1080/01621459.1958.10501452).
- [R5] Cox (1972), *Regression Models and Life-Tables*, JRSS B 34(2), 187-202,
  peer-reviewed. [DOI](https://doi.org/10.1111/j.2517-6161.1972.tb00899.x).
- [R6] Wagner and Whitin (1958), *Dynamic Version of the Economic Lot Size
  Model*, Management Science 5(1), 89-96, peer-reviewed.
  [DOI](https://doi.org/10.1287/mnsc.5.1.89).
- [R7] Glasserman (1991), *Structural Conditions for Perturbation Analysis
  Derivative Estimation: Finite-Time Performance Indices*, Operations Research
  39(5), 724-738, peer-reviewed.
  [DOI](https://doi.org/10.1287/opre.39.5.724).
- [R8] Glynn (1990), *Likelihood Ratio Gradient Estimation for Stochastic
  Systems*, Communications of the ACM 33(10), 75-84, peer-reviewed.
  [author archive](https://web.stanford.edu/~glynn/papers/1990/G90a.html),
  [DOI](https://doi.org/10.1145/84537.84552).
- [R9] Mohajerin Esfahani and Kuhn (2018), *Data-driven distributionally robust
  optimization using the Wasserstein metric: performance guarantees and
  tractable reformulations*, Mathematical Programming 171, 115-166,
  peer-reviewed. [DOI](https://doi.org/10.1007/s10107-017-1172-1),
  [author manuscript](https://arxiv.org/abs/1505.05116).
- [R10] Pan et al. (2025), *Marconi: Prefix Caching for the Era of Hybrid LLMs*,
  Proceedings of MLSys 7, peer-reviewed conference.
  [proceedings](https://proceedings.mlsys.org/paper_files/paper/2025/hash/7c180af017258d239bac6248d1eb26ac-Abstract-Conference.html).
- [R11] Lindenbauer et al. (2025), *The Complexity Trap: Simple Observation
  Masking Is as Efficient as LLM Summarization for Agent Context Management*,
  NeurIPS 2025 Deep Learning for Code in the Agentic Era workshop; workshop
  evidence, not main-conference acceptance.
  [paper](https://arxiv.org/abs/2508.21433),
  [workshop PDF](https://openreview.net/pdf/741655130e873bac88076fafdbc4e5114e87a6a3.pdf).
- [P1] Anthropic, *Prompt caching*, official production documentation:
  [matching prefixes, boundaries, usage categories](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).
- [P2] Anthropic, *Effective context engineering for AI agents*, first-party
  production discussion, not a peer-reviewed workload dataset:
  [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
