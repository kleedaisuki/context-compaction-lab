# Structural symbolic analysis of the finite four-price ledger

Recorded 2026-10-06. This is a theoretical analysis with executable exact
algebra, not another Monte Carlo workload study. Implementation:
`src/context_compaction_lab/structural_symbolics.py`; executable derivation:
`experiments/structural_symbolic_analysis.py`; maintained checks:
`tests/test_structural_symbolics.py`.

Prior internal knowledge reused:
[the working-set contract](../working-set-contract.md),
[mandatory first-use theory](mandatory-reload-theory.md),
[the previous smooth threshold surrogate](compaction-threshold-symbolic.md),
and [the actual-engine finite control](working-set-exact-control.md).
No production simulator, configuration, dependency, or inference was changed.

## 1. Main structural result

For a fixed finite-horizon policy with **price-independent state law and
feasibility**, the entire expected invoice is a pairing between a four-vector
of expected billed-token occupations and the four prices:

\[
\boxed{J_\pi(h,\alpha,p)=p\cdot L_\pi(h,\alpha).}
\]

This is not an approximation or a renewal formula. It includes full-context
processing in additional recovery requests, all compaction summaries, cache
misses, stable-prefix survival, file restoration, and output-token carries
through the occupation vector. The stochastic state law can be history
dependent, version dependent, or correlated; no stopping-time independence is
required for price linearity.

Consequences:

* Fixed-policy price gradients are the expected occupations, and the price
  Hessian is zero.
* At fixed demand parameters, comparing policies/thresholds is a hyperplane
  comparison in price space, not a new stochastic optimization for each price.
* The minimum over a fixed feasible policy set is **concave**, not convex, in
  the price vector. Active-policy changes produce the corners.
* For integer-token threshold states, the exact physical-threshold objective
  has jumps, not an ordinary smooth threshold gradient. Its distributional
  derivative consists of jump masses; integer forward differences contain the
  decision-relevant information.
* IID Bernoulli demands on N fixed ordinary-action indices yield degree-at-
  most-N exact occupation polynomials. **Endogenous stopping is already inside
  their coefficients**, not approximated by an independent cycle clock.

The actual-engine extraction below provides explicit nontrivial coefficients,
exact rational crossovers, an entire price/threshold phase diagram, and sign
certificates. The small fixture is solely a finite extraction basis for these
structural statements; it is not offered as an empirical workload model.

## 2. General finite-horizon occupation and price theorem

Let there be N ordinary actions. Between them, a policy may cause a bounded or
integrable number of additional compactor/recovery model requests. On outcome
omega define

\[
\ell_\pi(h,\omega)=(I,W,R,O),
\]

where I is uncached input, W newly written cached input, R cached reads, and O
generated output, including ordinary and additional model requests. These are
disjoint billed categories, not four copies of total prompt input. Tool payload
is later input, not generated output. Reload-event counts do not create an
extra fee unless an actual request introduces billed occupations.

Assume:

1. The policy and its transition/cache/feasibility law are fixed independently
   of p. The policy may depend on history, h, or alpha.
2. The exogenous law mu_alpha is independent of p.
3. Every expected occupation is finite; unsuccessful strict-loop trajectories
   are infeasible, not successful policies with cheap truncated invoices.
4. The price vector consists of four nonnegative per-token rates without an
   undeclared price tier or nonlinear provider invoice.

Pathwise the invoice is `p dot ell`. Linearity of finite expectation gives

\[
J_\pi=\int p\cdot\ell_\pi\,d\mu_\alpha
     =p\cdot\underbrace{\int\ell_\pi\,d\mu_\alpha}_{L_\pi}.
\]

Therefore, without interchanging a derivative with a state-dependent kernel,

\[
\boxed{\nabla_pJ_\pi=L_\pi,\qquad \nabla_p^2J_\pi=0.}
\]

For two candidates A and B,

\[
J_A-J_B=p\cdot(L_A-L_B).
\]

At fixed alpha the tie set is a hyperplane through the origin, restricted to
the nonnegative price cone. Candidate A is globally optimal exactly in the
intersection of its comparison halfspaces with every other feasible candidate.
The pairwise tie alone is **not** proof of global optimality.

