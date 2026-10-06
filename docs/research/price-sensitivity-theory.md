# Four-price and mechanism sensitivities of analytic compaction control

Recorded 2026-10-06. Scope: theory first, with explicit sign/phase boundaries
that community-driven trajectories can subsequently investigate. This extends
[renewal-analytic-control.md](renewal-analytic-control.md),
[renewal-closed-forms.md](renewal-closed-forms.md), and the exact ledger in
[renewal-study-contract.md](renewal-study-contract.md). The conditional-history
layer remains in [general-stochastic-control-theory.md](general-stochastic-control-theory.md).
No production code, dependency or test suite is changed by this note.

## 1. Results before parameter sweeps

The important quantity is not one isolated cache price: both compulsory reset
price A and history-carry price c change with the four-price vector. Under the
canonical renewal reduction, the optimal gap L=H-S obeys D(L)=A/c. Writing
V=S-B, K=compactor instruction tokens, C=generated summary tokens and q=the
independent eligible-prefix hit probability gives

\[
\boxed{c=(1-q)p_w+qp_r,\qquad
A=p_i[K+(1-q)S]+qp_wV+qp_rB+p_oC.}
\]

Consequences:

1. Uniform scaling of all four token rates changes every bill by that scale,
   but leaves the optimal thresholds unchanged. Relative prices matter.
2. Increasing p_i or p_o raises the core gap when their setup coefficients
   are nonzero. Ordinary output volume alone, held separate from growth,
   does not move the optimum; recurring summary output does.
3. Increasing p_w can **lower** the gap when misses dominate, but **raise**
   it when hits dominate. There is an explicit unique q crossover.
4. Increasing p_r usually lowers the gap. A genuine opposite regime exists
   when a large stable warm prefix dominates and write premiums are high.
5. With p_w>=p_i>=p_r, increasing q raises the **core** gap, although it lowers
   the full physical invoice. A sufficiently large cold terminal tail can
   reverse the threshold direction even in that standard price ordering.
6. The optimal bill is the concave lower envelope of price-linear invoices.
   Its price gradient is optimal expected disjoint usage; threshold derivatives
   and bill derivatives are different objects.
7. Smooth-core regret from retaining an outdated threshold is second order,
   with an explicit rank-one curvature formula. Atomic price boundaries instead
   have exact piecewise-linear switch losses and optimal plateaus.

These are mechanism-conditioned analytic statements, not claims about changing
models with different behavior or inferring q from billed cache-read share.

## 2. Definitions, interventions and regularity

Fix the nonnegative iid ordinary-growth law G with finite positive mean g.
Let U(L), M(L), D(L)=L*U(L)-M(L) be the renewal occupations defined in the
analytic-control note, using >= crossing and strict pre-crossing measure.
S is the complete reconstructed context, B an eligible unchanged stable prefix
inside S, and V=S-B the volatile rewritten part. Assume 0<=B<=S and C<=V when
the generated summary is part of this reset. K,C are nonnegative token counts.

q is an independent hit probability at an ordinary boundary, not an observed
token-weighted cache-read fraction. It affects history-carry and compactor
prices differently:

\[
c=(1-q)p_w+qp_r,\qquad
\kappa=(1-q)p_i+qp_r.
\]

The setup/output invoice is `F_0=p_i*K+p_o*C`. The rewrite surcharge is
`(p_w-c)V=q(p_w-p_r)V`, so

\[
A=F_0+(p_w-c)V+\kappa S.
\]

Expanding proves the boxed four-price formula. Its coefficient vector is

\[
a=(K+(1-q)S,\ qV,\ qB,\ C),\qquad
v=(0,\ 1-q,\ q,\ 0),\quad A=p\cdot a,\quad c=p\cdot v.
\]

Prices p=(p_i,p_w,p_r,p_o) are nonnegative USD/token with c>0 and A>0.
For classical derivatives assume an interior canonical root and continuity of
U at that root; density u=U' is additionally needed for curvature/mixed
derivatives. The root itself is distribution-general. Boundary roots, atoms
and grids are addressed below.

Unless explicitly stated, a price partial holds q,S,B,C,K and the growth law
fixed. A q partial holds prices and workload fixed. A B partial reclassifies
known warm material **within fixed S**, rather than adding another B on top
of a full-context anchor. A summary-size partial has two distinct meanings;
we distinguish preserving other material from silently replacing it.

