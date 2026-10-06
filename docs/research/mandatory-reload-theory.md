# Mandatory restoration as a versioned working-set process

Recorded 2026-10-06. Scope: a tractable mathematical extension of the fixed-N,
four-rate invoice objective, not a claim that all forgotten observations must
be reread. Production package behavior is unchanged by this research note.

## 1. Decision-relevant result

The useful next state variable is **which current-version facts are available**,
not another scalar distribution for an undifferentiated reset payload.
Compaction may erase tool observations without erasing the files on disk, and
different contracts require different facts before an ordinary action.

For a file of d tokens, initially unavailable after reset, used independently
with probability a per ordinary action, let K be its first required-use action,
T the cycle's ordinary-action count, and u = P(K <= T). In an ideal warm cache
ledger, with one write at first use and no subsequent version changes,

\[
\boxed{E[Q_{\rm file}]
  = F u+p_r d\{E[T]-u/a\}},\qquad
F=p_w d+\kappa d+f.
\]

Here kappa is the *marginal* terminal compactor input price for those tokens;
f is a declared isolated restoration overhead, including actual restoration
model output and extra requests if present. It is not a fee for an unbilled
disk read. If recovery requests themselves process existing context, their
whole invoices must be added explicitly, rather than assumed to be fixed f.

Two important distinctions:

1. `u=1-E[(1-a)^T]` requires T independent of the access process. It is generally
   false under a token threshold, because the first compulsory load grows the
   context and can change T.
2. The carry identity `E[(T-K)_+]=E[T]-u/a` remains exact for a predictable cycle
   stopping rule and constant conditional access hazard, even when T depends on
   previous loads. Its proof appears below. Thus the price mechanism survives,
   but u and E[T] must come from the joint model, not an independence shortcut.

For an externally fixed m-action cycle,

\[
u_m=1-(1-a)^m,\qquad
E[Q_{\rm lazy}]=F u_m+p_rd(m-u_m/a),
\]

whereas eager restoration costs `F + p_r d(m-1)`. Lazy restoration weakly
dominates for the same external cycle, equal per-file overhead, unchanged
versions and homogeneous warm caching. This is **not** a universal optimality
claim for token-triggered compaction or batched recovery requests.

These equations account for initial cache writes, repeated later carries,
terminal compactor processing and restoration output/round costs. Modeling
only `d*P(at least one use)` loses the price-relevant residency area.

## 2. Relation to established theory and production mechanisms

| External reality | Mathematical connection | Transfer limit |
| --- | --- | --- |
| Denning's working set is the set of recently referenced pages | Distinct files/ranges required over a cycle, locality and weighted occupancy | Our forward cycle demand set is not literally Denning's backward sliding-window working set; semantic/version contracts differ from hardware residency |
| Opderbeck and Chu model inter-reference behavior by renewal processes | Replace constant hazards with inter-reference distributions when locality data justify it | A fresh compaction is not a renewal of each file's underlying demand process; residual access ages matter |
| Anthropic describes up-front guidance plus just-in-time retrieval through file paths and tool primitives | Separate immediately required reset material from first-use compulsory loads | Described retrieval practice does not prove every file must be reread, nor provide use probabilities |
| Existing package models fixed/cold aggregate reset and explicit cache state | Keep aggregate reset as a compatibility control; introduce fact residency separately from prefix warmth | The 65,588 full prompt anchor does not identify a file working set or a stable-prefix share |