With a finite candidate set, take the convex hull of its occupation vectors.
Minimizing a linear price pairing exposes a lower face of this occupation
polytope. This replaces repeated price sweeps by one exact geometric object.
If alpha also varies, its vertices vary polynomially in the Bernoulli control,
and tie surfaces satisfy `p dot Delta L(alpha)=0`; these are not generally
hyperplanes jointly in alpha and p.

### Price-independence is a real hypothesis

The current simulator uses prices only when its completed token totals are
paired into an invoice; its state transitions satisfy this premise. A controller
that changes its reset rule as prices change must be treated as a collection of
fixed candidate policies, not one fixed price-independent occupation vector.
If feasibility depends on a dollar budget, the feasible candidate set itself
changes with p and the concavity theorem below need not apply. Nonlinear tiers
or price-dependent token generation likewise require a different invoice law.

## 3. Concavity of the optimal-value lower envelope

Fix alpha and a nonempty feasible candidate set A independent of price, and set

\[
V(p)=\inf_{a\in A}p\cdot L_a.
\]

For p,q and 0<=t<=1,

\[
\begin{aligned}
V(tp+(1-t)q)
&=\inf_a\{t(p\cdot L_a)+(1-t)(q\cdot L_a)\}\\
&\ge t\inf_a(p\cdot L_a)+(1-t)\inf_a(q\cdot L_a)\\
&=tV(p)+(1-t)V(q).
\end{aligned}
\]

This proves concavity. It also gives positive homogeneity, `V(cp)=cV(p)` for
c>=0, and coordinatewise monotonicity because occupations are nonnegative.
For a finite set, V is piecewise linear. At a unique active candidate its
gradient is that candidate's occupation; at a tie it can be nondifferentiable.
An active occupation is a **supergradient**, since

\[
V(q)\le q\cdot L_a=V(p)+L_a\cdot(q-p).
\]

In the finite setting the superdifferential is the convex hull of the active
occupations. Thus price sensitivity has a practical meaning: after a policy
switch, the slope changes to a different billed-token vector. Concavity of V
does not imply convexity/unimodality of the threshold objective, or concavity
in the demand parameter alpha.

## 4. Exact demand polynomial, without an independent stopping clock

Enumerate all b in {0,1}^N. Let k(b) be its success count and let the actual
simulator supply its integer occupation ell(b), including every endogenous
reset and recovery. For IID ordinary-index demands with probability alpha,

\[
L_j(\alpha)=\sum_b\ell_j(b)\alpha^{k(b)}(1-\alpha)^{N-k(b)}.
\]

Every occupation is a polynomial of degree <=N. Let

\[
s_{j,k}=\sum_{b:k(b)=k}\ell_j(b).
\]

Then `L_j=sum_k s_jk alpha^k (1-alpha)^(N-k)`. No additional binomial
multiplicity belongs in this expression: it is already in the grouped sums.
Equivalently,

\[
L_j=\sum_{k=0}^N\bar\ell_{j,k}B_{k,N}(\alpha),\quad
\bar\ell_{j,k}=s_{j,k}/\binom Nk,\quad
B_{k,N}=\binom Nk\alpha^k(1-\alpha)^{N-k}.
\]

The nonnegative Bernstein basis explains why negative power coefficients do
not mean negative expected tokens. Strictly signed Bernstein coefficients
certify a strict sign throughout [0,1]. The new module computes those
coefficients exactly, not by a numerical sign grid.

For 0<alpha<1, differentiating the finite path sum additionally gives

\[
\boxed{\frac{dL_j}{d\alpha}
 =E\!\left[\ell_j\frac{K-N\alpha}{\alpha(1-\alpha)}\right]
 =\frac{\operatorname{Cov}(\ell_j,K)}{\alpha(1-\alpha)}.}
\]

Here K is the success count over all N fixed ordinary-action indices, not a
first-use time. This likelihood-ratio identity retains the covariance between
demands and changed stopping states. It is not the derivative of an isolated
reload-probability fee. At alpha=0 or 1, evaluate the polynomial derivative
directly rather than dividing by alpha(1-alpha).