Provider bundles need total derivatives, not imagined independent changes:
changing a cache TTL tier can change p_w and q together; changing a model can
change all prices, output behavior, growth and cache eligibility together.
The latter is not a pure price experiment.

Token counts and executable thresholds are integer-valued. Material-size
derivatives describe the continuous analytical extension; use explicit one-
token or declared-step finite contrasts for an integer implementation, and
report optimal regions rather than implying subtoken operating precision.

## 3. Master derivative and price shares

Let R=A/c and let L_*=D^{-1}(R). Since D'=U at continuity points,

\[
\boxed{\frac{\partial L_*}{\partial p_j}
=\frac{a_j-Rv_j}{cU_*},\qquad U_*=U(L_*).}
\]

**Proof.** `R_pj=(a_j*c-A*v_j)/c^2=(a_j-R*v_j)/c`; differentiate D(L)=R.
This automatically includes the numerator and denominator changes. Replacing
it by A_pj/(cU) wrongly treats carry price as fixed for p_w,p_r.

The signs do not depend on the growth-law family: U_*>0 only changes magnitude.
The law still changes where the root lies, the sensitivity magnitude, plateaus
and finite-horizon effects. Define setup and carry expenditure shares

\[
\omega_j^A=\frac{p_ja_j}{A},\qquad
\omega_j^c=\frac{p_jv_j}{c}.
\]

Then the gap price elasticities are

\[
\boxed{\epsilon_{L,p_j}
=\epsilon_{L,R}(\omega_j^A-\omega_j^c),\qquad
\epsilon_{L,R}=\frac{D(L_*)}{L_*U_*}
=1-\frac{M(L_*)}{L_*U_*}.}
\]

`0<epsilon_(L,R)<=1`; in the large-gap regime it approaches 1/2. For
exponential growth, it is `(1+L/(2g))/(1+L/g)`. A price supports a larger gap
exactly when its setup share exceeds its carry share. With S fixed the absolute
threshold elasticity is `(L_*/H_*)*epsilon_(L,pj)`, smaller in magnitude because
the restored context shifts the origin.

All four gap price elasticities sum to zero. This is also Euler's identity
`sum_j p_j*L_pj=0`, reflecting degree-zero homogeneity of the policy.

## 4. Complete core sign regimes

Set T_0=p_i*K+p_o*C, so A=(T_0+p_i*S)+q[(p_w-p_i)S-(p_w-p_r)B].

### 4.1 Uncached input and generated output prices

\[
L_{p_i}=\frac{K+(1-q)S}{cU_*}\ge0,\qquad
L_{p_o}=\frac C{cU_*}\ge0.
\]

p_i raises the gap through compactor instructions and the miss-priced old
context; p_o raises it through recurring generated summaries. Their ordinary
per-action charges are additional invoice effects but do not move the optimum
when they are threshold-independent. At q=1,K=0 input price has no core policy
effect; at C=0 output price has no core policy effect even if ordinary output
is expensive. Zero derivatives are genuine cases, not omitted terms.

### 4.2 Cache-write price changes direction with the hit regime

\[
\boxed{\operatorname{sign}L_{p_w}
=\operatorname{sign}N_w(q),}
\]

\[
N_w(q)=q p_r(qS-B)
 -(1-q)\{p_i[K+(1-q)S]+p_oC\}.
\]

At q=0, `L_pw=-A/(p_w^2 U*)<0`: a miss writes the whole carried history,
so more expensive writes favor earlier compaction. At q=1,
`L_pw=V/(p_r U*)>=0`: old history reads cheaply, while the cold mandatory reset
is rewritten, so more expensive writes favor longer cycles.

When p_r>0,V>0 and T_0+p_i*S>0 there is a unique q_w in [B/S,1) at which the
sign changes. Below q_w it is negative, above q_w positive. To prove uniqueness,
for q<=B/S the first term is nonpositive and setup term nonnegative. For
q>=B/S the derivative of N_w is
`p_r*(2qS-B)+T_0+2p_i*(1-q)S>0` except degenerate zero-price cases. Finally
N_w(1)=p_r*V>0. This is a structural phase boundary, not a numerical sweep.

Its exact equation is the quadratic

\[
S(p_r-p_i)q_w^2+(T_0+2p_iS-p_rB)q_w-(T_0+p_iS)=0.
\]

