# Analytic renewal control for compulsory full-context reconstruction

Recorded 2026-10-06. This note develops a distribution-class result and useful
extensions, rather than choosing an invented Gamma/lognormal growth law and
optimizing a simulation curve. Its dominant-case assumption is that a project
requires a fixed, or narrowly distributed, reconstructed full working context.
The general joint-law control model remains in
[general-stochastic-control-theory.md](general-stochastic-control-theory.md).
The first-use model remains in
[mandatory-reload-theory.md](mandatory-reload-theory.md). Those models locate
the boundary of the renewal reduction; they are not replaced by it.

## 1. Main result and why it is useful

For fixed restored full context S, iid nonnegative ordinary growth G with
finite mean g>0, homogeneous history-carry price c>0, affine old-context
compactor price kappa*X, and fixed incremental reset invoice F, define gap
L=H-S>0. Let the renewal measure be

\[
\mathcal U(dx)=\sum_{n\ge0}\Pr(Y_n\in dx),\quad
Y_0=0,\quad Y_n=\sum_{j=1}^nG_j,
\]

\[
U(L)=\mathcal U([0,L)),\quad
M(L)=\int_{[0,L)}x\,\mathcal U(dx),\quad
D(L)=\int_0^L U(t)dt.
\]

Set A=F+kappa*S. The long-run invoice per ordinary action is

\[
\boxed{j(L)=b+cS+\kappa g+\frac{A+cM(L)}{U(L)}.}
\]

For a renewal density u away from zero,

