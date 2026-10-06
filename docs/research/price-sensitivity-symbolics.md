# Four-price threshold sensitivity: directions, paths, and regime changes

Recorded 2026-10-06. This extends the analytic renewal model, rather than
repricing a toy threshold simulation. Maintained source:
`src/context_compaction_lab/sensitivity_symbolics.py`; executable derivation:
`experiments/price_sensitivity_derivation.py`. Prior assumptions and exact laws
are in [renewal-analytic-control.md](renewal-analytic-control.md) and
[renewal-closed-forms.md](renewal-closed-forms.md).

## 1. Question and scope

A price increase can raise the best achievable bill while moving its optimal
threshold in either direction. Similarly, better caching can lower the bill
without forcing a universal direction for the preferred threshold. To predict
the threshold, specify **which price or mechanism changes and which other
parameters stay fixed**.

Fix an iid regenerative growth law with mean g>0. Let U(L),D(L) be its renewal
duration and integrated duration. The law is independent of prices and of the
cache-hit probability q. Prices p_i,p_w,p_r,p_o are the four disjoint per-token
rates; q is homogeneous cache-hit probability; S is full reset context; B its
eligible stable prefix; C generated summary already inside S; K uncached
compactor-instruction tokens. Domain: positive prices, 0<=q<=1,
S>=B+C>=0, K>=0. Feasible controllers are price-independent.

The core optimum is `H*=S+D^{-1}(R)`, where

\[
c=(1-q)p_w+qp_r,\quad\kappa=(1-q)p_i+qp_r,
\]
\[
A=p_iK+p_oC+q(p_w-p_r)(S-B)+\kappa S.
\]

The key simplifying representation is

\[
\boxed{A=p_i[K+(1-q)S]+p_oC+qp_w(S-B)+qp_rB.}
\]

It makes every coefficient a physical nonnegative token quantity and exposes
the cancellation of the volatile reset's read price. Let R=A/c and U*=U(L*).
For a parameter x that does not change the growth law,

\[
\boxed{\partial_xH_* = \partial_x S + \frac{\partial_x R}{U_*}.}
\]

This first-order inversion uses D'=U>0, not a smooth microscopic cost-curve
derivative. For arithmetic laws it describes the canonical crossing within
the minimizing cell away from a renewal node; one-sided derivatives apply at
nodes. It does not turn an entire optimal threshold plateau into one uniquely
identified economic choice.

## 2. Exact price and cache-hit sign numerators

For a fixed-reset price change, write `R_x=N_x/c²`. SymPy derives and verifies
the following exact numerators:

| Parameter x | N_x | Implication |
| --- | --- | --- |
| p_i | c[K+(1-q)S] | Nonnegative; input price raises the core threshold through compaction instructions and cold old-context processing |
| p_o | cC | Nonnegative; output price raises threshold only through generated summary C in this model |
| p_w | qp_r(qS-B)-(1-q)[p_i(K+(1-q)S)+p_oC] | Can reverse with q and stable-prefix/reset composition |
| p_r | q[p_w(B-qS)-p_i(K+(1-q)S)-p_oC] | Usually negative, but can be positive for a sufficiently stable reset at low q |
| q | (p_w-p_r)[p_w(S-B)+p_iK+p_oC]+p_rS(p_w-p_i) | Independent of q itself; its sign determines the whole core q-direction |

Ordinary output volume and ordinary uncached input that affect only the
threshold-independent baseline do not change the optimizer. If repricing
changes retained growth, generated-summary size, or future task behavior,
those effects require a total derivative through that changed law, not the
partials in this table.

### Cache-write price: cold carry versus reset amortization

At q=0 the write numerator is negative: write price is the carrying price of
every uncached history request, so increasing it favors shorter cycles. At
q=1 it becomes `p_r(S-B)`: when writes occur mainly at a reset, a higher
write price favors amortizing the mutable reset over longer cycles.

If V=S-B>0, the unique core sign crossing lies in (0,1). Let

\[
a_w=S(p_r-p_i),\quad b_w=2p_iS+p_iK+p_oC-p_rB,
\quad e_w=p_i(S+K)+p_oC.
\]

Then the stable algebraic representation is

\[
\boxed{q_w=\frac{2e_w}{b_w+\sqrt{b_w^2+4a_we_w}}.}
\]