If V=0, writes do not raise the q=1 optimum and their effect is nonpositive
for q<1. If p_r=0 and q<1, writes likewise do not have the usual positive
high-hit effect; q=1 would violate c>0.

### 4.3 Cache-read price has a qualified reversal regime

\[
\boxed{\operatorname{sign}L_{p_r}
=\operatorname{sign}\left[q\{p_w(B-qS)
                  -p_i[K+(1-q)S]-p_oC\}\right].}
\]

At q=0 it is zero. For q>0, increasing p_r generally raises ordinary carrying
expense and lowers the gap. But it also raises the recurring compactor price
of the stable prefix B. The latter can dominate.

If p_w<=p_i, the derivative is nonpositive everywhere. If p_w>p_i, define

\[
q_r=\frac{p_wB-p_i(K+S)-p_oC}{(p_w-p_i)S}.
\]

A positive reversal regime exists iff

\[
\boxed{p_wB>p_i(K+S)+p_oC.}
\]

Then 0<q_r<=1, and L_pr is positive for 0<q<q_r, zero at q_r, negative above.
Large summary/output setup expense can eliminate it. If the displayed
inequality fails, increasing p_r never raises this core optimum.

For example, the declared normalized-price control
`p=(1,2,0.1,1)`, S=10,B=9,V=1,C=1,K=1 has q_r=0.6, so the read-price effect
is positive at q=0.5. The generated summary fits within V. This is a simple
parameter-consistent counterexample to "read price up always means compact
earlier", not a provider-price quote.

### 4.4 Cache-hit probability and its invariant sign numerator

Let delta_wr=p_w-p_r. Since A and c are affine in q, their quotient has

\[
\boxed{L_q=\frac{N_q}{c^2U_*},\qquad
N_q=(p_w-p_r)(p_wV+p_iK+p_oC)+p_r(p_w-p_i)S.}
\]

N_q is independent of q. Thus the q-to-core-gap direction cannot itself
reverse as q varies for fixed prices/materials; only its magnitude changes.
For p_w>=p_i>=p_r, N_q>=0: better caching supports a longer core gap.
In the alternate ordering p_i>p_w>=p_r, it raises the gap iff

\[
(p_w-p_r)(p_wV+p_iK+p_oC)>p_r(p_i-p_w)S.
\]

This compares ordinary-cache savings/setup amortization against cheaper
cached compactor processing. Equality makes the core gap q-invariant.
The full marked ledger has an additional q effect, derived in Section 7;
do not export this invariant-sign statement beyond the core approximation.

## 5. Material, summary, timing and growth variables

### 5.1 Stable prefix at fixed reconstructed total

At fixed S, increasing an explicitly eligible stable B reduces V=S-B:

\[
\boxed{L_B=H_B=-\frac{q(p_w-p_r)}{cU_*}.}
\]

For normal read discounts this is nonpositive. Cheaper mandatory rebuilding
permits more frequent compaction. At q=0 there is no stable-cache benefit in
this ledger; copied text alone does not turn into warm eligible tokens.

Adding new stable material instead, holding V,C,K fixed, increases S:
`H_(new B)=1+kappa/(cU*)`. These are different interventions and must not be
described by the same "B sensitivity".

### 5.2 Required volatile material and summary growth preserving other material

Let S=B+V, with B fixed. Extra mandatory volatile input has

\[
a_V=(1-q)p_i+qp_w,\qquad
\boxed{H_V=1+\frac{a_V}{cU_*}>1.}
\]

There is a direct shift of the reset floor and an additional amortization shift.
If C increases while preserving all other material, it increases V and S by
the same amount and adds recurring output expense:

\[
\boxed{H_C=1+\frac{p_o+(1-q)p_i+qp_w}{cU_*}.}
\]

If total S is instead artificially held fixed by removing other reconstructed
material, the purely accounting derivative would be `H_C=p_o/(cU*)`.
That intervention may violate the compulsory working-set contract and is not
the primary summary experiment. Do not silently remove documents to keep a
larger summary scenario's S unchanged.

The compressor instruction-size effect is `H_K=p_i/(cU*)`. Extra reset
model rounds can be included only with their actual invoice and cache/time
consequences, not by interpreting added calls as productive ordinary work.

### 5.3 Ordinary generated output versus post-call retained tail