Primary references: [Denning, CACM 1968](https://doi.org/10.1145/363095.363141),
[Opderbeck and Chu, SIAM Journal on Computing 1975](https://doi.org/10.1137/0204031),
[Anthropic, context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
The first two are peer-reviewed classical foundations. The third is production
evidence, not a workload law. The derivations below are applications of standard
occupancy, compensator, renewal-reward and Markov-reward tools; no novel theorem
is claimed merely for this formulation.

## 3. State and contracts: semantic availability is not prefix warmth

Represent a required fact by an immutable identity

\[
e=(\mathrm{file\ id},\mathrm{version},\mathrm{range/fact},\mathrm{contract}).
\]

The contract specifies whether a summary, a verbatim snippet, a current read, or
external harness metadata satisfies a requirement. A pathname alone may locate
a file but need not satisfy a read-before-edit requirement. Conversely, if a
tool validates read-before-edit through its own persistent bookkeeping, clearing
the model's observation does not necessarily erase that permission. This is a
mechanism parameter, not a mathematical certainty.

Before ordinary action n, let `A_n` be its required facts and `R_n` be the
currently valid resident facts. The compulsory deficit is

\[
\Delta_n=A_n\setminus R_n.
\]

Restoration inserts facts satisfying Delta_n before the action can proceed.
Disk/storage copies are separate from R_n unless the action contract explicitly
allows them to substitute for model-visible facts. An edit to file version v+1
invalidates facts about v when the contract demands current contents. Whether
an applied patch itself supplies valid current-version facts is also explicit.
Do not reread mechanically when a contract-preserving resident update suffices.

At reset, a declared preservation map supplies `R^+ = preserve(R, summary,
retained observations, external certificates)`. Eager restoration additionally
loads an immediate compulsory set E. Lazy restoration loads only Delta_n as it
becomes required. Files never required before the next reset need not be loaded.

The numerical cache state is different:

\[
s=(x,\mathcal P,\mathcal A,R,v,z),
\]

where x is retained token length, P is the set of eligible matching prefix
boundaries, A their ages, v file versions and z task phase. A fact can be
available in a newly constructed, cold prompt; a stable warm tool-schema prefix
can coexist with missing file contents. Identical text appended at a different
location does not guarantee an eligible identical prefix.

```text
Current-version file requirement
            |
     resident valid fact? ---- yes --> ordinary action
            | no
     mandatory restoration --> insert fact --> ordinary action
            |                        |
       recovery-call invoice    cache write/read/input invoice
                                     |
                          repeated later-context carries
```

The restored file payload belongs to retained input, not generated model
output. A model-generated read command or recovery explanation is output;
the returned tool file contents are later input. Count neither token class twice.

## 4. Exact fixed-cycle working-set expectations

### 4.1 Bernoulli reference model

Assume m >= 1 ordinary actions between externally fixed resets, file i is
unavailable initially, d_i >= 0 is its retained payload, and its requirement
indicator is iid Bernoulli(a_i) across ordinary actions, 0 < a_i <= 1. Files
need not be independent *of one another* to obtain these individual expectations.
There are no edits, intervening evictions, repeated failed reads or payload
changes in this benchmark. A required file is restored before its first ordinary
action and retained through the cycle.

Let `K_i=min{n>=1: file i required at n}`, `q_i=1-a_i`, and
`Z_{i,n}=1{K_i<=n}`. Then

\[
P(K_i\le m)=u_i(m)=1-q_i^m,
\]

\[
E[D_m]=\sum_i d_i u_i(m),\qquad
E[\hbox{distinct files restored}]=\sum_i u_i(m).
\]

Linearity, not cross-file independence, proves these statements. Correlations
still matter for size variance, bursts and threshold-crossing times. For example,
`Var(D_m)=sum_i d_i^2 Var(Z_i)+2 sum_{i<j} d_i d_j Cov(Z_i,Z_j)`.

The expected number of ordinary prompts carrying file i, including its first
write, is

\[
\sum_{n=1}^{m}E[Z_{i,n}]
=m-q_i\frac{1-q_i^m}{a_i}.
\]

The expected number of later warm reads is

\[
\sum_{n=1}^{m}P(K_i<n)
=m-\frac{1-q_i^m}{a_i}.
\]

**Derivation:** sum the geometric series for `P(K_i>n)=q_i^n`.
On K_i=k<=m, the file is written once and read on actions k+1,...,m.
It is present in the terminal compactor input exactly when K_i<=m.
Consequently, with ideal first-write price p_w, later-read price p_r,
terminal marginal price kappa and isolated first-use fee f_i,

\[
F_i=(p_w+\kappa)d_i+f_i,\qquad
E[Q_i]=F_i u_i(m)+p_r d_i\{m-u_i(m)/a_i\}.
\]

For a_i=0 all lazy restoration costs are zero; interpret that case directly,
not by dividing by zero. For a_i=1 lazy and eager coincide.

### 4.2 Cold misses and recovery calls

If subsequent file tokens survive in context but a cache entry misses with a
constant independent probability, replace p_r on later ordinary carries by
`c = q_hit*p_r + (1-q_hit)*p_w`, provided the eligible input is written on a miss.
Below eligibility, or for a provider with a different write policy, use the
appropriate p_i or provider ledger instead. This substitution requires
independence of the miss event from residency and current context.

Without that independence, the exact contribution uses joint terms such as

\[
d_i E\!\left[\sum_{n=K_i+1}^{T}
  \{p_r M_n+p_w(1-M_n)\}\right],
\]

plus first-insertion, terminal and recovery-call charges. Conditional cache
boundary/age tracking is needed for the real ledger. The apparent scalar
effective price cannot replace `E[M_n * resident_length_n]` arbitrarily.

If recovery entails a model request at first use k, replace f_i u_i by
`E[1{K_i<=T} f_i(K_i,s_{K_i})]` only if f_i is defined as its actual isolated
invoice. Shared or batched calls belong to a separate joint recovery invoice,
not once per file. Those calls can read the *entire* existing prefix, write new
commands, generate output and delay subsequent ordinary requests enough to
change cache expiry. They do not increase the fixed ordinary-action count N.

### 4.3 Fixed-cycle eager versus lazy

For eager restoration with the same per-file overhead,

\[
Q_i^{\rm eager}=F_i+p_r d_i(m-1).
\]

Subtracting lazy expectation gives

\[
\boxed{Q_i^{\rm eager}-E[Q_i^{\rm lazy}]
 = F_i q_i^m+p_r d_i\{u_i(m)/a_i-1\}\ge0.}
\]

The first nonnegative term is avoided unused loads; the second is avoided
pre-first-use carries. Here `u_i(m)>=a_i`. This result is exact only under the
same externally fixed cycle boundaries, unchanged versions, equal nonnegative
per-file overhead and nonnegative homogeneous token prices. It does not compare
the complete invoices of policies whose resets occur at different actions.

At small a_i*m, `u_i(m) approx a_i*m`, so only a small fraction of candidate
payload becomes mandatory. When a_i*m is large, u_i(m) approaches one, yet the
delay before loading still avoids roughly `(1/a_i-1)` read-carries per cycle.
For frequent files, that benefit is small. For a large low-demand file, carrying
it from every reset can be particularly wasteful.

## 5. Random cycles: exact occupancy identity and where independence fails

### 5.1 Independent-cycle formula

Let T>=1 be integrable and independent of the file's iid access process. Its
probability-generating function is `phi_T(q)=E[q^T]`. Conditioning on T yields

\[
u=1-\phi_T(1-a),\qquad
E[Q_i]=F_i u+p_r d_i\{E[T]-u/a\}.
\]

For fixed E[T], replacing random T by its mean overestimates u in this
independent reference model: `E[q^T]>=q^{E[T]}` by convexity of q^t. Thus
`u<=1-q^{E[T]}`. This is not a bound for endogenous threshold cycles.

### 5.2 A stronger identity under predictable stopping

T is allowed to depend on previous accesses and growth. Assume the decision
whether ordinary action n belongs to the current cycle is determined before
observing that action's requirement mark. Formally `{T>=n}` is measurable with
respect to the past `F_{n-1}`, and the conditional probability of first use,
given no earlier use, remains a. This is the post-growth/before-next-action
trigger convention in the existing contract. Assume E[T]<infinity, no file
mutation and no additional semantic eviction inside a cycle.

Define `B_n=1{T>=n, K>=n}`, a predictable indicator. Then

\[
u=E\sum_{n\ge1} B_n 1\{\hbox{use at }n\}
 =a E\sum_{n\ge1} B_n
 =a E[\min(T,K)].
\]

The first sum is one if and only if the file is used before the cycle ends;
conditional expectation gives the second equality. Nonnegative summands justify
interchanging expectation and sum. Pathwise,

\[
(T-K)_+=T-\min(T,K),
\]

which proves `E[(T-K)_+]=E[T]-u/a`. Therefore the same ideal invoice formula
holds under endogenous stopping, **with the actual joint-model value of u**.
An immediate useful bound is

\[
\boxed{a\le u\le\min(1,aE[T])}\quad(T\ge1).
\]

Constant conditional hazard is essential. Bursty Markov phases or version
invalidations require separate episode/hazard terms. Cross-file marks may be
correlated at the same action, but their law must not change the conditional
hazard after conditioning on the past.

### 5.3 Exact counterexample to the independent-T plug-in

Take reset s=0, threshold h=2, deterministic ordinary growth g=1, one initially
missing file d=1, iid file demand probability a, and restore before the ordinary
action. Check threshold before the next ordinary action; the cycle ends after
its crossing ordinary action.

- If the first action uses the file, one restoration plus one growth crosses
  h, so T=1.
- Otherwise T=2, whether or not the second action uses the file.

Thus `E[T]=2-a` and the actual first-use probability is
`u=1-(1-a)^2`. Treating the marginal T as independent gives
`u_ind=1-[a(1-a)+(1-a)^3]`, which is too small by `a^2(1-a)`.
At a=1/2, true u=0.75, plug-in u_ind=0.625 and E[T]=1.5. There are **zero**
post-load ordinary carries: every load ends this small cycle. The predictable
identity correctly gives `1.5-0.75/0.5=0`, while the independence plug-in
incorrectly gives `1.5-0.625/0.5=0.25`.

This is a constructive failure of independence, not a failure of renewal
theory: with fresh iid marks, the actual joint cycles can still regenerate.

## 6. Poisson first use and explicit threshold slopes

### 6.1 Continuous-time occupancy benchmark

Use t as a continuous ordinary-action clock, not wall-clock time. Assume first
required use K is exponential with rate lambda in that clock; the reset time
t is external. With u(t)=1-exp(-lambda*t) and per-unit-clock resident charge
c*d, a one-time restore/terminal charge F yields

\[
E[Q_i(t)]=F u(t)+c d\{t-u(t)/\lambda\}.
\]

Derive the resident area by integrating
`E[(t-K)_+]=integral_0^t P(K<=x) dx=t-u(t)/lambda`.
This is a fluid/Poisson accounting benchmark. Actual ordinary prompts are
discrete; do not relabel a wall-clock occupancy integral as a prompt invoice.

For independent random T, replace u by `1-E[exp(-lambda*T)]`. The residual
time to first use is exponential only under this model. A general renewal
access process requires its residual-life distribution at compaction, not
the unconditional inter-reference distribution.

### 6.2 Fixed m smooth surrogate

Extend u(m)=1-(1-a)^m to real m>0 only as an analytical interpolation. Write
`B=F-p_r*d/a`. Then

\[
r_i(m)=E[Q_i]/m=p_r d+B u(m)/m,
\]

\[
\boxed{r_i'(m)=B\{m u'(m)-u(m)\}/m^2},\qquad
u'(m)=-\log(1-a)(1-a)^m.
\]

For 0<a<1, `m u'(m)-u(m)<0`, since `exp(x)>1+x` for x>0.
Therefore longer cycles lower this file's cost rate when `F>p_r*d/a`, but
**raise** it when `F<p_r*d/a`. The latter can occur for rarely required files:
longer cycles make eventual load and lengthy subsequent residency more likely.

For deterministic ordinary growth g and exogenous cycle surrogate
`m(h)=(h-s)/g`, the threshold slope is `r_i'(m)/g`. In a complete renewal
model, add this term to the derivative of the base cycle invoice divided by
the same cycle length. This is not a derivative of integer threshold samples.

### 6.3 Exact passive exponential-growth benchmark aligned with analytic.py

Use the existing benchmark's externally generated clock
`T_h=1+Poisson((h-s)/g)`, which is independent of file demand. Restoration is
charged but deliberately does not change this pilot clock. This is a passive
reward extension of analytic.py, not an exact model of physical token growth
when restored files count toward h.

Writing `L(h)=1+(h-s)/g` and q=1-a,

\[
u(h)=1-q\exp[-a(h-s)/g],\qquad
u'(h)=a q\exp[-a(h-s)/g]/g,
\]

\[
r_i(h)=p_r d+B\frac{u(h)}{L(h)},\qquad
\boxed{r_i'(h)=B\frac{u'(h)L(h)-u(h)/g}{L(h)^2}}.
\]

Its bracket is strictly negative for h>s and 0<a<=1. To see this for a<1,
let z=a(h-s)/g; multiplying the numerator by g gives
`q exp(-z)(a+z)-1<0`. Its maximum over z>=0 occurs at z=1-a and is
`q exp(-q)-1<0` (or the endpoint), so the sign claim follows. At a=1,
u=1 and the bracket is -1/g. The a=0 case is exactly zero cost.

The full passive benchmark is

\[
r_{\rm augmented}(h)=r_{\rm analytic.py}(h)+\sum_i r_i(h),
\]

after ensuring the file payload and restoration invoices were not already
inside the baseline recovered s. No extra payload may be added on top of
65,588 while calling that aggregate an unchanged measured scenario.

### 6.4 What changes in a physical threshold model

In the ideal no-version/no-cache-miss physical cycle, let
`L_h=E[T_h]`, `u_i(h)=P(K_i<=T_h)`, and Q_0 include all non-file charges.
The predictable identity yields

\[
r(h)=\frac{E[Q_0(h)]+\sum_i F_i u_i(h)}{L_h}
  +\sum_i p_r d_i\left(1-\frac{u_i(h)}{a_i L_h}\right).
\]

When the displayed expectations are differentiable and L_h>0, put
`A_0(h)=E[Q_0(h)]`, `B_i=F_i-p_r d_i/a_i` to obtain

\[
\boxed{r'(h)=\frac{A_0'L_h-A_0L_h'
 +\sum_i B_i(u_i'L_h-u_iL_h')}{L_h^2}.}
\]