Below q_w a write-price increase lowers H; above it, raises H. The endpoint
signs and quadratic degree imply a unique crossing in the feasible interval;
if the quadratic coefficient vanishes this expression has the correct linear
limit. Under the common ordering `p_w>=p_i>=p_r`, its numerator is strictly
increasing in q. At the root q_w>B/S: an extremely stable reset pushes this
write-up regime close to fully warm caching.

### Cache-read price: a real positive-direction regime

If p_w<=p_i, the read numerator cannot be positive in the feasible domain.
If p_w>p_i, define

\[
\boxed{q_r=\frac{p_wB-p_i(K+S)-p_oC}{S(p_w-p_i)}.}
\]

A positive regime exists only if the numerator is positive. In that case the
read-price effect is positive for 0<q<q_r and negative for q>q_r. It means
cached reads have increased the reset/crossing burden more strongly relative
to carrying, not that increasing a billable price improves the invoice.

The reset constraint B<=S-C gives a useful necessary feasibility condition:

\[
(p_w-p_i)S>p_iK+(p_w+p_o)C.
\]

Thus expensive or large generated summaries can eliminate the entire read-up
regime even if most reset instructions are stable. Increasing B expands the
regime; increasing K, C, or the summary-output price contracts it.

For illustration only, the declared relative vector `(3,3.75,0.30,15)` gives
the limiting summary-share requirement `C/S<4%` even with K=0 and maximally
stable B. These are algebraic ratios, not claims about current provider prices
or measured stable-prefix shares.

### Cache-hit probability

Under `p_w>=p_i>=p_r`, every term in N_q is nonnegative, so better hit
probability raises the core preferred gap. This is not universal: if uncached
compactor input is sufficiently more expensive than writes, higher q can
reduce reset/crossing cost faster than carry cost and lower the gap. For
example `p_i=10,p_w=3,p_r=1,S=B=100,K=C=0` has N_q=-700.

### Radial consistency constrains the regimes

Common repricing leaves R unchanged. Consequently

\[
\boxed{\sum_{j\in\{i,w,r,o\}}p_j\partial_{p_j}H_*=0.}
\]

Since the input/output price directions are nonnegative, write and read
directions cannot both be strictly positive. When both read-up and write-up
cache regimes exist, they are separated by a region in which both carrying
price increases lower H. This is a coherence condition on regime maps, not
another arbitrary one-dimensional price example.

The write numerator does not contain p_w itself, and the read numerator does
not contain p_r itself. Consequently, at a fixed mechanism and with all other
prices held fixed, each core carrying-price axis has one consistent direction
throughout its positive range. Its sign regimes change with q, other prices,
or reset composition, not merely by raising that same price through arbitrary
levels. The marked model below need not retain that simplification because
W is evaluated at a price-dependent optimum.

## 3. Parameter paths: two meanings of “more stable context”

The mechanism has no single derivative with respect to an ambiguous phrase.
Core paths are:

| Intervention | What stays fixed? | Total threshold derivative |
| --- | --- | --- |
| Improve survival of existing B | S,C,K fixed; cold mutable text becomes an eligible stable prefix | `-q(p_w-p_r)/(cU*)` |
| Add new stable tokens | dS=dB; volatile size unchanged | `1+kappa/(cU*)` |
| More generated summary at fixed S | Summary replaces other reset payload; composition/contract must allow it | `p_o/(cU*)` |
| Add generated summary tokens | dS=dC; B fixed | `1+[p_o+(1-q)p_i+qp_w]/(cU*)` |
| Add compactor instruction K | S,B,C fixed | `p_i/(cU*)` |

With reads cheaper than writes, improving survival permits earlier compaction,
whereas adding a new stable block raises the physical threshold. Summary
generation affects both generated-output price and reset residency when S
changes. Treating C and S as independent without describing the intervention
can therefore omit most of the derivative.

At a composition boundary, only feasible one-sided paths are allowed. For
example B cannot increase at fixed S if it already equals S-C.

## 4. Mixed interactions: denominator and renewal curvature compete

Even R=A/c has informative price/cache interactions:

\[
R_{p_iq}=\frac{K(p_w-p_r)-Sp_r}{c^2},\quad
R_{p_oq}=\frac{C(p_w-p_r)}{c^2},
\]
\[
R_{Sq}=\frac{p_w^2-p_ip_r}{c^2},\quad
R_{Bq}=-\frac{p_w(p_w-p_r)}{c^2}.
\]