The marked study uses o=E[ordinary billed output] and theta separately:
G is the net ordinary growth already including previously retained outputs/
tools; theta*G is the portion appended after the current request rather than
before it. Changing o with G,theta,S fixed changes the invoice by p_o per extra
output token per ordinary action, but not the threshold. Hidden billed output
can make this a meaningful controlled intervention.

If added output is actually retained, it also changes the growth law and/or
timing split. Then apply the full joint-variable derivative; o alone is not
the mechanism. The full marked theta effect is derived below. The core equation
has no theta dependence because its threshold-independent base terms do not
enter D(L)=A/c; neglecting the marked correction is exactly the approximation.

### 5.4 Growth scale and dispersion are separate from prices

For G=a*Z, with A,c,S fixed, the analytic-control note proves
`L*(a)=a*D_Z^{-1}(A/(ca))` and
`dL*/da=M_Z(z)/U_Z(z)>=0`, z=L*/a. Its growth-scale elasticity is
`M/(L U)`, complementary to the setup-ratio elasticity D/(L U).
Larger scale raises the gap sublinearly. A same-mean convex-order spread
instead raises D and lowers the gap. CV alone does not establish that order.
Price sign regimes remain unchanged by either law choice, but magnitude and
curvature change.

## 6. Mixed price/cache/material effects

For any scalar parameters s,t that affect R but not the renewal law,

\[
\boxed{L_{st}=\frac{R_{st}}{U_*}
 -\frac{u_* R_sR_t}{U_*^3}.}
\]

This follows by differentiating L_s=R_s/U. The second term is the endogenous
root shift; signs of mixed ratio derivatives alone are not mixed threshold
signs. At atoms use one-sided/incremental comparisons, not a classical u_*.

### 6.1 q-by-price interactions

Because R_q=N_q/c^2,

\[
R_{q p_j}=\frac{(N_q)_{p_j}}{c^2}
                  -\frac{2N_q v_j}{c^3}.
\]

In particular,

\[
R_{q p_i}=\frac{(p_w-p_r)K-p_rS}{c^2},\qquad
R_{q p_o}=\frac{(p_w-p_r)C}{c^2}.
\]

In the usual N_q>0 regime, if `(p_w-p_r)K<=p_rS`, increasing q attenuates
input-price sensitivity of the optimum: both terms of L_qpi are nonpositive
(strict when the root has density and the relevant coefficients are positive).
For output price, the direct interaction is positive but root curvature opposes
it. Its exact sign condition is

\[
\operatorname{sign}L_{q p_o}
=\operatorname{sign}\{(p_w-p_r)cU_*^2-u_*N_q\}
\quad(C>0).
\]

For exponential growth, `c*U_*^2/u_*=c*g+2A`, so that condition is
`(p_w-p_r)(c*g+2A)>N_q`. This supplies a phase boundary instead of asserting
all positive mixed effects from cheaper caching.

### 6.2 Price-by-stable-prefix interactions

At fixed S,

\[
R_B=-q(p_w-p_r)/c,
\]

\[
R_{B p_w}=-qp_r/c^2,\quad
R_{B p_r}=qp_w/c^2,\quad
R_{B p_i}=R_{B p_o}=0,\quad
R_{Bq}=-p_w(p_w-p_r)/c^2.
\]

At the ratio level, high write prices strengthen the benefit of stable-prefix
reclassification and high read prices weaken it. At the threshold level,
the additional curvature term can reverse some mixed signs. In the standard
discount regime, L_Bpi and L_Bpo are positive at a positive-density root:
larger setup expense increases U_* and attenuates B's negative threshold shift.
The exact L_Bpw, L_Bpr and L_Bq follow the master mixed formula; none should
be inferred solely from the ratio partial.

When switching a real cache TTL tier, use
`dL=L_pw*dpw+L_q*dq+...`. A write-price surcharge and a hit improvement can
reinforce or oppose one another according to q_w. If a stylized independent
gap CDF gives q(tau)=P(gap<=tau), its continuous TTL effect is L_q*f_gap(tau)
with prices fixed; real discrete TTL choices require the complete invoice
comparison and provider eligibility/refresh rules.

## 7. Full four-price marked correction

Let t(L)=E[G_T] be the crossing-increment mean and theta*G the retained tail
appended after the ordinary request. The study's full long-run rate is

