# Closed renewal laws, overshoot corrections, and analytic thresholds

Recorded 2026-10-06. This delivers an analytic model and closed-form law
evaluation, not a threshold-path simulation. Source:
`src/context_compaction_lab/renewal_analytic.py`; executable derivation:
`experiments/renewal_closed_form_derivation.py`. General ledger and single-
crossing proofs are in [renewal-analytic-control.md](renewal-analytic-control.md).
Actual growth calibration, including serial dependence and large-tail warnings,
is in [renewal-community-calibration.md](renewal-community-calibration.md).

## 1. Main result

For iid nonnegative ordinary growth with mean g>0, fixed reset context S,
homogeneous history-carry price c>0, crossing-context price kappa>=0, and a
one-cycle reset surcharge F, set L=H-S>0 and A=F+kappa*S. The analytic rate is

\[
j(L)=b+cS+\kappa g+\frac{A+cM(L)}{U(L)},
\quad D(L)=LU(L)-M(L)=\int_0^L U(x)dx.
\]

For continuous renewal density u=U',

\[
\boxed{j'(L)=\frac{u(L)}{U(L)^2}\{cD(L)-A\},\qquad D(L_*)=A/c.}
\]

This replaces arbitrary threshold sweeps by a unique scalar crossing in the
specified regenerative class. Endogenous crossing/overshoot is retained;
`T` is not replaced by `(H-S)/g`. For atoms, the general note supplies the
signed-jump/plateau version. This note adds:

* Exact exponential, Erlang-k, and two-exponential mixture U,D and terminal
  crossing-increment laws, with executable Laplace identities.
* A third-moment constant in the integrated renewal expansion, proved using
  the key renewal theorem rather than assumed from a formal Laplace series.
* Corrected thresholds for output tails that remain cold at compaction.
* An exact independent random-reset mean/variance threshold.
* A typed numerical implementation of those analytic expressions and their
  bracketed roots, without Monte Carlo law evaluation.

The rate is long-run USD per ordinary action. It is not an exact finite-task
bill and must not introduce a terminal compact in a finite task. Versions,
first-use file recovery, correlated phases, TTL/state-dependent misses, or
policy-dependent future growth need the general state model unless regeneration
is separately justified.

## 2. Exponential law and compatibility with the existing analytic model

For G exponential with mean g,

\[
U(L)=1+L/g,\quad M(L)=L^2/(2g),\quad D(L)=L+L^2/(2g).
\]

The initial 1 is one ordinary request before any renewal, not an optional
finite-sample correction. Exponential overshoot has mean g and the expected
crossed context is `S+gU=H+g`, not H.

\[
\boxed{L_*=\sqrt{g^2+2gA/c}-g,\quad H_*=S+L_*.}
\]

The derivation script substitutes
`A=k0+(k1+pw-pr)S`, `c=pr`, and `kappa=k1` into the older
`analytic.py` formula and verifies exact equality. Its API remains unchanged.
The deterministic fluid gap `sqrt(2gA/c)` is a different relaxation; it misses
the initial-renewal/overshoot correction and is not the exact exponential root.

## 3. Erlang phases: exact laws below CV=1

Let the positive increment be Erlang-k with mean g and integer k>=1. Its
Laplace transform is

\[
\widehat F(s)=(1+gs/k)^{-k},\qquad
\widehat U(s)=\frac{1}{s(1-\widehat F(s))}.
\]

Write `omega_j=exp(2 pi i j/k)`, `r_j=(k/g)(omega_j-1)` for j=1,...,k-1.
All r_j have negative real part. Residues at those poles give

\[
\boxed{U_k(L)=\frac Lg+\frac{k+1}{2k}
+\sum_{j=1}^{k-1}\frac{\omega_j}{k(\omega_j-1)}e^{r_jL}.}
\]

The expression is real because conjugate poles pair. The integrated law is

\[
\boxed{D_k(L)=\frac{L^2}{2g}+\frac{k+1}{2k}L
+\sum_{j=1}^{k-1}\frac{\omega_j}{k(\omega_j-1)}
                         \frac{e^{r_jL}-1}{r_j}.}
\]

The nonzero-pole residue simplifies to `(s+k/g)/(ks)` before substituting
s=r_j. The double pole at zero supplies L/g and the intercept. This is a
finite k-phase analytic law, not a fitted arbitrary Gamma shape.

For k=2,

\[
U_2=L/g+3/4+e^{-4L/g}/4,
\]
\[
\boxed{D_2=L^2/(2g)+3L/4+\frac g{16}(1-e^{-4L/g}).}
\]

For k=3, put `theta=3 sqrt(3)L/(2g)`:

\[
U_3=L/g+2/3+e^{-9L/(2g)}\{\cos\theta/3+\sqrt3\sin\theta/9\},
\]
\[
D_3=L^2/(2g)+2L/3+\frac{2g}{27}
                      (1-e^{-9L/(2g)}\cos\theta).
\]

Their threshold equations are explicit smooth increasing scalar equations
`D_k(L)=A/c`; a bracketed root is more useful than forcing an elementary
inverse that does not exist. SymPy directly verifies the k=1,2,3 Laplace
transforms, D'=U, and complete rate derivative.

### Deterministic increments are not the deterministic fluid

For actual G=g deterministically, T=ceil(L/g) and the rate is constant on
each cell `((m-1)g,mg]`:

\[
j_m=b+cS+\kappa g+\frac Am+\frac{cg(m-1)}2.
\]

An optimal m satisfies
`g(m-1)m/2 <= A/c <= gm(m+1)/2`. The whole corresponding threshold cell is
optimal; ties at a triangular boundary add a neighboring cell.

For `n=floor(L/g)` and `theta=L/g-n`,

\[
D(L)=L^2/(2g)+L/2+g\theta(1-\theta)/2.
\]

The last term is genuinely periodic and does not converge to one constant.
Thus the nonarithmetic expansion below cannot be transplanted pointwise to
this lattice law. The fluid model instead uses `U=L/g`, `D=L²/(2g)` and
obtains `L_fluid=sqrt(2gA/c)`. This is a declared macroscopic relaxation,
not a claim that deterministic iid increments have fractional crossing counts.

## 4. Hyperexponential law: a tractable high-variance mechanism

Let positive growth mix exponentials with weights p,1-p and rates lambda1,
lambda2, both positive. Define

\[
g=p/\lambda_1+(1-p)/\lambda_2,\quad
m_2=2\{p/\lambda_1^2+(1-p)/\lambda_2^2\},
\]
\[
v=(1-p)\lambda_1+p\lambda_2,\qquad a=m_2/(2g^2).
\]

The rational Laplace transform has only one nonzero renewal pole, yielding

\[
\boxed{U(L)=L/g+a+(1-a)e^{-vL},}
\]
\[
\boxed{D(L)=L^2/(2g)+aL+\frac{1-a}{v}(1-e^{-vL}).}
\]

This covers a two-scale burst mechanism without attributing an empirical shape
to it. The module can construct a balanced-means two-phase law matching a
given mean and CV>=1:

\[
p=\frac{1+\sqrt{(CV^2-1)/(CV^2+1)}}2,
\quad\lambda_1=2p/g,\quad\lambda_2=2(1-p)/g.
\]

Matching mean/CV is not proof that a marginal mixture, or independence of its
successive increments, fits actual traces. The community calibration records
both large tails and positive serial dependence, which these iid laws do not
erase.

## 5. Third-moment integrated renewal constant

Let G be nonnegative, nonarithmetic with g>0 and finite raw moments m2,m3.
With the initial renewal included,

\[
U(L)=L/g+a+o(1),\quad a=m_2/(2g^2)=(1+CV^2)/2.
\]

The integrated refinement is

\[
\boxed{D(L)=L^2/(2g)+aL+C_0+o(1),\qquad
C_0=\frac{m_2^2}{4g^3}-\frac{m_3}{6g^2}.}
\]

### Proof of the constant, not only a Laplace heuristic

Let `P(L)=L²/(2g)+aL+C0`. Since D solves `D(L)=L+F*D(L)`, its remainder
q=D-P solves a renewal equation `q=r+F*q`, with

\[
r(L)=-E[P(L-G)\mathbf1\{G>L\}].
\]

Expanding the forcing gives a finite linear combination of
`E[(G-L)_+²]`, `E[(G-L)_+]`, and `P(G>L)`. Each is bounded, nonincreasing,
and integrable when m3 is finite; hence r is directly Riemann integrable.
Tonelli applied to the nonnegative individual terms gives

\[
\int_0^\infty r(L)dL=-m_3/(6g)+a m_2/2-C_0g=0.
\]

The nonarithmetic key renewal theorem therefore gives
`q(L) -> (1/g) integral r = 0`. This proves the displayed expansion, including
its assumptions. Formal Laplace expansion independently checks the algebra:

\[
\widehat U(s)=\frac1{gs^2}+\frac{m_2}{2g^2s}
+\left(\frac{m_2^2}{4g^3}-\frac{m_3}{6g^2}\right)+o(1).
\]

The established renewal-theory foundations include
[Blackwell's renewal theorem, Duke Mathematical Journal 1948](https://doi.org/10.1215/S0012-7094-48-01517-8)
and [Daley's higher-moment refinements, Probability and Mathematical Statistics 2017](https://doi.org/10.19195/0208-4147.37.2.5).
The key-renewal hypotheses are also stated in the
[Encyclopedia of Mathematics entry](https://encyclopediaofmath.org/wiki/Blackwell_renewal_theorem).
The proof above makes the specific constant and forcing checkable without
claiming a new general renewal theorem.

### Inverting the refinement

Write `R=A/c` and `L0=sqrt(2gR)`. Retaining C0 gives

\[
\boxed{L_{\rm quad}=-ag+\sqrt{a^2g^2+2g(R-C_0)}.}
\]

As R tends to infinity under a fixed law,

\[
\boxed{L_*=L_0-ag+
\frac{m_3/(3g)-m_2^2/(4g^2)}{2L_0}+o(1/L_0).}
\]

Thus the first stochastic correction to the fluid gap is
`-g(1+CV²)/2`. Higher variability lowers that leading correction's threshold
at fixed mean and fee ratio, but finite-gap ordering must not be inferred
from CV alone: the third moment and transient shape also matter. The general
note separately proves an exact ordering under **convex order**, a stronger
assumption than a CV comparison.

For Erlang-k,
`a=(k+1)/(2k)` and `C0=g(1-1/k²)/12`. For the two-exponential mixture,
`C0=(1-a)/v`, which may be negative and large. A short gap relative to 1/v
can invalidate a moments-only approximation even though all moments exist.

## 6. Zero-growth actions

If `p0=P(G=0)<1`, condition the law on G>0. Its renewal functions satisfy

\[
U(L)=U_+(L)/(1-p_0),\qquad D(L)=D_+(L)/(1-p_0).
\]

The atom at zero is `1/(1-p0)`, recording repeated zero-growth ordinary
requests. It must not be replaced by one. Terminal crossing increment is
strictly positive and has the same law as in the thinned positive renewal.
The module's `mean_growth` is unconditional; its positive mean is
`mean_growth/(1-p0)`. Moment and asymptotic constants use unconditional
moments, which agree with this thinning identity. The derivation script checks
duration/D scaling and unchanged terminal increments numerically.

## 7. Four-price cache-tail correction

The clean affine crossing model can otherwise miss the last generated output
tail Z, which has not yet entered the cached prefix when compaction begins.
For iid cache-hit marks q independent of joint growth/output marks, eligible
stable prefix B<=S, no extra expiry delay, and compactor instruction u_c:

\[
c=p_w-q(p_w-p_r),\quad\kappa=p_i-q(p_i-p_r),
\]
\[
F_0=p_i u_c+p_o C,\quad
F=F_0+(p_w-c)(S-B),\quad A=F+\kappa S,
\]
\[
b=(p_w-c)g+p_i u+p_o E[O],\quad d=q(p_i-p_w).
\]

C is the generated summary already included in S. Required file payload
belongs in S or growth, not again in generated output. The collapsed rate is

\[
j=b+cS+\kappa g+
\frac{A+cM(L)+d\zeta(L)}{U(L)},\qquad\zeta(L)=E[Z_T].
\]

This is an explicit correction, not a declaration that the four-price ledger
equals a generic single-price renewal rate.

The current `physical_cache_fees` helper puts **all ordinary retained growth
in the post-call tail** when constructing b. Billed generated output O is a
separate nonnegative finite mark: it can exceed retained growth when not all
billed output is kept. The helper therefore does not impose `E[O]<=E[G]`.
With a genuine pre-call append component B_n and post-call tail Z_n, the
consistent ordinary baseline is instead
`b=p_w E[B_n]+(p_w-c)E[Z_n]+p_i u+p_o E[O]`. Changing `terminal_fraction`
in `rate` or `optimal_gap` only changes the crossing correction; it does not
silently rebuild this pre/post timing baseline. For a literal proportional
tail law `Z_n=alpha G_n`, callers must supply the corresponding b as well.
Holding b fixed while varying that argument is a declared crossing-correction
sensitivity, not a change of all ordinary input timing.

For proportional marks Z=alpha G, the terminal-growth transform is

\[
\widehat{E[G_T]}(s)=\frac{g+\widehat F'(s)}{s(1-\widehat F(s))}.
\]

The exact Erlang-k terminal mean is

\[
\boxed{E[G_T]=g(1+1/k)+(g/k)\sum_{j=1}^{k-1}e^{r_jL}
-g e^{-kL/g}.}
\]

It tends to the size-biased mean m2/g, not the ordinary mean g. For k=2 it
equals `g(3/2+e^(-4L/g)/2-e^(-2L/g))`; for exponential growth it is
`g(2-e^(-L/g))`. The mixture terminal law is also explicitly implemented and
its rational Laplace transform checked in the artifact.

For exponential growth, the corrected threshold solves

\[
\boxed{cD(L)=A+d\alpha\{2g-(2g+L)e^{-L/g}\}.}
\]

When `p_i<=p_w`, d<=0 and the extra term lowers the optimal gap. The left
side is strictly increasing and the right side is decreasing, so uniqueness
survives. This is the exact correction requested by the engineering ledger,
not a terminal compaction mistakenly added to a finite task. General marked
phases need their own global sign analysis; the implementation deliberately
does not declare every tail-corrected Erlang/mixture rate unimodal.

The proportional-mark assumption is stronger than setting alpha to E[O]/g.
Observed output-growth dependence must be preserved by a joint marked renewal
convolution when that assumption does not hold. The community analysis owns
that nonparametric extension.

## 8. Independent random reconstruction

If bounded fresh reset S is independent of future growth, let mu=E[S],
v=Var(S), and Abar=E[F+kappa*S]. For exponential growth and
`H>ess sup S`,

\[
E[U(H-S)]=1+(H-\mu)/g,
\]
\[
E[D(H-S)]=(H-\mu)+\{(H-\mu)^2+v\}/(2g).
\]

The correct derivative comes from the ratio of mixture expectations and its
stationary condition is `c E[D]=Abar`:

\[
\boxed{H_*=\mu-g+\sqrt{g^2+2g\overline A/c-v}.}
\]

The variance derivative is exactly
`-1/(2 sqrt(g²+2g Abar/c-v))` while mu,Abar stay fixed. Random reset
concentration therefore changes the threshold; replacing S by its mean loses
the variance term. If F is nonlinear in S, Abar is its actual expectation,
not F(mu). The support condition is essential: if the displayed root lies
below the reset upper bound, the interior formula is not an admissible result.
The typed helper rejects that case rather than reporting a false optimum.

## 9. Executed analytic comparisons and approximation scope

These are dimensionless comparative statics, **not workload measurements**.
Set g=1 and A/(cg)=50. The scalar equations give:

| Analytic growth law | CV² | Exact optimum L/g | Fluid gap | C0/g |
| --- | ---: | ---: | ---: | ---: |
| Exponential | 1 | 9.04987562 | 10 | 0 |
| Erlang-2 | 0.5 | 9.27185113 | 10 | 0.0625 |
| Erlang-3 | 1/3 | 9.34813719 | 10 | 2/27 |
| Erlang-8 | 0.125 | 9.44511429 | 10 | 0.08203125 |
| Balanced hyperexponential, CV=2 | 4 | 8.15186848 | 10 | -3.75 |

For the hyperexponential law the moments-only quadratic root is 8.16536450,
0.166% above the exact root. At fee ratio 2 its relative error is 56.8%; at
fee ratio 0.2 it is 618.7%. At ratio 500 the relative error is only 3.21e-8.
This directly demonstrates why a formal large-gap expansion is not a default
substitute for a real renewal law at a short or tail-dominated gap.

With exponential g=1, A/c=50, d/c=-2.5, and proportional tail alpha=0.4,
the exact tail correction moves the gap from 9.04987562 to 8.84901590.
With bounded reset mean 20, variance 4, upper support 24 and the same g,A/c,
the random-reset threshold is 28.84885780 instead of the mean-plug-in
29.04987562. These are mechanism demonstrations derived from equations,
not invented empirical observations.

Real community growth has strong tails and serial dependence. Approximately
the top 1% of accepted aggregate increments account for 95.7% of its measured
third moment. Consequently C0 estimated from that sample can be highly
tail-sensitive. The root calibration should compare the exact empirical renewal
function against any proposed moment expansion, rather than assume its
asymptotic regime from the existence of three finite sample moments.

## 10. Executable contracts and reproduction

```python
from context_compaction_lab.renewal_analytic import ErlangRenewal, RenewalFees, optimal_gap

law = ErlangRenewal(mean_growth=1.0, shape=2)
fees = RenewalFees(reset_tokens=0.0, fixed_cost=50.0, carry_price=1.0, crossing_price=0.0)
gap = optimal_gap(law, fees)
# law.statistics(gap).integrated_duration equals fees.numerator_fee / fees.carry_price.
```

`physical_cache_fees` constructs the four-price coefficients with explicit
reset/base/summary, all-post-call growth, and independent cache-hit assumptions.
It enforces `B+C<=S` but does not bound billed output by retained growth. `rate_derivative`
includes the marked terminal correction. `optimal_gap` brackets the increasing
renewal condition; a nonzero terminal correction is enabled only for the
exponential law where its positive crossing is justified. `statistics(0)`
returns a right limit for bracketing; actual rate evaluation requires L>0.
`asymptotic_optimal_gap` rejects nonpositive approximate gaps and does not
claim finite-gap accuracy. Random reset inputs enforce necessary bounded-
support variance constraints and the admissible threshold domain.

Run from the repository root:

```powershell
uv run python experiments/renewal_closed_form_derivation.py
uv run ruff check src/context_compaction_lab/renewal_analytic.py experiments/renewal_closed_form_derivation.py
```

All symbolic identities and deterministic evaluations completed successfully
in approximately 3.00 seconds; Ruff passed. No new large unit-test suite,
simulation path count, dependency, or version bump is a claimed contribution.
`.cache/renewal-closed-form/results.json` preserves exact U,D,M/Laplace
expressions, general phase formulas, moment constants, marked-tail and reset
identities, physical accounting coefficients, and the dimensionless evaluation
table. The executable includes exact old-model equivalence checks, zero-mass
thinning, stationary residual checks, and local rate comparisons.

The useful outcome is a coherent analytic reduction with explicit validity
boundaries: scalar renewal inversion for broad iid growth laws, tractable phase
mechanisms on both sides of CV=1, controlled large-gap corrections, and precise
four-price corrections where the idealized ledger was incomplete.