## 5. Executable extraction and exact coefficients

The experiment reuses the previous eight-action actual-engine fixture: one
24-token file plus a 2-token wrapper; 32 warm stable base tokens; 8 summary
tokens; 20 non-file retained input and 10 output per ordinary action; 2-token
ordinary uncached suffix; 4-token compactor instruction; cache minimum 16;
no expiry or mutations; atomic resets; **no terminal compact**. Only alpha is
now symbolic. All 256 paths are converted to integer occupations first; no
floating expectation or polynomial fit is used to obtain coefficients.

The engine currently represents totals as float64. The exact-lifting boundary
rejects nonintegral values and values >=2^53, rather than rounding or inventing
rationals. The fixture's token additions remain far below that bound. The
polynomial extraction also requires the entire unique Boolean cube and full
successful completion. It cannot silently drop a failed path.

### First-use at h=100

SymPy returns the exact vector

\[
\boxed{L_{100}(\alpha)=
\left(58,
320+208\alpha-78\alpha^2-52\alpha^3+26\alpha^4,
578+156\alpha-26\alpha^2,
104\right).}
\]

The degree-four reduction is an actual cancellation in the finite path sum,
not a forced degree-four approximation. With exact prices

\[
p=(3/10^6,\ 3/800000,\ 3/10^7,\ 3/200000),
\]

the full expected price is

\[
\boxed{J_{100}(\alpha)=
\frac{3}{10^7}
\left(325\alpha^4-650\alpha^3-1001\alpha^2+2756\alpha+10358\right).}
\]

Its demand derivative is

\[
J_{100}'(\alpha)=\frac{39}{5\cdot10^6}
\left(50\alpha^3-75\alpha^2-77\alpha+106\right).
\]

At alpha=7/20,

\[
J_{100}=\frac{214598127}{64000000000},\qquad
J_{100}'=\frac{449319}{800000000}.
\]

The cubic in the derivative is positive on [0,1]: its derivative is
`150 alpha(alpha-1)-77 < 0`, so its minimum is its value 4 at alpha=1.
Furthermore `J_100''<0` throughout this interval. Thus this particular
physical-threshold policy has increasing, concave demand cost.

That does **not** transfer to arbitrary h. At h=71 the actual-engine default-
price extraction has

\[
J_{71}(\alpha)=\frac{3}{10^7}
(915\alpha^7-4605\alpha^6+11100\alpha^5-14880\alpha^4
+13050\alpha^3-5670\alpha^2+6450\alpha+10306),
\]

and `J_71''(7/20)=1764843003/3200000000000 > 0`. This exact counterexample
prevents incorrectly extending the price-envelope concavity theorem to
demand intensity.

### Policy hyperplanes and a full-alpha dominance certificate

At h=100, stable-prefix first-use minus cold-reset first-use is

\[
\boxed{\Delta J_{\rm stable}=96(p_r-p_w).}
\]

It is independent of alpha here, because all paths have three resets and each
surviving stable base moves 32 tokens from writes to reads. Stable survival
helps when `p_r<p_w`, ties when equal, and hurts when the mathematical price
cone allows `p_r>p_w`. This is not a change in semantic file availability.

For retained file plus retained read guard minus first-use, let q=1-alpha.
The exact difference simplifies to

\[
\boxed{\Delta J_{\rm retain}
=26\alpha q\{p_wP_w(q)+p_rP_r(q)\},}
\]

where

\[
P_w(q)=q^6+2q^5+2q^4+3q^3+4q^2+3q,
\]
\[
P_r(q)=q^5+2q^4+3q^3+4q^2+5q+3.
\]

Every coefficient is nonnegative. Thus at this h, retaining both file and
guard is dominated by first-use for **every** alpha in [0,1] and every
nonnegative price vector; the inequality is strict for 0<alpha<1 when either
write or read price is positive. This extends a single numerical comparison
to an exact whole-parameter certificate, while retaining its stated fixture
and threshold scope. At alpha=0 or 1 the policies tie.

## 6. Exact physical-threshold structure and derivative