\[
j(L)=p_i e+p_o o+(p_w-c\theta+\kappa)g+cS
 +\frac{A+cM(L)+d\theta t(L)}{U(L)},\qquad
d=q(p_i-p_w).
\]

e is ordinary uncached suffix size, o ordinary output mean. This is exactly
the contract's ledger under independent hits/marks and full reconstruction.
No tail is cached retroactively on its generating request. The joint law of
growth/tail is part of the model; proportional theta is a declared sensitivity,
not measured by community total-input increments.

At smooth density points define

\[
\chi(L)=t(L)-t'(L)U(L)/u(L).
\]

Then

\[
j'(L)=\frac{u(L)}{U(L)^2}\Phi(L),\qquad
\boxed{\Phi(L)=cD(L)-A-d\theta\chi(L).}
\]

For a general law, chi can be irregular and need not be monotone/nonnegative;
the core's universal single crossing cannot simply be declared for this marked
ledger. For exponential growth,

\[
t=g(2-e^{-L/g}),\qquad
\chi=g[2-(2+L/g)e^{-L/g}],\qquad
\chi'=e^{-L/g}(1+L/g)>0.
\]

If p_i<=p_w, then d<=0 and
`Phi_L=cU-d*theta*chi'>0`, proving a unique positive marked crossing when
A>0. Set W_*=Phi_L at the root. All the following derivatives include the
marked numerator and actual root shift:

\[
\boxed{L_{p_j}
=\frac{a_j+d_{p_j}\theta\chi_*-v_jD_*}{W_*},\qquad
d_p=(q,-q,0,0).}
\]

Thus input and summary-output prices still raise the optimum in this marked
exponential regime. The write-price sign is
`qV-q*theta*chi_*-(1-q)D_*`; the read-price sign is `q(B-D_*)`.
Their phase boundaries depend on the actual marked crossing and not only A/c.
Recompute them rather than transplanting the core crossover q_w/q_r.

### 7.1 Theta, stable material and summary derivatives

\[
\boxed{L_\theta=d\chi_*/W_*\le0\quad(p_i\le p_w).}
\]

More of a fixed aggregate increment appended after the call makes early
compaction's avoided tail cache-write economically more valuable. At q=0 or
p_i=p_w there is no marked policy effect. This is a timing intervention at
fixed growth/output billing, not the effect of generating more output.

At fixed S, `L_B=-q(p_w-p_r)/W_*` retains its nonpositive sign. Adding volatile
material or enlarging summary while preserving the other material gives
`H_V=1+[(1-q)p_i+q*p_w]/W_*` and
`H_C=1+[p_o+(1-q)p_i+q*p_w]/W_*`.
The ordinary suffix e and output mean o only change the threshold-independent
baseline when all other laws are held fixed.

### 7.2 Better hits can reverse the marked threshold direction

Differentiate Phi with respect to q and use the root equation. Exactly,

\[
\boxed{\operatorname{sign}L_q
=\operatorname{sign}\{N_q+p_w(p_i-p_w)\theta\chi_*\}.}
\]

For the usual p_w>p_i>=p_r, the marked q-to-gap effect is negative iff

\[
\theta\chi_* > N_q/[p_w(p_w-p_i)].
\]

The left side is a terminal-tail scale; the right side is a setup/cache
amortization scale. The core has no reversal as q varies, but this term depends
on the moving marked root, so the full marked response can have a phase
transition. If p_i=p_w, the terminal correction disappears and the core
direction applies. If S is large relative to this tail scale and the setup
expense is large, the core direction is more resistant to reversal.

### 7.3 Invoice direction is not threshold direction

Let P_n be the prefix eligible for an ordinary hit before its fresh input and
P_c the prefix eligible for the terminal compactor. Their expected total
amounts per cycle are

\[
P_{\rm normal}=SU+M-\theta(gU-t)-V,\qquad
P_{\rm compact}=S+gU-\theta t.
\]

These are nonnegative because they are actual available-prefix lengths;
the first normal reset prefix is B=S-V. Direct differentiation of the full
rate gives the exact prefix-saving identity

\[
\boxed{j_q(L)=
-\frac{(p_w-p_r)P_{\rm normal}
       +(p_i-p_r)P_{\rm compact}}{U}.}
\]

Hence for p_w>=p_r and p_i>=p_r, increasing q never raises the invoice at any
fixed L. The optimized invoice is also nonincreasing by comparison/envelope.
Its optimal threshold may go either way as proved above. Cheaper operation
and a longer/shorter economically chosen context are not contradictory.