All four are checked as exact mixed derivatives, not inferred from a grid.
Better caching amplifies summary-output price sensitivity in R when reads
are cheaper, but its interaction with input price can reverse depending on
K relative to S.

For fixed growth law and smooth renewal density u*=U'(L*), the actual
threshold's mixed derivative is

\[
\boxed{H_{xy}=\frac{R_{xy}}{U_*}
-\frac{u_*R_xR_y}{U_*^3}.}
\]

The second term is the concavity of inverse D. It prevents casually extending
a sign of R_xy to H_xy. In particular R_{p_i p_o}=0 but

\[
H_{p_i p_o}=-\frac{u_*C[K+(1-q)S]}{c^2U_*^3}\le0.
\]

Similarly R_{CS}=0 while H_{CS}<0 at a continuous strict optimum. Input and
summary price effects can therefore be jointly diminishing even though A is
linear in both. The executable verifies the general chain formula against
the explicit exponential inverse `L=sqrt(g²+2gR)-g`.

## 5. Full marked-tail correction changes price regimes

Let retained post-call growth be `Z=theta G`, 0<=theta<=1, and let
`zeta(L)=E[G_T]`. Define the **already theta-weighted** quantity

\[
\boxed{W(L)=\theta\{\zeta-U\zeta'/u\}.}
\]

With d=q(p_i-p_w), the marked stationarity equation is

\[
f(L)=cD(L)-A-dW(L)=0.
\]

At a selected nondegenerate strict minimum require
`f_L=cU-dW'>0`. For a price/mechanism parameter x that leaves D,W unchanged
at fixed L,

\[
\boxed{H_x=S_x+
\frac{A_x+d_xW-c_xD}{cU-dW'}.}
\]

If x changes the law or theta, add the explicit partials `d W_x-c D_x` to
the numerator. For exponential growth,

\[
W=\theta\{2g-(2g+L)e^{-L/g}\},\quad
f_L=(1+L/g)\{c-d\theta e^{-L/g}\}.
\]

W>=0, and the denominator is positive under the common p_i<=p_w ordering.
Multiplying the on-root numerator by c exposes these changes to the core
regime numerators:

\[
\boxed{\widetilde N_w=N_w-q\kappa W,\quad
\widetilde N_r=N_r-qdW,\quad
\widetilde N_q=N_q+p_w(p_i-p_w)W.}
\]

All three are exact symbolic identities with theta inside W. Omitting theta
would mix a terminal mark model with an all-growth-tail correction.

At q=1 the write direction becomes

\[
\widetilde N_w=p_r\{S-B-W\}.
\]

Thus even fully warm caching does not force a write-price increase to raise
the threshold: a nearly fully stable reset with mutable volume below W
reverses the sign. The fully warm read numerator is

\[
\widetilde N_r=-p_w(S-B)-p_iK-p_oC+(p_w-p_i)W.
\]

The terminal balance can also create a read-up regime or reverse the core
q-direction. Stable survival and added-token paths retain the signs above,
with `cU*` replaced by f_L. Common radial repricing still leaves the full
marked optimum unchanged; the script checks its Euler identity on f=0.

These are local branch sensitivities. A general marked phase law may have
several stationary branches; this formula alone does not prove their global
ordering or uniqueness. The exponential model has the earlier verified
single-crossing result under its assumptions.

## 6. Repricing basis, positivity, and the optimized value

The consistent ordinary baseline for proportional pre/post timing is

\[
b=p_i I+p_o E[O]+p_w g-c\theta g.
\]

This differs from the all-post-growth helper when theta is changed. Changing
only a terminal correction while keeping an all-post baseline fixed is a
diagnostic sensitivity, not a physical reclassification of all input timing.
Billed output E[O] need not equal retained post-call growth theta g.

For fixed L the complete marked rate is exactly
`j=sum_j p_j V_j`, with four expected billed-token rates:

\[
V_i=I+(1-q)g+[K+(1-q)S+q\theta\zeta]/U,
\]
\[
V_w=[1-(1-q)\theta]g+(1-q)S
+[q(S-B)+(1-q)M-q\theta\zeta]/U,
\]
\[
V_r=q\{(1-\theta)g+S+(B+M)/U\},\quad V_o=E[O]+C/U.
\]

The module independently verifies this identity and every price derivative.
There is no new symbolic or numerical pricing category that double-counts a
file reload. The fixed-gap price Hessian is zero.

The only apparently subtractive token coefficient V_w can be rewritten as

\[
V_w=(1-q)\{(1-\theta)g+S+M/U\}
+q\{g+(S-B-\theta\zeta)/U\}.
\]

Wald's identity and nonnegative stopped increments give `0<=zeta<=gU`, so
this is nonnegative; all other coefficients are manifestly nonnegative.
Thus raising any price cannot lower a fixed controller's bill or the minimum
over a fixed feasible controller family, regardless of threshold direction.

### Better caching lowers value, even when its threshold moves either way

The exact fixed-L cost improvement between q=0 and q=1 is

\[
(p_i-p_r)P_c+(p_w-p_r)P_n,
\]

where

\[
P_c=g+(S-\theta\zeta)/U,
\quad P_n=S-\theta g+(M+\theta\zeta-(S-B))/U.
\]

Both matching-prefix rates are nonnegative. To see the less immediate second
one, pathwise accumulated pre-action area includes the last pre-crossing
partial sum. Hence `M>=E[Y_(T-1)]=gU-zeta>=0`. Together with U>=1 and
theta<=1 this proves P_n>=0. Therefore when reads are no more expensive than
input and writes, increasing q decreases the fixed-L bill. The minimum over
L is also nonincreasing. Since the fixed-L expression is affine in q, that
minimum is concave in q as well. No universal direction for H_q follows.

### Envelope gradient and curvature

For a unique smooth interior minimum L*(p), the envelope gradient is the
billed basis evaluated at that minimum:

\[
\boxed{\partial_{p_j}j_*(p)=V_j(L_*(p)).}
\]

Fixed-policy price linearity and differentiation of the stationary equation
give

\[
\boxed{\nabla_p^2j_*=-
\frac{j_{pL}j_{Lp}}{j_{LL}}.}
\]

It is negative semidefinite and rank at most one for a single smooth threshold
decision. This is consistent with the general concavity of the lower envelope
of linear prices. At ties or exact threshold plateaus, use active-policy
supergradients instead of pretending the value has this smooth Hessian.
Price homogeneity also gives `sum_j p_j V_j=j*`, while the optimizer itself
has radial derivative zero. Joint price/q or model-size curvature is not
automatically covered by the price-only concavity theorem.

## 7. Executed sign certificates and artifacts

The script uses exact rational algebraic cases, not workload simulations or
current-provider claims. For the declared relative price vector
`(3,15/4,3/10,15)`:

* `S=100,B=0,C=10,K=1`: write-direction crossover is exactly
  `(251-sqrt(8641))/180`, approximately 0.87801678. Its sign numerator is
  -144 at q=1/2 and +27.843 at q=0.99.
* `S=100,B=95,C=1,K=1`: the read-direction crossover is exactly 51/100.
  Its numerator is +123/40 at q=0.1 and -1053/40 at q=0.9.
* `q=1,S=100,B=99,C=1,K=1`, exponential g=1 and theta=1: the corrected
  analytic root is 17.27566697 rather than the core 17.54723699. Effective
  W is 1.999999394; write direction changes from +0.3 to -0.299999818.

These validate reversals that a one-direction narrative would miss. The
empirical calibrated phase study is a separate root-owned task; these values
do not estimate its file, summary, or stable-prefix distribution.

```powershell
uv run python experiments/price_sensitivity_derivation.py
uv run ruff check src/context_compaction_lab/sensitivity_symbolics.py experiments/price_sensitivity_derivation.py
```

The executable checks original-versus-cancelled A, every sign numerator,
cache-hit crossovers, radial invariance for core and marked models, four mixed
ratio interactions, explicit exponential threshold gradients, the input/output
mixed threshold derivative, full billed-basis identity, basis positivity
decomposition, fixed-gap price Hessian, and cache-gain decomposition. It
persists exact formulas and sign certificates under
`.cache/price-sensitivity/symbolic-results.json`. No new large test suite,
Monte Carlo price sweep, dependency, or existing API modification is used.

The value of this analysis is a reusable sensitivity map: one ledger ratio
explains the core directions; a marked terminal balance locates where they
reverse; mechanism paths prevent conflating survival with added context; and
the billed vector distinguishes an optimizer movement from an invoice
improvement. It is a conditional analytic model with checkable regimes, not
a universal claim that one price or more caching must always favor one h.