If retained lengths and append/reset token counts are integers, comparing
`x >= h` is equivalent to `x >= ceil(h)`. Induction on actual simulator
transitions therefore gives the pathwise and expected identity

\[
J(h)=J(\lceil h\rceil),\qquad h>0.
\]

This identity does not require IID demands. In the finite extraction support,
the experiment obtains a complete finite cell partition, preserves alpha
symbolically on every cell, and represents it as a SymPy Piecewise expression.
There are 22 first-use occupation cells, 12 eager cells, and 22 cells for each
of the four retention/stable variants. The final cell is an unbounded tail.
Cells are derived from changes in **four occupations**, not merely coincident
floating costs at one alpha/price.

Write a jump at integer k as `Delta_k=J(k+1)-J(k)`. The right-closed trigger
convention puts J(k) at the point itself and the next value immediately to its
right. Point values do not affect its distributional derivative:

\[
\boxed{D_hJ=\sum_{k\ge1}\Delta_k\,\delta(h-k).}
\]

The executable `ThresholdCurve.distributional_derivative` returns these exact
Dirac masses, with alpha and all four prices still symbolic. Its ordinary
Piecewise derivative is zero inside cells, not a substitute for the jump
derivative. A threshold optimum is characterized by cells, not by setting a
fictitious smooth derivative to zero. The full artifact stores all exact
integer deltas and the entire distributional expression for every policy.

For continuous-valued state laws an expected threshold function may instead
be smooth; boundary-flux derivatives then depend on that law. Those are not
proved by this integer-state extraction. The older smooth duration surrogate
remains a different model, not the exact gradient of this physical ledger.

## 7. Threshold comparison crossover, symbolic in alpha

Compare first-use on the cell containing h=157 (real h in (156,178]) with the
no-compaction cell h>268. Their occupation difference is

\[
\Delta L=(14, A(\alpha), -B(\alpha), 8),
\]

where

\[
\begin{aligned}
A(\alpha)={}&52\alpha^8-390\alpha^7+1274\alpha^6-2340\alpha^5\\
&+2574\alpha^4-1638\alpha^3+494\alpha^2+30,
\end{aligned}
\]
\[
\begin{aligned}
B(\alpha)={}&52\alpha^7-390\alpha^6+1248\alpha^5-2262\alpha^4\\
&+2522\alpha^3-1690\alpha^2+572\alpha+284.
\end{aligned}
\]

An exact Bernstein certificate proves A>0 and B>0 throughout [0,1]. For
example the degree-eight coefficients of -B are

\[
(-284,-711/2,-5133/14,-10149/28,-12449/35,
-349,-2404/7,-1357/4,-336),
\]

all strictly negative; the certificate is algebraic, not a sampling claim.

Hold `p_i/p_w=4/5`, `p_o/p_w=4`, `p_w>0`, and let r=p_r/p_w. Then

\[
\frac{\Delta J}{p_w}=A(\alpha)+\frac{216}{5}-rB(\alpha),
\]

so the unique economically admissible pairwise crossover is

\[
\boxed{r_*(\alpha)=\frac{A(\alpha)+216/5}{B(\alpha)}.}
\]

The earlier-reset candidate is cheaper iff r>r_*(alpha). At alpha=7/20,

\[
r_* = \frac{588316516163}{2286290402180}
     \approx0.25732361715818536.
\]

The experiment substitutes this symbolic rational function into Delta J and
verifies that its numerator is **identically zero**, not merely small at a
sample point. Its alpha derivative is computed exactly. Root isolation of
that derivative's numerator produces precisely one simple root in (0,1), in

\[
\left(\frac{2329}{19957},\frac{1988}{17035}\right).
\]

The derivative is negative at alpha=0 and positive at alpha=1, with no other
interior roots and no denominator zero by the Bernstein certificate. Thus the
price-ratio crossover decreases and then increases; demand intensity does
not shift this threshold comparison in one universal direction. For reference,
r_*(0)=0.25774648, r_*(0.1)=0.23495218, r_*(0.35)=0.25732362, and
r_*(1)=0.29523810. Those decimals only display the exact rational evaluations.

## 8. Global exact price/threshold lower hull