At fixed L, `j_theta=-c*g+d*t/U`, negative when p_i<=p_w. This means a larger
post-call share at fixed total growth and billed output is cheaper under that
timing intervention; it does not imply that more generated output is free.

## 8. Price geometry and optimal expected-usage gradients

### 8.1 Projective policy geometry

At fixed workload/q, A and c are linear in p. For any alpha>0,
`R(alpha*p)=R(p)`, so all core thresholds are unchanged. The full marked rate
also scales by alpha and its root is unchanged because A,c,d all scale.
Every actual finite invoice has the same homogeneity when all non-token fees
are either zero or scaled with the rates and all feasible laws/policies are
unchanged. A separately fixed USD fee breaks this token-price homogeneity.

Normalizing one positive price removes one irrelevant degree of freedom.
For a chosen gap x, the core root's price boundary is the homogeneous plane

\[
p\cdot[a-D(x)v]=0.
\]

Atomic plateau switches occur on these planes at renewal support points.
For finite candidate policies with price-invariant expected usage t_h, equality
of their invoices is `p*(t_h-t_k)=0`; their optimal-price regions form a
polyhedral cone arrangement. This is why relative-price sign regions are a
better first visualization than arbitrary four-dimensional price sweeps.

### 8.2 Exact envelope statement beyond the renewal model

For any fixed ordinary horizon and price-independent conditional workload
law/admissible policy class, let t_pi be its expected disjoint usage. Then

\[
V(p)=\inf_\pi p\cdot t_\pi.
\]

V is concave, coordinatewise nondecreasing and homogeneous of degree one.
**Proof:** an infimum of linear functions is concave; each function is
nondecreasing because usage is nonnegative; scaling factors out of the infimum.
This holds for history-dependent nonanticipative policies as well as a
threshold restriction. It does not require a smooth objective or renewal law.

With a separately fixed policy-dependent non-token fee f_pi, replace the
objective by `inf_pi[p*t_pi+f_pi]`. Concavity, monotonicity and usage
supergradients still hold for this affine envelope. Degree-one homogeneity
and Euler's all-token expenditure identity need not; the unscaled fee creates
a separate price scale and can change the policy after a uniform token-rate cut.

At a differentiability point with an attained optimizer,

\[
\boxed{\nabla_p V=t_{\pi_*}.}
\]