This states precisely what is missing from a constant reload derivation:
the joint stopping process determines both L_h and u_i(h), while Q_0's
compactor charge and ordinary-context area also change. If terminal marginal
price or restoration fee varies with h/state, include its direct derivative
and joint expectation, not constant F_i. Cache-dependent carry prices require
the full residency-cache joint rewards instead of this ideal simplification.

With integer token sizes or deterministic increments, r(h) can be a staircase.
Use reported finite differences on an admissible threshold grid rather than
asserting the classical derivative always exists.

### 6.5 Complete fixed-duration threshold-control relaxation

A particularly inexpensive pilot combines deterministic ordinary growth g,
pre-call warm context `s+g(n-1)`, non-file fixed cycle overhead K_0, and one
first-use file. With file payload and its terminal charge excluded from s and
K_0 to prevent duplication, the fixed-duration invoice rate is

\[
r(m)=p_r s+\frac{p_r g(m-1)}{2}+\frac{K_0}{m}
      +p_r d+\beta\frac{u(m)}{m},\qquad
\beta=d(p_w+\kappa-p_r/a)+f.
\]

Up-front independent per-action charges add constants and do not affect this
derivative. Its real-m interpolation has

\[
\boxed{r'(m)=\frac{p_r g}{2}-\frac{K_0}{m^2}
 +\beta\frac{m u'(m)-u(m)}{m^2}.}
\]

Relative to the no-file optimum, a positive beta contributes a negative slope
and a negative beta contributes a positive slope. Thus first-use restoration
need not move the economically favorable cycle duration in only one direction.
For f=0 the sign flips at `a=p_r/(p_w+kappa)`; the synthetic rates
`p_w=3.75`, `p_r=kappa=0.30` USD per million give a=0.074074....
This is an analytical mechanism distinction, not an empirical demand cutoff.
For a local strict interior minimum whose curvature remains positive, the
perturbation moves that minimum toward longer duration when beta>0 and toward
shorter duration when beta<0. Multiple-file terms are summed; they can oppose
one another. The cost-optimal integer duration is evaluated on its grid.

Mapping `h=s+g*m` is an **external duration-control parameterization**. In a
physical threshold implementation, mandatory file tokens advance the crossing,
so this mapping is not the actual cycle-length identity. Production write
costs of ordinary growth, first-cold-reset surcharge, compactor old-context
charges and ordinary output must either be included in the displayed constants
under declared assumptions or restored in the complete ledger. The formula is
not a replacement for the package's four-rate simulator.

## 7. Finite-horizon Markov evaluation and semi-Markov extension

For a fixed policy pi (eager/lazy/hybrid) and threshold h, define a transition
kernel `P_h^pi(s, d ell, ds')` that includes:

1. exogenous request gap and eligible-prefix expiry;
2. at most one threshold-triggered compaction at this boundary;
3. immediate compulsory reset material, with declared preservation semantics;
4. the requirement mark for the next fixed ordinary action;
5. all compulsory restoration requests and their duration, cache, input/output
   ledger and version updates;
6. exactly one ordinary action and its fixed task growth/output marks.

For n ordinary actions remaining,

\[
V_{0,h}^{\pi}(s)=0,\qquad
V_{n,h}^{\pi}(s)=\int[\ell+V_{n-1,h}^{\pi}(s')]
             P_h^{\pi}(s,d\ell,ds').
\]

Then `J_N^pi(h)=integral V_N,h^pi(s) nu_0(ds)` is the exact finite objective.
Only ordinary actions decrement n. An extra recovery call is not a productive
task step and cannot be discounted out of the horizon. Initial resident facts,
cache warmth, versions and phase are fixed and reported across threshold
comparisons. No reset is performed after the final ordinary action.

For tiny fact universes, x and ages may be discretized to evaluate this dynamic
program exactly. A larger research prototype can replay fixed demand/version
marks and Monte Carlo only the explicitly declared workload uncertainty. This
is a policy-evaluation recursion, not a claim that pi is the globally optimal
adaptive policy.

If gaps/restoration durations depend on phase or state, use a semi-Markov
description that tracks the holding-time law. Ordinary-action count remains
the denominator for the present objective; dividing by wall-clock duration
would answer a different question. Prefix TTL still depends on elapsed time.

### A two-state version-validity control

An inexpensive alternative to pretending file restoration happens only once is
a two-state per-file Markov control: 0 means no current valid fact; 1 means a
current valid fact is available. Before ordinary action n, let r_n be the
probability of state 1. Requirement probability a is independent of that state.
A missing required fact is restored. After the action, an independent version
change with probability b invalidates it before the next action. Starting
missing at reset, r_1=0 and

\[
r_{n+1}=(1-b)[a+(1-a)r_n],\qquad
P(\hbox{compulsory restoration at }n)=a(1-r_n).
\]

With `theta=(1-b)(1-a)<1`,

\[
r_n=r_*[1-\theta^{n-1}],\quad
r_*=\frac{(1-b)a}{a+b-ab},\quad
E[\hbox{reloads over }m]
=a\left[m(1-r_*)+r_*\frac{1-\theta^m}{1-\theta}\right].
\]

The stationary restoration rate is `a*b/(a+b-a*b)`. When b=0 this reduces to
`1-(1-a)^m` finite-cycle loads; when b=1 every required action loads anew.
The a=b=0 case is directly zero restoration and no need for an invariant-law
formula. Requirement/invalidations dependent on task phase need a larger chain.

This chain controls **semantic validity**, not physical token deletion. A stale
version may remain in historical context and incur carry charges even after its
fact becomes unusable. A new version then adds another payload. Append-only
history must retain those old token counts separately; substituting r_n for
physical resident length would underbill. If a harness replaces/removes stale
text in place, that policy changes cache prefix identity and needs its own
ledger. This small Markov control is useful before a full arbitrary-version
model, but cannot silently collapse validity and caching into one bit.

### Compulsory growth and overshoot

At the cycle level, with fixed base reset s and no mutation, a representative
physical recurrence after n ordinary actions is

\[
X_n=s+\sum_{j=1}^n G_j+\sum_i d_i1\{K_i\le n\}
       +\hbox{retained recovery-command/output tokens},
\qquad T_h=\inf\{n\ge1:X_n\ge h\}.
\]

The tool-file payload is not hidden again inside ordinary G_j. If G_j already
contains those file observations, remove the duplicate component before adding
the explicit d_i loads. At h crossing, X_T may exceed h; restored payload is
one reason a scalar iid growth model misses the overshoot mechanism.

If G_j are iid mean g independent of the past and E[T_h]<infinity, Wald's
identity gives `g E[T_h]=E[sum_{j<=T_h} G_j]`; it need not give `(h-s)/g`.
In the no-extra-recovery-token special case,

\[
gE[T_h]=h-s+E[\mathrm{overshoot}]-\sum_i d_i u_i(h).
\]

The formula is useful for checking a simulator, not an independent solution:
overshoot and u_i must be computed jointly. After restoration itself exceeds h,
the existing one-compaction-per-boundary convention still permits the pending
ordinary action; a repeated-reset-until-small loop would change the model and
can fail to terminate.

## 8. Regeneration, final cycles and boundary invoices

An iid access/growth law with identical reset facts, versions, cache state and
phase can yield regenerative cycles even though T and first use are dependent
*inside* a cycle. With integrable cycle invoice Q_h and ordinary length T_h,
the long-run ordinary-action rate is `E[Q_h]/E[T_h]`, not `E[Q_h/T_h]`.
Nonnegative accrued invoices avoid the pathological signed partial-reward
example in [Vlasiou's renewal-reward review](https://arxiv.org/abs/1404.5601),
but integrability and genuine regeneration must still be stated.

File edits, surviving version metadata, preserved recent facts and Markov
phases generally link cycles. At reset epochs the embedded state chain needs
its invariant law pi_h; the long-run ratio is
`integral E[Q_h|s] pi_h(ds) / integral E[T_h|s] pi_h(ds)` under stationarity,
ergodicity and integrability. That law changes with h. Do not pretend freshly
generated summaries refresh the entire file/task process.

For finite N, the last cycle has no terminal compactor. In a fixed last-cycle
length m, its file charge uses `F_last=p_w*d+f`, **not**
`p_w*d+kappa*d+f`. If initial files are already resident/warm, the initial
cycle has neither an initial file restoration nor a reset rewrite for them.
The first cycle may therefore have a different law from later cycles.

The policy's future absence of use is not known when a reset is undertaken.
Lazy compulsory restoration naturally avoids loading files never required
before finite termination. A long-run N*r(h) approximation can miss this
boundary advantage and bill a nonexistent final compaction. The finite DP is
the primary result when only a few cycles occur.

## 9. Useful conjectures, falsifiers and next measurement

### Exact claim that should be tested first

The scalar first-use probability plus retention area should reproduce the
fixed-cycle warm-ledger invoice under iid per-file hazards. Exhaustive
enumeration, not a large random simulation, is enough to test it. The probe
listed below also reproduces the endogenous-threshold independence failure.

### A qualified engineering conjecture

If the maximum compulsory resident payload `D_max` is small relative to the
ordinary-growth gap h-s, version churn is negligible and requirement/gap
coupling is weak, the passive independent-clock approximation should select
roughly the same near-optimal threshold region as the physical first-use model.
This is a practical conjecture, not a theorem. Small D_max alone does not
guarantee small error: a lattice crossing exactly at h can move discontinuously
when even one token is inserted. A rigorous approximation needs an additional
anti-concentration or smooth-crossing condition and price-weighted reward bounds.

Discriminating test: sweep `D_max/(h-s)`, demand hazard, burst correlation and
mutation rate with paired ordinary-action marks. Compare selected thresholds,
cost regret against the full joint model, E[T_h], u_i(h), restoration-call count
and resident token area. If a rare large load advances resets materially, stop
using the independent-T formula rather than merely refitting marginal T.

### Counterexample to universal lazy dominance: recovery batching

Fix two ordinary actions and two one-token files, used respectively on actions
1 and 2. Suppose first-use restoration truly requires separate model recovery
calls, each costing f=10 in arbitrary invoice units. An eager operation can
batch both files in one such call. Let first-write price be 1 and later read
price 0.1, with no terminal fee. Eager cost is `10+2+0.2=12.2`; lazy cost is
`20+2+0.1=22.1`. Both perform exactly two ordinary task actions.
The single-file dominance assumptions excluded shared/batched overhead, which
is precisely what fails. This synthetic construction is not a claim about
real provider request fees; the overhead can represent the whole extra model
round's context processing and output.

### Minimal measurements with decision value

For each fixed ordinary action, record required file/fact identifiers (hashed),
current versions, ranges/tokens, semantic availability and reason for a
compulsory read. For each compact, record immediate preservation/injection
and cleared facts. For each extra request, record its full disjoint input/write/
read/output usage and duration. Keep sizes, ages, phases and rates without
publishing source contents. Measure first-use lag and version-change lag;
the residence of those payloads is as important as their initial reread volume.

Priority: exact fixed-demand replay -> physical first-use threshold model ->
cache/gap coupling -> phase/version model. Fit named hazard laws only after
checking whether first-use lags and residual access ages support them.

## 10. Reproducible verification and accounting status

The companion research probe was promoted from temporary investigation to
`experiments/exact_first_use_control.py`; run from the repository root with
`uv run python experiments/exact_first_use_control.py`. It uses only the local
project environment and writes `.cache/experiments/first-use-reload/exact-control.json`.
The script exhaustively enumerates 2^8 Bernoulli demand paths at a=0.2,
verifies expected first-use/write/read counts and eager-minus-lazy cost,
enumerates the h=2 endogenous example, and checks the threshold-slope algebra
symbolically with SymPy. Its maintained conclusions and actual numerical
results are recorded below, so deleting generated output does not destroy the
research finding. It does not validate production billing or infer any empirical
workload law.

Executed 2026-10-06 using the root uv project environment (uv 0.12.9). All
enumeration assertions and both SymPy derivative identities passed. The fixed
eight-action case used d=12,000, a=0.2, p_w=3.75e-6 and
p_r=kappa=0.30e-6 USD/token, with no extra restoration-call fee. Exact results:

| Quantity | Result |
| --- | ---: |
| First-use probability | 0.83222784 |
| Expected later warm-read carries | 3.8388608 |
| Expected lazy file invoice | USD 0.054266171904 |
| Eager file invoice | USD 0.0738 |
| Eager-minus-lazy saving | USD 0.019533828096 |
| Endogenous toy actual u / independent-T plug-in | 0.75 / 0.625 |
| Endogenous toy actual carries / incorrect plug-in | 0 / 0.25 |

These are synthetic exact model expectations, not measurements of a coding
agent. Floating-point enumeration agrees within 1e-12 with the closed forms;
the symbolic differences simplify to exactly zero. No production code is
modified.

An additional root-environment SymPy check substituted b=0 and b=1 into the
two-state finite reload expression; its differences from `1-(1-a)^m` and
`a*m` respectively simplified to zero. This verifies the stated limiting
identities, not the adequacy of independent mutation/demand for real tasks.

## References

1. Peter J. Denning. *The working set model for program behavior*. Communications
   of the ACM 11(5), 323-333, 1968. [DOI](https://doi.org/10.1145/363095.363141).
   Peer-reviewed primary foundation for reference locality and working sets.
2. H. Opderbeck and W. W. Chu. *The Renewal Model for Program Behavior*. SIAM
   Journal on Computing 4(3), 356-374, 1975.
   [DOI](https://doi.org/10.1137/0204031). The publisher abstract and bibliographic
   record were consulted; no uninspected theorem from the full paper is invoked.
3. Maria Vlasiou. *Renewal Processes with Costs and Rewards*. Wiley Encyclopedia
   of Operations Research and Management Science, 2011; author manuscript
   updated 2018. [University metadata](https://research.utwente.nl/en/publications/renewal-processes-with-costs-and-rewards/),
   [author manuscript](https://arxiv.org/abs/1404.5601),
   [university-hosted full text](https://ris.utwente.nl/ws/portalfiles/portal/249488824/10.1002_9780470400531.eorms0722.pdf).
   Primary support for reward ratios and partial-cycle qualifications.
4. Anthropic. *Effective context engineering for AI agents*, 2025-09-29.
   [Production source](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
   Supports hybrid up-front/just-in-time retrieval as an actual mechanism,
   not a fitted demand process.
5. Internal dependencies: [stochastic-model.md](stochastic-model.md),
   [implementation-contract.md](../implementation-contract.md),
   [engineering-context-evidence.md](engineering-context-evidence.md),
   [analytic.py](../../src/context_compaction_lab/analytic.py).

Future academic frontier directions, including memory/compaction policies that
change task behavior, are handled in `compaction-memory-literature.md`. They
should be compared as separate policy/quality questions, not used to erase the
ordinary-action invariance of this invoice study.