The previous pairwise root is not the global price switch. The experiment
computes the lower hull over **all six policies and all effective physical
threshold cells**, keeping alpha=7/20 and the same fixed input/output ratios.
Every line is `J/p_w = b+rR` with rational b,R. Intersections, slope ordering,
and optimizer ties are computed with exact rationals. A candidate optimal only
at a breakpoint is not discarded from the reported endpoint ties.

| Open price-ratio interval r | Global minimizing policy | Integer h interval |
| --- | --- | --- |
| 0 .. 0.1842509174 | First-use variants without a reset; equivalent here | 269 .. infinity |
| 0.1842509174 .. 0.8337907892 | Stable-prefix first use | 157 .. 178 |
| 0.8337907892 .. 1 | Stable-prefix first use | 119 .. 122 |
| 1 .. 1.0447826045 | First use | 119 .. 122 |
| 1.0447826045 .. 1.6614803254 | First use | 97 .. 100 |
| 1.6614803254 .. 2.1640302952 | First use | 89 .. 92 |
| 2.1640302952 .. 2.9829550416 | First use | 71 .. 88 |
| 2.9829550416 .. 3.3272727273 | First use | 63 .. 70 |
| 3.3272727273 .. infinity | First use | 33 .. 62 |

All displayed boundaries are backed by exact artifact rationals. In particular
the first global switch is

\[
\boxed{r_1=127838838721/693830134060,}
\]

not the pairwise 0.2573236172 boundary. Stable-prefix reuse changes the globally
relevant hyperplane. The next boundary is
`883638123047/1059783982420`; subsequent ones are exactly
`1`, `1606254/1537405`, `567597401/341621500`,
`8902150867/4113690500`, `13636201629/4571373500`, and `183/55`.
At boundaries both adjoining candidates tie; the full artifact reports every
tie. It also records each segment's exact slope and intercept.

The selected read occupation decreases along increasing r, providing an
explicit realization of the concavity theorem. The integer threshold cells
need not vary smoothly. The ranges r>1 are a mathematical completion of the
nonnegative price cone, not a claim about current providers or a deployment
recommendation. The entire phase diagram is scoped to this extraction basis;
the occupation/hyperplane/lower-envelope method itself is general.

## 9. Reproduction, independent checks, and contribution

```powershell
uv run python experiments/structural_symbolic_analysis.py
uv run pytest tests/test_structural_symbolics.py -q
uv run ruff check src/context_compaction_lab/structural_symbolics.py experiments/structural_symbolic_analysis.py tests/test_structural_symbolics.py
```

The complete exact formulas, all polynomial coefficients, threshold cells,
integer jumps, distributional derivatives, rational price phases, stationary
root isolation, and direct rational checks are materialized in
`.cache/structural-symbolic-analysis/results.json`. The checked-in source and
this note are the maintained deliverables; cache outputs are regenerable.

The recorded derivation run took 12.75 seconds. Nine tests passed in 0.86
seconds, and Ruff passed. These are local execution observations. For each
h=100 policy the experiment independently computes a direct rational sum over
all per-path integer invoices, then requires equality with the grouped symbolic
polynomial evaluated at alpha=7/20. It additionally checks the corresponding
existing floating invoice as a numeric sanity check, without using that float
to derive symbolic coefficients. No cached Monte Carlo estimate is an input.

The value delivered beyond the earlier enumeration is structural:

* One reusable occupation object exposes every price derivative and comparison.
* Numerical retention harm becomes an exact full-alpha dominance certificate.
* A threshold comparison becomes an exact rational function with certified
  inequality direction and a nonmonotonic demand response.
* A full finite policy family becomes a globally correct price phase diagram,
  distinguishing its first switch from an appealing but incorrect pairwise one.
* Integer trigger optimization is connected to distributional jump calculus,
  while retaining the real compaction/recovery stopping state.

This work does not assert a new general theorem for elementary linearity or
concavity, nor universal optimality of first-use, stable caches, or any h.
It turns existing working-set mechanisms and four-price engineering contracts
into exact, inspectable structural results. The next useful extension is a
larger calibrated state's occupation operator or dynamic-programming basis,
not arbitrary extra marginal distributions or additional toy simulations.