\[
\boxed{j'(L)=\frac{u(L)}{U(L)^2}[cD(L)-A].}
\]

D is continuous, strictly increasing and unbounded. If A>0, the unique
canonical optimum gap solves

\[
\boxed{D(L_*)=A/c.}
\]

The invoice decreases before that crossing and increases after it, with
possible exact plateaus when the renewal measure has gaps. Atomic and lattice
laws obey the same signed crossing through their jump formula, proved below.
Thus nonparametric growth laws, mixtures and zero-growth actions fit the same
one-dimensional analytic selection rule. There is no need to search every
threshold with Monte Carlo to establish the objective's shape in this class.

Consequential extensions:

- Growth made more variable in **convex order**, with the same mean, moves the
  canonical optimum to a weakly smaller gap. A higher CV alone is not that order.
- Independent reset variability obeys an exact mixture version of the same
  rule; replacing reset size with its mean is unnecessary and generally wrong.
- Four-price delayed-cache insertion creates a specific terminal-tail
  correction. It can be expressed by a marked renewal convolution, not hidden
  as a universal constant reload fee.
- Finite ordinary-task horizons have an exact ordinary-count renewal recursion;
  a terminal compactor must not be charged. Long-run and finite objectives
  should be distinguished rather than treating a rate theorem as a finite bill.

The result is a mechanism-conditioned theorem, not a theorem for arbitrary
correlated file restoration, arbitrary cache expiry, or every summarizer.

## 2. Assumptions, ledger and cycle timing

### 2.1 Workload and regeneration

1. Every cycle starts with the same reconstructed required working context S.
   Required files/instructions are part of S, not counted again inside G.
   All file prerequisites for the modeled project phase are reconstructed.
2. Ordinary increments G_1,G_2,... are iid, nonnegative, and have mean
   0<g<infinity. Zero growth is allowed. Their law restarts after a reset.
3. A cycle finishes after its crossing ordinary action:
   `T_L=inf{n>=1:Y_n>=L}`. A compact is performed only if another ordinary
   action remains. In a long-run complete cycle, it processes S+Y_T and resets
   the next required context. No repeated-reset-until-small loop is assumed.
4. The complete cycle invoice has the declared form

\[
Q_L=bT_L+c\sum_{n=0}^{T_L-1}(S+Y_n)
                    +\kappa(S+Y_{T_L})+F.
\]

Here c and kappa are nonnegative USD/token, b is nonnegative USD per ordinary
action, and F is a fixed **incremental** reset invoice. The exact ledger may
split F between a reset's generated-output/instruction charge and the first
ordinary prompt's rewrite correction. That allocation is harmless in the
long-run ratio but must be restored for finite endpoints.
5. Complete cycle laws are iid, with independent freshly restarted future
   marks and cache conditions adequate for this ledger. Compaction does not
   automatically establish this; it is an explicit dominant-case model.

b need not be a fabricated price inferred from g. With iid joint marks
`(G_n,B_n)` and integrable ordinary base charge B_n, the expected sum of B_n
up to this predictable stopping time is `E[B_n]*E[T]` by Wald's identity.
Dependence of B_n on the *same action's* growth is allowed. Write b=E[B_n].
Policy-dependent future ordinary outputs or phase transitions generally fall
outside this scalar regeneration model, even though they are allowed by the
general control model.

### 2.2 Stable and volatile reset components

Use `S=B+V`, where B is an explicitly unchanged eligible stable prefix and V
is rewritten mutable reconstructed context. If B is genuinely warm after
reset, the ideal first history input costs `c*B+p_w*V` instead of the baseline
`c*S`. Its incremental rewrite surcharge is

\[
\rho=(p_w-c)V.
\]

If no eligible prefix survives, V=S. Preservation of semantic contents is not
evidence of prefix-cache survival. Set

\[
F=f+\rho,
\]

where f includes actual compactor instruction input, generated summary output
and any state-independent actual extra recovery invoice. Generated summary C
belongs to output inside f; required files and verbatim preserved text belong
to V/B input, not summary output. A recovery model round processing a changing
old context can contribute to kappa or a marked/state-dependent correction;
it is not necessarily a fixed f.

This separates stable-prefix reuse from compulsory file availability without
double counting the reconstructed full-prompt anchor. For example, a stated
65,588-token full prompt is S, not an additional document payload on top of
independently added system/tool/summary components.

## 3. Proof of the renewal invoice and single crossing

### 3.1 Finiteness and zero increments

Because g>0 and G>=0, there exist epsilon>0 and q>0 with P(G>=epsilon)=q.
To cross L requires no more than the time needed to accumulate
ceil(L/epsilon) such successes. Hence T_L is stochastically bounded by a
negative-binomial success time and has finite moments of every integer order,
for each fixed L. No finite second moment of G is required for this statement.

The renewal measure is locally finite. With p_0=P(G=0)<1,

\[
\mathcal U(\{0\})=\sum_{n\ge0}p_0^n=\frac1{1-p_0}.
\]

That atom records repeated ordinary zero-growth actions at the same token
level. It must not be silently replaced by one. It also implies U(L)>=1 for
every L>0, so none of the ratios below has a zero denominator.

### 3.2 Expected length, retained area and crossed context

Nonnegative increments give `{T_L>n}={Y_n<L}`. Therefore

\[
E[T_L]=\sum_{n\ge0}\Pr(Y_n<L)=U(L).
\]

Tonelli's theorem and the same event yield

\[
E\sum_{n=0}^{T_L-1}Y_n
=\sum_{n\ge0}E[Y_n1\{Y_n<L\}]=M(L).
\]

Predictability of `{T_L>=n}` and independence of G_n from its past give

\[
E[Y_{T_L}]
=\sum_{n\ge1}E[G_n1\{T_L>=n\}]
=g E[T_L]=gU(L).
\]

This is the nonnegative stopped-sum form of Wald's identity. The terminal
compactor receives the overshot S+Y_T, not H exactly. Taking expectations in
Q_L and dividing by U(L) proves the boxed rate. Integrability follows from
the displayed expectations: before crossing Y_n<L, so M(L)<=L*U(L).

Renewal reward theory then identifies this ratio with long-run expected USD
per **ordinary action**, not per wall-clock second and not E[Q_L/T_L].
For an actual finite invoice, the last incomplete/terminal cycle is treated
separately in Section 8.

### 3.3 The central identity

Fubini/Tonelli gives

\[
\boxed{D(L)=L U(L)-M(L)
=\int_{[0,L)}(L-x)\,\mathcal U(dx)
=\sum_{n\ge0}E[(L-Y_n)_+].}
\]

U(t) is nondecreasing, locally bounded and at least the positive atom at zero.
Consequently D is continuous and convex, absolutely continuous with
`D'(L)=U(L)` almost everywhere, strictly increasing and unbounded.
At renewal atoms the one-sided derivative differs, but D itself is continuous.

If the renewal measure on (0,infinity) has density u, then
`U'=u` and `M'=L*u` almost everywhere. Differentiating the rate gives

\[
\frac{d}{dL}\frac{A+cM}{U}
=\frac{cL u U-(A+cM)u}{U^2}
=\frac{u}{U^2}(cD-A).
\]

Thus a positive-density interval has exactly the sign asserted. Nonarithmetic
does not by itself imply a density; singular/nonlattice laws require the
measure form rather than an unjustified classical derivative.

### 3.4 Atomic jumps and general-measure monotonicity

Use the strict-before-boundary convention U(L)=measure([0,L)). At a positive
renewal atom x with mass m, increasing L just past x adds m to U and x*m to M.
If U_-=U(x), M_-=M(x), then

\[
\boxed{j(x+)-j(x)
=\frac{m}{U_-(U_-+m)}[cD(x)-A].}
\]

This is an exact algebraic identity. At a continuous singular component, the
bounded-variation quotient rule gives non-atomic increment measure
`dj=(cD-A)/U^2 dU`; at atoms use the displayed jump denominator. On every
compact interval away from zero U is finite and positive, so this quotient
rule is well-defined. Both continuous and atomic changes have the same sign.

Therefore j is nonincreasing up to the unique solution of D(L)=A/c and
nondecreasing thereafter, for **any** nonnegative iid growth law of finite
positive mean. A plateau arises when no new renewal measure is added while
the threshold changes. At an atom where cD=A, crossing that atom is an exact
tie. L_* is a canonical point in the minimizing region, not necessarily the
only threshold with the minimum invoice.

For A<=0 and c>0 there is no positive-gap interior crossing: j is
nondecreasing, and the smallest admissible gap/first plateau is optimal.
For c=0, j=b+kappa*g+A/U(L): when A>0 longer cycles decrease cost and the
infimum is the no-compaction limit; A=0 makes every threshold equivalent in
this ledger. Negative incremental A is possible algebraically but must be
checked against the actual nonnegative full invoice and rewrite convention.

An engineering upper capacity H_max or a minimum allowed gap restricts the
domain. Project the canonical crossing onto that admissible interval/grid,
respecting plateaus and >= trigger ties. Unbounded G means positive capacity
overflow probability even when H<H_max; this theorem does not certify hard
context-window feasibility.

## 4. Exact comparative statics beyond named growth families

### 4.1 Setup price and carry price

Where U is continuous at the optimum, implicit differentiation gives

\[
\frac{dL_*}{dA}=\frac1{cU(L_*)}>0,\qquad
\frac{dL_*}{dc}=-\frac{A}{c^2U(L_*)}<0.
\]

Higher compulsory reconstruction/setup charge supports a larger gap; higher
history-carry charge supports a smaller one. With atoms, D's one-sided inverse
has the corresponding one-sided slopes. This is a mechanism statement for A/c,
not a claim that all provider-rate changes modify only A or c.

For S=B+V and `A=f+(p_w-c)V+kappa*S`, increasing volatile reconstruction V
with B,f fixed changes the absolute optimum by
`dH_*/dV=1+(p_w-c+kappa)/(c*U(L_*))`. If a generated summary component C
also increases f by p_o*C, add p_o in that numerator. At fixed full S,
reclassifying a known eligible portion as genuinely warm stable B decreases
the setup charge: `dH_*/dB=-(p_w-c)/(c*U(L_*))`. Cheaper resets support more
frequent compaction in this class; a stable-prefix improvement need not imply
a larger optimal threshold.

The coefficient kappa contributes `kappa*g` as a constant per ordinary action:
every net ordinary-growth token is eventually processed by one terminal
compactor in complete cycles. Only repeated processing of the fixed reset
context, `kappa*S/U`, affects the threshold optimum. Overshoot is not ignored;
Wald accounts for it. This cancellation explains why treating the crossed
context as exactly H can misrepresent the mechanism.

### 4.2 More-variable growth in convex order lowers the gap

Let G^(1) and G^(2) be nonnegative iid increment laws with the same finite
positive mean, and `G^(1) <=cx G^(2)`: the second law is a mean-preserving
spread, i.e. every integrable convex test function has at least as large an
expectation. Independent sums preserve convex order, hence

\[
Y_n^{(1)}\le_{cx}Y_n^{(2)}.
\]

Since y -> (L-y)_+ is convex,

\[
E[(L-Y_n^{(1)})_+]\le E[(L-Y_n^{(2)})_+].
\]

Summing the nonnegative terms proves

\[
\boxed{D_1(L)\le D_2(L)\quad\hbox{for every }L>0,
\qquad L_{*,2}\le L_{*,1}.}
\]

This is an exact distribution-class comparative result. It does not assert
pointwise ordering of raw renewal U, nor of the entire cost curve, nor that
CV/tail variance alone is a complete convex ordering. Equal mean/CV Gamma and
lognormal laws need not be ordered; their D functions may need direct analytic
evaluation. A mixture's extra mass near zero as well as its large jumps can
drive the effect. The stop-loss representation identifies the relevant object.

Closure of independent sums used in the proof follows directly by conditioning:
for convex phi, both `x -> E[phi(x+G)]` and
`g -> E[phi(Y+g)]` are convex, so replacement of one independent component by a
larger-in-convex-order component preserves the expectation inequality.
Induct on the number of components; no parametric tail theorem is being invoked.

An exact counterexample to a CV-only slogan is informative. Consider two
mean-one laws: law 1 is {0,2} with equal probabilities (CV=1); law 2 is 0.5
with probability 0.9 and 5.5 with probability 0.1 (CV=1.5). For setup ratio
A/c=0.1, their canonical gaps are 0.05 and 0.1 respectively: the higher-CV law
has a **larger** optimum because its renewal atom at zero is smaller. At A/c=5,
the first optimum is 2.25. For the second law, below its first 5.5 jump the
renewal masses at k/2 are 0.9^k, so
`D_2(2)=2+1.35+0.81+0.3645=4.5245`, and its slope on (2,2.5) is
`1+0.9+0.81+0.729+0.6561=4.0951`. Thus its optimum is
`2+(5-4.5245)/4.0951`, about 2.1161, now **smaller** than 2.25.
The D curves cross and the laws are not convex-ordered. This is a closed-form
structural example, not a sampled simulation or a claimed real traffic law.

### 4.3 Mean/moment brackets without choosing a marginal family

Deterministic growth g is smaller in convex order than every law of mean g.
For L=k*g+r, 0<=r<g, its integrated renewal function is

\[
D_{\rm det}(L)=g\frac{k(k+1)}2+(k+1)r
=\frac{L^2}{2g}+\frac L2+\frac{r(g-r)}{2g}.
\]

Hence `D(L)>=D_det(L)>=L^2/(2g)+L/2`.
If m_2=E[G^2]<infinity, Lorden's overshoot inequality and Wald give

\[
\frac Lg\le U(L)\le\frac Lg+\frac{m_2}{g^2}.
\]

The source uses strict crossing; the >= crossing's overshoot is no larger
under the same nonnegative increment path, so the bound remains valid.
Zero increments can be removed to the positive skeleton without changing
the positive-jump overshoot law or m_2/g ratio.

Integrate the upper bound and put B_2=m_2/g^2. For A,c>0,

\[
\boxed{\sqrt{g^2B_2^2+2gA/c}-gB_2
\ \le L_*\le
\sqrt{g^2/4+2gA/c}-g/2.}
\]

The simpler fluid upper bound is sqrt(2gA/c). An additional upper bound is
`L_*<=A/[c*U({0})]`. These are analytical uncertainty brackets from moments
and mechanisms, not confidence intervals or fitted-workload claims.
The deterministic D inversion supplies an even tighter distribution-free
upper canonical gap than its displayed quadratic relaxation.

### 4.4 Growth scale increases the optimal token gap sublinearly

For a fixed nonnegative reference law Z, let G=a*Z with a>0. Then
`U_G(L)=U_Z(L/a)`, `M_G(L)=a*M_Z(L/a)` and
`D_G(L)=a*D_Z(L/a)`. Holding A,c,S fixed,

\[
L_*(a)=a D_Z^{-1}(A/(ca)).
\]

At continuity points, put z=L_*/a and differentiate the implicit equation:

\[
\boxed{\frac{dL_*}{da}=z-\frac{D_Z(z)}{U_Z(z)}
=\frac{M_Z(z)}{U_Z(z)}\ge0.}
\]

The elasticity `a*L_*'/L_*=M_Z(z)/(z*U_Z(z))` belongs to [0,1) and approaches
1/2 in the large-gap regime. Atom points use one-sided slopes. This separates
a genuine scale increase, which raises the optimum gap, from a same-mean
convex-order spread, which lowers it. If the growth law itself changes with
the threshold through model behavior or task phase, this comparative statement
cannot be applied as if a were an exogenous constant.

Primary bound source: [Lorden 1970, Annals of Mathematical Statistics](https://doi.org/10.1214/aoms/1177697092),
[author-hosted record](https://authors.library.caltech.edu/records/8eyxa-q6789).

## 5. Exponential, deterministic and zero-growth specializations

### 5.1 Existing exponential benchmark is a special case

For exponential growth of mean g,

\[
\mathcal U=\delta_0+(1/g)dx,\quad
U=1+L/g,\quad M=L^2/(2g),\quad D=L+L^2/(2g).
\]

Thus

\[
\boxed{H_*=S-g+\sqrt{g^2+2gA/c}.}
\]

Taking c=p_r, kappa=k_1 and
`F=k_0+(p_w-p_r)S` gives exactly analytic.py's exponential benchmark.
No overshoot was dropped: the term kappa*g comes from Wald's actual crossed
context. The fluid square-root `H=S+sqrt(2gA/c)` is its large-gap leading term,
not an equality for random growth.

### 5.2 Deterministic growth has exact threshold plateaus

For G=g almost surely, if `(k-1)g<L<=kg`,

\[
U=k,\quad M=g k(k-1)/2,\quad
j_k=b+cS+\kappa g+\frac Ak+c g\frac{k-1}2.
\]

The next plateau's invoice difference is

\[
j_{k+1}-j_k=cg/2-A/[k(k+1)].
\]

Thus an optimal k satisfies
`c*g*k*(k-1)/2 <= A <= c*g*k*(k+1)/2`, with adjacent ties at equality.
Every gap in that k plateau has the same invoice. Reporting one sharp integer
threshold without the plateau would fabricate precision.

### 5.3 Zero-growth actions can be factored analytically

Let q=P(G>0) and Z have the law of G conditional on G>0. Then positive
renewal locations are repeated by geometric runs of zero-growth ordinary
actions. Their expected multiplicity is 1/q, giving

\[
\mathcal U_G=(1/q)\mathcal U_Z,\qquad D_G=(1/q)D_Z,
\quad g=qE[Z].
\]

The canonical gap solves `D_Z(L_*)=q*A/c`. In the special law G=0 with
probability 1-q and G=z otherwise,

\[
U=k/q,\quad M=z k(k-1)/(2q),\quad
j_k=b+cS+\kappa g+q A/k+c z(k-1)/2.
\]

Zero growth does not mean an ordinary action is unproductive or free; its
ordinary invoice is b and its retained context still incurs c. The objective
holds ordinary actions fixed. It does not discount zero-growth calls out of N.

### Large-gap asymptotics

For nonarithmetic growth with finite m_2, the second-order renewal theorem gives
`U(L)=L/g+beta+o(1)`, beta=m_2/(2g^2). Consequently

\[
D(L)=L^2/(2g)+\beta L+o(L),\qquad
L_*=\sqrt{2gA/c}-\frac{m_2}{2g}+o(1)
\quad(A/c\to\infty).
\]

The leading square-root term knows only the mean; the next correction knows
dispersion through m_2. For exponential growth it is -g. Arithmetic growth
can have oscillating renewal-function corrections; its exact measure/plateau
rule remains valid without pretending a nonarithmetic pointwise asymptotic
applies. Family-specific and stronger integrated asymptotics belong in the
exact-law track rather than being inferred from a short simulation run.

Primary second-order reference:
[Daley 2017, Renewal Function Asymptotics Refined a la Feller](https://doi.org/10.19195/0208-4147.37.2.5),
[journal-hosted full text](https://wuwr.pl/pms/article/download/6907/6553).

Recent frontier signal: [Imomov and Rizaqulov 2026](https://arxiv.org/abs/2608.06392)
studies refined renewal corrections for regularly varying finite-variance tails,
including different local and integrated correction scales. This is a preprint;
only its official abstract/metadata were consulted here, and no unverified
remainder theorem is used in our proofs. It motivates estimating tail-sensitive
renewal remainder before trusting a second-order approximation numerically;
finite variance alone is not a claim of rapid finite-scale convergence.

## 6. Concentrated random reset: an exact extension, not mean substitution

Let each cycle draw a fresh iid reset S and incremental F(S), independent of
future increments, with bounded S and fixed law not depending on H. Work in
the regime H>ess_sup S so every cycle has a positive gap. Conditional growth
may have a law depending on S if its conditional mean remains the same g;
denote its renewal functions by U_S,M_S,D_S. Assume the required expectations
are finite. For the simple independent case these conditional functions are
the same U,M,D evaluated at H-S.

Set

\[
\bar U(H)=E[U_S(H-S)],\quad
\bar W(H)=E[S U_S(H-S)+M_S(H-S)],\quad
\bar A=E[F(S)+\kappa S].
\]

The regenerative invoice rate is

\[
j(H)=b+\kappa g+\frac{\bar A+c\bar W(H)}{\bar U(H)}.
\]

With dominated differentiability and conditional renewal densities,
`bar_U'=E[u_S(H-S)]` and
`bar_W'=E[(S+H-S)u_S(H-S)]=H*bar_U'`.
Hence

\[
\boxed{j'(H)=\frac{\bar U'(H)}{\bar U(H)^2}
       \left[cE[D_S(H-S)]-\bar A\right].}
\]

The exact optimality equation is

\[
\boxed{E[D_S(H_*-S)]=E[F(S)+\kappa S]/c.}
\]

The left side has derivative bar_U>0, so again there is one crossing or an
admissible-boundary optimum. A general-measure formulation can use the mixed
absolute-context renewal measure instead of densities. Dependence between
S and F is allowed. Correlation with future growth is allowed only through a
declared restarted conditional law with common conditional mean; surviving
history that links cycles is not fresh iid reset sampling.

### 6.1 Reset variability and a small-variance correction

In the independent common-growth case D is convex. If S_1<=cx S_2 and
`E[F(S)+kappa S]` is held equal (e.g. F affine and reset means equal), then
`E[D(H-S_2)]>=E[D(H-S_1)]`. On a common admissible range containing both
canonical optima, more-variable reset weakly lowers the optimal absolute H.
Jensen gives `E[D(H-S)]>=D(H-E[S])`: the mean-reset plug-in tends toward too
large a canonical threshold under these hypotheses.

For mean s and small centered reset fluctuation epsilon, if D is twice
differentiable with a controlled Taylor remainder near L_0=H_0-s,

\[
E[D(H-S)]=D(H-s)+\tfrac12\operatorname{Var}(S)u(H-s)
             +\hbox{higher-order remainder}.
\]

When bar_A stays fixed, the leading optimum shift is

\[
\delta H_*\approx
-\frac{\operatorname{Var}(S)}{2}\frac{u(L_0)}{U(L_0)}.
\]

This is a local asymptotic expansion, not a guarantee based on CV alone.
An unbounded reset law has P(S>=H)>0 for every finite H; concentrating it
does not justify clipping, conditioning those cases away, or applying the
positive-gap theorem literally. Model its atomic one-action reset behavior
separately or use a genuinely bounded declared reset law.

For exponential growth, this concentration extension is exactly solvable.
With mu=E[S], sigma_squared=Var(S),

\[
E[D(H-S)]=(H-\mu)+\frac{(H-\mu)^2+\sigma^2}{2g},
\]

\[
\boxed{H_* =\mu-g+
 \sqrt{g^2+2g\bar A/c-\sigma^2}.}
\]

The formula requires a real radicand and H_*>ess_sup S; otherwise the admissible
boundary must be considered. Its full rate is
`b+kappa*g+[bar_A+c*mu+c*(H^2-E[S^2])/(2g)]/[1+(H-mu)/g]`.
Thus reset variance is not automatically irrelevant even when reset sizes are
concentrated. The variance subtraction is an exact consequence of the mixture
renewal equation, not an invented Gaussian reset assumption.

### 6.2 Phase-conditioned growth and where the common-mean condition matters

For a fresh iid phase Z with conditional mean g_Z, homogeneous c and affine
kappa, the terminal contribution is
`kappa*E[g_Z U_Z(H-S)] / bar_U(H)` rather than kappa*g.
Let weights be proportional to U_Z and conditional local expansion rate
`lambda_Z(H)=u_Z(H-S)/U_Z(H-S)`. Its derivative adds

\[
\kappa\operatorname{Cov}_{\mathrm{weighted}\ Z}(g_Z,\lambda_Z(H)).
\]

There is no generally fixed sign for that covariance. Equal conditional means
recover the previous single crossing; different phase means require this
additional term. If phase persists across reset, use a Markov-renewal or
general controlled-state model and its invariant/reset-state law, not an iid
mixture. Selecting phase-conditioned thresholds can be useful when phase is
observed, but is a larger policy class than one global H.

If the ordinary baseline price itself differs by phase, its weighted mean
adds `Cov_weighted(b_Z,lambda_Z(H))` to the derivative as well. The phase result
above holds b fixed; it must not silently average differing b_Z into a constant.

## 7. Exact four-price transfer and the marked-tail correction

The homogeneous carry ledger is not automatically the package's request ledger.
The important discrepancy can be identified algebraically instead of hidden.
Assume no TTL misses, cache eligibility throughout, no changing file versions,
and full reset reconstruction. On ordinary action n:

- B_n is newly retained input before its model request;
- O_n is billed generated output;
- Z_n is all retained text appended **after** the request, including output
  and any automatic tool observations;
- total ordinary growth is G_n=B_n+Z_n.

The joint marks (B_n,O_n,Z_n) are iid; they need not be independent components.
The previous Z_{n-1} is not yet in the cache prefix. Normal invoice is

\[
p_rX_{n-1}+p_wB_n+p_oO_n+(p_w-p_r)Z_{n-1},
\]

with the first-reset rewrite surcharge rho replacing that previous-tail term
at cycle start. The compactor charges

\[
p_rX_T+(p_i-p_r)Z_T+f.
\]

Summing the previous-tail writes yields the complete expected cycle rate

\[
\boxed{j(L)=b+p_rS+p_rg+
 \frac{A_0+p_rM(L)+(p_i-p_w)\zeta(L)}{U(L)},}
\]

\[
b=E[p_wB+p_oO+(p_w-p_r)Z],\qquad
A_0=f+(p_w-p_r)V+p_rS,\quad \zeta(L)=E[Z_{T_L}].
\]

Every input is billed exactly once per request in the correct category;
the final output/tool tail is uncached at the compactor, not retroactively
written on its generating ordinary call. Z is not automatically all model
output; O remains separately charged. Full restored files are not counted
again in these ordinary marks.

The ideal theorem is exact if Z=0, p_i=p_w, or zeta is threshold-constant
and its fixed contribution is included in A. Otherwise define
`A(L)=A_0+(p_i-p_w)zeta(L)`. Under density/differentiability,

\[
\boxed{j'(L)=\frac{u(L)[p_rD(L)-A(L)]+A'(L)U(L)}{U(L)^2}.}
\]

This is the precise mechanism by which a four-price implementation can depart
from the fixed-A single crossing. It is still a tractable marked-renewal
problem rather than a reason to abandon analysis for brute-force simulation.

### 7.1 The terminal mark is a renewal convolution

Define `psi(y)=E[Z*1{G>=y}]`, y>0. Condition on the cumulative pre-crossing
position and use independence of the next iid mark from its past:

\[
\boxed{\zeta(L)=\int_{[0,L)}\psi(L-x)\,\mathcal U(dx).}
\]

This uses the **joint** increment/tail law; a growth marginal alone cannot
identify it. Exact lattice convolution, Laplace methods or quadrature can
evaluate it directly. If a restored/recovery tail has an additional distinct
mark, represent its joint kernel too rather than treating every output as
the configured ordinary output fraction.

For exponential G of mean g and synthetic proportional after-call tail
Z=alpha*G,

\[
\psi(y)=\alpha(y+g)e^{-y/g},\quad
\zeta(L)=\alpha g(2-e^{-L/g}),\quad
\zeta'(L)=\alpha e^{-L/g}.
\]

With delta=p_i-p_w<=0, the exact optimum equation becomes

\[
\boxed{p_r\left(L+\frac{L^2}{2g}\right)
 =A_0+\delta\alpha[2g-(2g+L)e^{-L/g}].}
\]

The left side increases strictly. The bracket on the right increases from
zero, so its coefficient delta<=0 makes the right side nonincreasing.
For A_0>0 this gives a unique positive crossing and an exact monotone scalar
root calculation. The marked correction's added rate has derivative
`delta*alpha*[(2+L/g)exp(-L/g)-2]/U(L)^2`, which is nonnegative for delta<=0.
It therefore moves the optimum toward a smaller gap than the ideal fixed-A_0
benchmark. This is an actual four-price structural result in a declared
proportional/exponential control, not a claim that real output tails obey it.

### 7.2 Cache misses and price/carry correlation

A scalar effective c is justified when the conditional expected marginal
history price is the same constant at all pre-crossing histories. An
independent matching-prefix hit probability q gives
`c=q*p_r+(1-q)*p_w` in the simplified selected-for-write ledger.
If hit/expiry/routing survival is correlated with current history length,
the reward is `E[price_n*X_n]`, not E[price_n]*E[X_n].

### 7.3 A broader exact single-crossing class: monotone carry reward

Suppose a **policy-independent** scalar conditional expected history-carry
reward a(x), in USD per ordinary action at length x, correctly describes the
workload. It may include length-dependent marginal prices. Keep fixed reset,
iid nonnegative growth and affine compactor, with no additional threshold-
dependent terminal mark. Put

\[
C_a(L)=\int_{[0,L)}a(S+x)\,\mathcal U(dx),\qquad
j_a(L)=b+\kappa g+\frac{A+C_a(L)}{U(L)}.
\]

At a density point, its derivative has the sign of `B_a(L)-A`, where

\[
\boxed{B_a(L)=a(S+L)U(L)-C_a(L)
=\int_{[0,L)}[a(S+L)-a(S+x)]\,\mathcal U(dx).}
\]

If a is nondecreasing, B_a is nondecreasing: existing integrand terms increase
and newly included terms are nonnegative. The corresponding atomic-rate
change has the same sign. Thus the decrease-then-increase/plateau structure
extends beyond a constant effective per-token cache price. For locally
absolutely continuous a,

\[
B_a(L)=\int_0^L a'(S+t)U(t)dt,\qquad
B_a'(L)=a'(S+L)U(L)\ge0.
\]

Linear a(x)=c*x recovers B_a=c*D. If B_a never exceeds A, no finite interior
optimum is required; bounded/flat holding rewards can favor the largest
admissible threshold. Discontinuous price tiers use the nondecreasing B_a
crossing and exact jumps, rather than a fictitious derivative at the tier.

The condition that a is policy-independent matters: conditioning cache hits
on length using data from one threshold may hide different age/phase mixtures
at another threshold. TTL ages, changing cache boundaries, recovery duration
and phase cannot generally be compressed into a(x) without verifying this
conditional-reward property. Monotonicity of a is also a premise, not implied
by an average price schedule; caching can make the actual conditional reward
nonmonotone. The formula shows exactly what must be established for transfer.

## 8. Finite ordinary horizons and no terminal reset

Split F=rho+f: rho is first-reset rewrite correction, f is the compactor's
fixed instruction/output charge. Start with an already reconstructed context S
whose first ordinary prompt incurs rho. Let N=n remaining ordinary actions,
m=min(T_L,n), and

\[
B_n=E\sum_{j=0}^{m-1}[b+c(S+Y_j)].
\]

For n>=1 the exact finite expected invoice in the ideal ledger is

\[
\boxed{V_n=\rho+B_n+
 \sum_{t=1}^{n-1}\Pr(T_L=t)V_{n-t}
 +E[1\{T_L<n\}\{f+\kappa(S+Y_{T_L})\}],
\quad V_0=0.}
\]

The strict t<n exclusion is essential: if crossing occurs on the last ordinary
action, no compactor and no next reset rewrite is billed. The ordinary partial
cycle is still billed. No recovery call decrements n. Joint terminal marks
are carried in the truncated compactor expectation, not replaced with their
unconditional means.

This is an ordinary-count renewal equation, evaluable by convolution/recursion
without simulating every token trajectory. With a different initial S_0,
resident facts or cache state, the first-cycle kernel is different; use a
delayed first-cycle equation then the regenerative continuation V.

### 8.1 An explicit finite-versus-rate error bound

Assume rho,f,b,c,kappa>=0 for this bound. Let complete ideal cycles have
ordinary length T and nonnegative total invoice Q. Let M_N be the first cycle
whose cumulative ordinary length reaches or exceeds N. The actual finite
invoice C_N consists of the preceding complete cycles plus the charged
ordinary partial final cycle, without the final compactor.

Wald on iid cycle pairs gives
`E[sum_{j<=M_N} Q_j]=j(L)*E[sum_{j<=M_N}T_j]`.
Write ordinary-count overshoot B_N=sum T_j-N and uncharged final-cycle
remainder Delta_N>=0. Then exactly

\[
E[C_N]-N j(L)=j(L)E[B_N]-E[\Delta_N].
\]

Lorden bounds E[B_N]<=E[T^2]/E[T]. At integer ordinary times the probability
of a renewal epoch is at most one. Summing over possible final-cycle start
times therefore bounds `E[Q_{M_N}]<=E[TQ]`, and Delta_N<=Q_M_N. Hence

\[
\boxed{|E[C_N]-N j(L)|
 \le j(L)\frac{E[T^2]}{E[T]}+E[TQ].}
\]

This bound is finite for the fixed-L ideal model with E[G]<infinity. Before
crossing context is below H and crossed context is at most H+G_T, so

\[
E[TQ]\le(b+cH)E[T^2]+(F+\kappa H)E[T]
           +\kappa g E[T(T+1)/2].
\]

For the final term use
`E[T*G_T] <= sum_n n E[G_n*1{T>=n}]
=g E[T(T+1)/2]`. The negative-binomial domination already gives finite
moments of T. The displayed bound is a conservative certificate, not a
sharp fitted estimate. Its constants depend on H, so pointwise O(1) error
in N does not justify uniformly optimizing very large H at a short horizon.
For practical selection use the exact finite renewal recursion whenever N
is only a few expected cycles.

An initially warm versus rewritten first prompt can be adjusted by its actual
rho_0-rho boundary term when the remaining initial state is otherwise the
same. If incremental rho is negative, use absolute/reward domination or the
actual nonnegative request ledger instead of the nonnegative-partial-reward
bound just proved.

## 9. Boundary with lazy restoration and persistent phases

If only some files are compulsory and they reenter at first use, retained
growth includes indicators `d_i*1{K_i<=n}`. That growth is not an iid sum of
ordinary aggregate G unless a workload model justifies it. First-use marks
can change T and survival of file versions can link cycles. A fixed full
reconstruction assumption should be tested against these mechanisms rather
than asserted solely from a full-prompt median.

Endogenous first use inside a cycle does **not by itself** destroy regeneration
between cycles. If every reset clears all prerequisite state and future demand
marks truly restart iid, the enlarged first-use cycles can still be iid and
renewal reward can still apply. What fails is the specific iid additive-growth
representation yielding U,M,D and its universal crossing. Persistent versions,
guards, phase or preserved facts create the further intercycle-dependence issue.
This distinguishes a failure of the simple renewal clock from a failure of
regenerative cycle theory altogether.

Useful decomposition for model selection:

1. Apply the renewal analytic result to immediately mandatory reconstructed
   context and net ordinary aggregate growth within a stable project phase.
2. If delayed restoration contributes a small controlled perturbation, measure
   its price-weighted residency area and terminal mark, then bound/test the
   threshold regret of ignoring it.
3. If restoration substantially changes stopping or facts survive resets,
   use the versioned joint-state Bellman/Markov-renewal model. The analytic
   core supplies a mechanistic baseline and initial region, not an oracle.

The exact general-control counterexample shows equal context lengths can
require opposite compact decisions. It does not contradict this theorem:
that example varies valid file facts and permits delayed prerequisites,
whereas this renewal class reconstructs the same full required state every
cycle. The theorem's useful breadth is arbitrary iid nonnegative growth laws,
not arbitrary informational state.

## 10. Measurement and analysis priorities

The essential empirical target is the **net ordinary increment law and its
serial/phase dependence after compulsory reconstructed input is separated**.
Do not infer growth G from total billed prompt input: repeated history carries
are invoice exposure, not new retained growth. Collect append categories,
current retained length, post-call tail Z, ordinary output O, cache prefix
length/ages, reset S and actual compactor/recovery usage.

The analytic workflow is:

- Identify the compulsory full reconstructed set and genuine stable prefix;
  obtain S,V,F rather than adding components on top of an unidentified aggregate.
- Estimate or bracket g,m_2, zero mass and the conditional net-growth law.
  Check phase persistence and dependence before using iid convolution.
- Compute U,D from the empirical/lattice law or justified symbolic family;
  solve one monotone equation rather than inspect a Monte Carlo curve for shape.
- Use convex-order/moment bounds to explain movement across scenarios.
- Add the marked-tail convolution needed by the actual four-price cache ledger.
- Evaluate finite N by the ordinary-count renewal recursion and endpoint
  adjustments; use discrete event replay to discover model violations.

This yields a useful scale model while retaining an explicit route back to
full working-set behavior. It prioritizes structural invoice insight and
analytic optimization; the number of tests or simulated thresholds is not
the scientific contribution.

## References and intellectual status

1. Gary Lorden. *On excess over the boundary*. Annals of Mathematical Statistics
   41(2), 520-527, 1970. [DOI](https://doi.org/10.1214/aoms/1177697092),
   [author archive](https://authors.library.caltech.edu/records/8eyxa-q6789).
   Peer-reviewed basis for uniform overshoot bounds; >= convention handled
   explicitly by comparison with the strict-crossing path.
2. Maria Vlasiou. *Renewal Processes with Costs and Rewards*. Wiley Encyclopedia
   of Operations Research and Management Science, 2011; author manuscript
   updated 2018. [Author manuscript](https://arxiv.org/abs/1404.5601),
   [university full text](https://ris.utwente.nl/ws/portalfiles/portal/249488824/10.1002_9780470400531.eorms0722.pdf).
   Standard ratio theorem and partial-cycle qualifications.
3. Daryl Daley. *Renewal Function Asymptotics Refined a la Feller*. Probability
   and Mathematical Statistics 37(2), 291-298, 2017.
   [DOI](https://doi.org/10.19195/0208-4147.37.2.5),
   [journal full text](https://wuwr.pl/pms/article/download/6907/6553).
   Primary source for finite-second-moment nonarithmetic renewal asymptotics.
4. Karl Sigman. *Renewal Theory*.
   [Author-hosted lecture notes](https://www.columbia.edu/~ks20/4106-18-Fall/Notes-Renewal-Theory.pdf).
   Supporting primary exposition; not an independent research novelty claim.
5. Anthropic. *Prompt caching* and *Context editing*.
   [Caching documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
   [editing documentation](https://platform.claude.com/docs/en/build-with-claude/context-editing).
   Production ledger/prefix mechanisms; no provider price or empirical hit
   law inferred here. Implementation transfer uses the in-repository contract.
6. Azam Imomov and Shakhzod Rizaqulov. *Second-order renewal asymptotics in the
   finite-variance regularly varying regime*. Submitted 2026-07-28,
   [arXiv:2608.06392](https://arxiv.org/abs/2608.06392). Non-peer-reviewed
   frontier context, abstract only consulted; not a theorem dependency.

The single-crossing and comparative results are derived here from classical
renewal identities. They are a contribution to this project's formulation and
decision method; no priority claim over the replacement/maintenance literature
is made without a separate novelty review. No code or dependencies were edited
by this theory track. Closed-form family and reproducible numeric artifacts
are owned by the root/exact-law tracks.