At a tie, the active optimal usage vectors are supergradients of the concave
value. For a finite policy set the directional derivative is
`min_(active pi) delta_p*t_pi`; a particular tied policy's usage is not
automatically the unique derivative. General infinite policy classes need the
appropriate envelope/compactness/integrability assumptions; the finite
statement is immediate from the lower envelope. Primary general envelope
reference: [Milgrom and Segal, Econometrica 2002](https://doi.org/10.1111/1468-0262.00296).

If differentiable, Euler gives `p*grad V=V`: optimal invoice elasticities
`p_j*t_j/V` are nonnegative expenditure shares summing to one. Contrast this
with threshold elasticities, which can be negative and sum to zero.

### 8.3 Explicit full marked usage vector per ordinary action

Let `R_h=S+M/U` and `z=t/U`. Expanding the full rate in the four prices yields

\[
\bar I=e+(1-q)g+[K+(1-q)S]/U+q\theta z,
\]

\[
\bar W=[1-(1-q)\theta]g+(1-q)R_h+qV/U-q\theta z,
\]

\[
\bar R=q(1-\theta)g+qR_h+qB/U,\qquad
\bar O=o+C/U.
\]

The negative write correction removes the last tail's unperformed ordinary
cache write; it does not represent negative actual usage. Since t<=gU and
0<=theta<=1, the whole write count is nonnegative. The sum of input categories
is `e+(2-theta)g+R_h+(K+S)/U`, verifying input conservation for the declared
macro ledger. At a smooth attained optimum this vector is the price gradient
of the optimized rate, without an additional threshold-motion term because
the stationary first-order effect is zero.

## 9. Near-optimum regret and curvature

At a positive-density core interior root,

\[
\boxed{j_{LL}(L_*)=c u_*/U_*>0.}
\]

For a small threshold error delta_L,
`j(L_*+delta_L)-j(L_*)=0.5*(c*u_*/U_*)*delta_L^2+o(delta_L^2)`.
Thus a sensitive argmin need not imply a large invoice penalty: root movement
and the objective's flatness are separate quantities.

Put alpha=a-R*v. Under a small price change delta_p,
`delta_L=alpha*delta_p/(cU_*)+o(norm(delta_p))`. If the previous optimal
threshold is kept rather than adapted, its regret at the new prices is

\[
\boxed{\mathrm{regret}
=\frac{u_*}{2cU_*^3}(\alpha\cdot\delta p)^2
                          +o(\|\delta p\|^2).}
\]

Radial price changes have alpha*p=A-Rc=0 and no selection regret. For one
smooth scalar control and a price-linear rate, the optimized value Hessian is

\[
\boxed{\nabla_p^2 V
=-\frac{u_*}{cU_*^3}\alpha\alpha^\top.}
\]

This is rank-one negative semidefinite, consistent with concavity. Mixed
entries may be positive when alpha components have opposite signs; concavity
is a quadratic-form statement, not a claim that every cross partial is negative.

For the marked root replace its curvature by
`j_LL=(u_*/U_*^2)*Phi_L`. Its mixed price slope is
`j_Lpj=(u_*/U_*^2)[v_j D-a_j-d_pj*theta*chi]`. The general scalar-control
envelope identity `Hess_p V=-j_pL*j_Lp/j_LL` and regret
`0.5*j_LL*(delta_L)^2` still apply when this root is a strict attained minimum
and the law/price-linear ledger remains fixed. There is no need to pretend
the marked optimum equals the core root.

### Atomic and constrained optima

For an atomic renewal point x of mass m, the core's exact rate jump is

\[
j(x+)-j(x)=\frac{m}{U_-(U_-+m)}[cD(x)-A].
\]

That expression is price-linear. Inside an optimal plateau, no threshold
retuning changes the invoice; at its price-plane boundary a competing plateau
can become strictly preferable with linear loss. Quadratic smooth curvature
is inappropriate there. The canonical D^{-1} point can move continuously
inside a plateau even while the optimal invoice region is unchanged.

For a finite policy/threshold set, a currently optimal policy remains optimal
for price changes satisfying all exact inequalities
`delta_p*(t_other-t_current)>=-current_margin`. These give a robust price
region without estimating a fictitious derivative. A hard capacity boundary
can pin H even when the unconstrained root moves; report one-sided KKT/grid
comparisons and actual regret instead of the interior derivative formula.

## 10. Finite horizons, q-dependent laws and conditional-history limits

The long-run root is not the exact finite ordinary-action invoice. Initial
cache warmth, first reconstruction, residual last-cycle carries and absent
terminal compactor change threshold-sensitive usage. The envelope geometry and
usage-gradient statement survive at finite N if workload kernels remain price-
independent; the core sign formulas need not. Finite price boundaries are
computed from finite disjoint usage, not by billing an imaginary final reset.

If price changes cause model routing, summary quality, task decisions or growth
to change, total sensitivity includes the conditional-law derivative. The
simple price envelope assumes those kernels are fixed, although the chosen
control is allowed to adapt. An optimal policy's response to prices is
already handled by the envelope; a changed environment is a separate effect.

Likewise, q correlated with growth, context length, output duration, phase or
restoration makes scalar c/kappa averaging questionable. The relevant rewards
contain `E[hit*eligible_prefix]`. A token-weighted read fraction is not an
independent-hit probability. Price or B changes can alter eligibility and
therefore q itself; use a total conditional-state calculation or a justified
policy-independent conditional carry reward before exporting the sign table.

Under general history kernels, a fixed policy's total derivative consists of
direct invoice changes plus occupation/transition effects. The exact Bellman
or finite-policy usage model is the right continuation when first-use facts,
versions, cache ages or persistent phases matter. Same-length opposite-action
states in the general-control note already prove there is no universal scalar
price-threshold theorem for every such environment.

## 11. Discriminating community-driven investigations

The theory specifies what should be investigated rather than demanding broad
arbitrary sweeps:

| Structural prediction | Targeted contrast | Observable explanation |
| --- | --- | --- |
| Common scaling leaves policy unchanged | Multiply all four rates together | Every same-policy invoice scales exactly |
| Write-price effect flips at q_w | Choose q below/above the analytic boundary | Carry-write exposure versus mandatory reset writes |
| Read-price reversal needs large B and cheap setup | Compare identified B or within-S B sensitivity on both sides of q_r | Stable-prefix compactor reads versus ordinary history reads |
| Marked theta lowers gap for p_i<p_w | Increase retained-tail timing share holding growth/output billing fixed | Last tail avoids ordinary write and pays compactor input |
| Full q invoice always decreases under standard discounts | Compare matched q interventions with the same ordinary marks | Prefix-saving identity, not a generic hit-rate slogan |
| Marked q threshold can reverse | Test theta*chi against the analytic scale boundary | Tail discount competes with carry savings |
| Larger summary preserving material raises H more than one-for-one | Increase C and S together | Generated output fee plus reset floor and rewrite |
| Output billing alone does not move H | Increase o without altering retained G | Per-action baseline expense, distinct from summary output |
| Near-optimal policy can tolerate large point shifts | Evaluate regret, not only argmin | Curvature/plateau and expenditure-direction geometry |

Reuse pinned community growth and aligned ordinary output marks; do not count
old outputs as additional growth a second time. Treat q,B,theta as declared
uncertainty/mechanism interventions unless jointly identified by data. The
published S/C medians are scenario anchors, not a joint fitted distribution.
Start with the predicted boundary contrast and explain unexpected behavior via
marked tails, finite horizon, serial dependence or conditional cache-state
changes. Simulation supplies the size and importance of deviations, not the
proof of the structural sign regime.

## 12. Primary external grounding

1. Paul Milgrom and Ilya Segal. *Envelope Theorems for Arbitrary Choice Sets*.
   Econometrica 70(2), 583-601, 2002.
   [DOI](https://doi.org/10.1111/1468-0262.00296),
   [author full text](https://milgrom.people.stanford.edu/wp-content/uploads/2002/03/Envelope-Theorems.pdf).
   Peer-reviewed primary envelope foundation. Our finite-policy concavity and
   usage-supergradient claims also have the self-contained proofs above.
2. Stephen Boyd and Lieven Vandenberghe. *Convex Optimization*, 2004.
   [Author-hosted book](https://www.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf).
   Authoritative background for infima of affine functions and sensitivity;
   no differentiability at price-policy ties is assumed from convexity alone.
3. Anthropic. *Prompt caching*.
   [Official documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
   consulted 2026-10-06. Writes, reads, TTL tiers, eligible prefix lengths and
   refresh rules are distinct mechanisms. Rates here remain symbolic or the
   project's declared illustrative values, not a copied current model quote.
4. Recent cache-aware compression work is a frontier signal for nonconstant
   cache behavior:
   [Cache-Aware Prompt Compression: A Two-Tier Cost Model for LLM API Caching](https://arxiv.org/abs/2607.15516),
   Yan Song, submitted 2026-07-17, preprint, not peer-reviewed. Its official
   abstract reports model/config-
   specific cache measurements; they do not identify this project's q and are
   not used as parameter values or theorem assumptions here.
5. Internal mathematical dependencies: renewal single-crossing, Stieltjes jumps,
   marked-tail accounting and regeneration conditions are proved in the linked
   analytic-control/closed-form notes. Community provenance and limitations are
   in [renewal-community-calibration.md](renewal-community-calibration.md).

The contribution is a transparent map from rates/material/cache mechanisms to
control directions, switching surfaces, usage gradients and retuning regret.
It is not a novelty claim for envelope theory and not a claim that one synthetic
four-price schedule applies universally.

### Reproducible algebra checks

Executed 2026-10-06 in the root uv/SymPy environment, without adding dependencies
or a test suite: the differences between the symbolic derivatives of A/c and
the displayed q, write, read, q-by-input, q-by-output, B-by-write and B-by-read
expressions all simplified to zero. The full marked rate's q derivative plus
the two-prefix-saving expression also simplified to zero. Reproduce by declaring
symbols `(pi,pw,pr,po,q,S,B,K,C)`, setting `V=S-B`, c and A as in Section 2,
and applying `sympy.simplify(sympy.diff(A/c,parameter)-displayed_expression)`;
mixed identities use both parameter arguments. For the last identity, declare
`(g,U,M,t,theta,e,o)` independently and use the rate and prefix expressions in
Section 7. These check transcription/algebra; the conditional-law and reset
assumptions remain substantive model premises.
