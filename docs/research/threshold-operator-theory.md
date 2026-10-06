# The threshold derivative is a control-boundary operator

Date: 2026-10-06. This replaces scalar marginal fitting as the theoretical
foundation, not the backwards-compatible experimental implementation.
The companion [tool review](mathematical-tools-for-compaction.md) records
primary academic and production sources. [General control theory](general-stochastic-control-theory.md)
defines the history/kernel model and a simulator-checked sufficient-state
counterexample. This note supplies exact identities and their proof boundaries.

## 1. Do not turn dependence into independent marginal distributions

Let H_t be the observations and actions available at a decision epoch. On a
standard Borel history space, use a conditional environment law K_t(dh'|h,a)
and conditional mean ledger ell_t(h,a) in R_+^4. Demand, output, edits,
compression summaries, recovery and cache expiry can be arbitrarily correlated
and action-dependent. A reduced state S_t is allowed only if it preserves
conditional transition and cost laws for every admissible action. The entire
history is a formal sufficient state, not a claim of computational tractability.

Ordinary work is fixed at N actions. A macro-action must finish one ordinary
action and include ALL intervening compactor/recovery requests. Otherwise the
intervention uses the same remaining-work index and requires an impulse/obstacle
formulation. Strict rechecks can be expanded into bounded microdecision states;
they cannot be hidden inside a supposedly h-independent atomic kernel.

Feasible policies must complete the declared work. A failed finite bill is not
a completed-task cost. One can impose almost-sure completion or an explicit
chance constraint; these are different domains. The prior sampled all-success
filter is not a proof of either population constraint.

## 2. Exact forward occupations and backward values

For a finite sufficient-state discretization and a FIXED policy, use a row
initial law mu, row-stochastic K_t and d-by-4 ledgers L_t. Define

```
d_0 = mu,                 d_(t+1) = d_t K_t
g_t = L_t p,              V_N = 0
V_t = g_t + K_t V_(t+1)
q = sum_t d_t L_t,        J = mu V_0 = q p.
```

No independence between ledger components, between actions, or between file
demand and cache state is used. The state/kernel already contains that law.
Four expected quantities suffice for PRICE comparison of a fixed policy, but
four means emphatically do not suffice to predict transitions or optimize it.

For genuinely differentiable parameters theta, differentiation and telescoping
give the adjoint identity

```
dJ/dtheta = (dmu/dtheta) V_0
          + sum_t d_t [(dg_t/dtheta) + (dK_t/dtheta) V_(t+1)].
```

Proof: differentiate each backward equation, substitute recursively, and cancel
the propagated derivatives with the forward recurrence. The final derivative
is zero because V_N=0. This explains the missing structure in immediate-cost
arithmetic: a transition change is weighted by the ENTIRE remaining value,
not merely the next request price. With price-independent kernels/ledgers,
`dJ/dp = q` exactly. Parameter-dependent prices add `L_t dp/dtheta` to dg_t.

Implemented in `control_symbolics.py`. Arbitrary symbolic ledger coefficients
and correlated finite-state evolution are evaluated by
`experiments/threshold_operator_analysis.py`; direct expansion independently
returns ZERO for the occupation, adjoint, policy-difference and all four price
gradient residuals. Symbolic probability entries require their declared domain;
the implementation checks normalization, not universal nonnegativity proofs.

## 3. Exact policy difference: all changed future crossings are included

For baseline pi, define `Q_t^pi(s,a)=g_t(s,a)+K_t^a V_(t+1)^pi(s)`.
For alternative pi' with the same initial law and conditional environment:

```
J(pi') - J(pi)
  = sum_t E_pi'[Q_t^pi(S_t,A_t) - V_t^pi(S_t)].
```

Proof: expand the right-hand side. Conditional expectation turns each transition
term into the next V expectation. All intermediate terms cancel, the initial
term is J(pi), and the terminal term is zero. Integrability and compatible
information/admissibility contracts are needed; iid inputs are not.
Notice that occupations are under pi', NOT pi. This is how all later
threshold crossings, reloads and cache rewrites enter the exact comparison.

For atomic threshold policies compact iff x>=h, raising h by epsilon changes
the decision only in the slab h<=x<h+epsilon. Consequently

```
J(h+epsilon)-J(h)
  = sum_t integral_(h<=x<h+epsilon)
      [Q_t^h(s,continue)-Q_t^h(s,compact)] d_(t,h+epsilon)(ds).
```

This is the primary general sensitivity identity. It remains valid for atoms
and arbitrary dependence. It applies to every threshold-controlled microstate
if strict housekeeping is explicitly expanded with a common finite horizon.
It does not hold for a changed environment law without a kernel-change term.

### 3.1 When a classical boundary derivative exists

If the visited state law has a continuous x-density at h, action advantage has
appropriate traces, perturbed occupation laws converge on the slab, and
dominating bounds justify the limit, the exact identity yields

```
J'(h) = sum_t integral rho_(t,h)(h,z)
        [Q_t^h(h,z,continue)-Q_t^h(h,z,compact)] dz.
```

The necessary conditions matter: deterministic reset points can create atoms
even when ordinary growth is continuous. There is no general permission to
apply this density formula merely because one input was lognormal.
For a regular differentiable score phi(s), coarea calculus gives a surface
integral over phi(s)=h with factor 1/||grad phi||. This is the legitimate
state-space geometry/vector-calculus connection, not a fictitious physical field.

SymPy demonstration, X uniform on [0,1], 0<h<1:

```
Q_continue(x)=a+b*x, Q_compact(x)=c
J(h)=a*h+b*h^2/2+c*(1-h)
J'(h)=a+b*h-c.
```

For every fixed X except its crossing, the ordinary pathwise derivative is
zero. SymPy confirms that differentiating its Piecewise branch expression
returns zero, whereas integrating first gives a+b*h-c. The omitted term is
boundary mass. This is a checkable reason not to backpropagate naively through
hard compact comparisons. The example illustrates calculus assumptions, not
a fitted context process or a production optimum.

### 3.2 The implemented integer-token model has an exact atomic derivative

Assume retained lengths, payloads and additions are integers, and h enters
only comparisons x>=h. For every path and every positive real h:

```
C(h,omega) = C(ceil(h),omega).
```

Proof by induction over the event decisions: for integer x,
`x>=h` iff `x>=ceil(h)`. Equal previous decisions produce equal next states,
so the whole event history and ledger coincide. This proof permits arbitrary
joint input laws, expiry ages and endogenous reset times; it does not require
Bernoulli demands. Exact integer arithmetic or a safe float representation is
part of the premise. Other uses of h, such as continuous retention budgets,
would break it.

If the resulting expectations J(k) are finite, then J is constant on
`(k-1,k]`. On the positive real line its distributional derivative is

```
D_h J = sum_(k>=1) [J(k+1)-J(k)] delta_k.
```

Proof: integrate J against the negative derivative of a smooth compactly
supported test function and telescope the adjacent intervals. Point values at
integer boundaries do not affect a distribution. Only finitely many atoms meet
any compact support, so no infinite-series interchange is needed there.
The ordinary derivative is zero away from the integers and generally absent
at nonzero jumps. Thus solving J'(h)=0 in this exact model selects every
non-boundary interval and does not find an optimum. The meaningful threshold
object is the SIGNED jump measure or exact adjacent-policy difference.

This is a microscopic statement, not a prohibition on continuous probability
or macroscopic differentiation. As jump locations become dense and their
weights vanish, signed derivative measures can converge to a continuous
density while every microscopic ordinary derivative is zero. The subsequent
[continuum bridge](continuum-bridge-theory.md) supplies finite approximation,
boundary-stability and optimization-regret conditions rather than stopping
at exact discreteness.

`structural_symbolics.py` instantiates this using actual simulator ledgers and
exact rational path weights. Its finite-support Dirac formula is symbolic.
Lean checks the rational-cell gate equivalence and its lift to arbitrary
finite threshold decision trees, invoices and finite correlated task weights;
it does not prove this real distribution theorem or Python-to-tree refinement.

## 4. Structural economic geometry, not one imagined sweet number

Under a fixed price-independent law, q_pi is the expected ledger of a policy.
Its invoice is the linear functional p dot q_pi. Consequences:

1. **Price exposure:** q_pi is the exact price gradient. Correlations influence
   q_pi through the dynamics but do not break price linearity.
2. **Dominance:** if q_pi<=q_sigma componentwise, pi cannot cost more at any
   nonnegative prices. Remove dominated candidates before price optimization.
3. **Price regions:** pi wins over sigma exactly when
   `p dot(q_pi-q_sigma)<=0`. Finite candidate regions are intersections of
   half-spaces: polyhedral cones. Overall price scaling cannot change winners.
4. **Optimized value:** `F(p)=inf_pi p dot q_pi` is positively homogeneous,
   monotone in nonnegative prices and concave, wherever finite. For lambda in
   [0,1], taking the infimum proves
   `F(lambda*p+(1-lambda)*r)>=lambda*F(p)+(1-lambda)*F(r)`.
5. **Dimension reduction:** if p_w>0, decisions depend on three price ratios,
   not four absolute price magnitudes. This does NOT remove state variables.
6. **Implementation sensitivity:** different cache-safe forks or read guards
   change q_pi, thus rotate the policy-comparison hyperplanes. A price-only
   model with one reset scalar cannot represent that change.

These are applications of established linear-control geometry, not claims of
new general mathematics. Their project contribution is to organize the
coupled billing mechanisms into provable comparisons and exact price regions.
The fixed-policy premise excludes price-adaptive transition laws; global
optimization is over a declared feasible policy set, not a claim that our
finite candidate list contains every optimal engineering controller.

## 5. What can be certified without simulating another guessed workload

Finite-state occupation flows are linear constraints. Bellman subsolutions
`u_t(s)<=g_t(s,a)+K_t^a u_(t+1)(s)` with u_N=0 give a lower bound mu u_0 on
EVERY admissible policy in that finite model. Multiply by each state-action
occupation and telescope to prove it. Equality on occupied actions certifies
optimality. A scalar threshold's gap above the bound is its measurable policy
restriction loss. Numerical state aggregation without an error bound does not
certify the original history model.

The same-length opposite-action simulator counterexample establishes that X
alone is not generally sufficient. The boundary advantage therefore depends
on versions, cache state and future work; a scalar sweet point can average
opposite preferences across states. The next substantive theorem would find
conditions making that advantage monotone in X, rather than presume such a
threshold theorem from a plotted bowl.

### A whole parameter region, not an isolated numerical counterexample

With one ordinary action remaining and cold cache, let both states have length
X. A has a valid required file; B lacks it. The file has size D and is required
with the SAME conditional probability alpha. Compaction erases the valid
snapshot and rebuilds base B plus summary S. Its instruction has c tokens.
Assume X>=B+D so the valid snapshot fits, and all input is eligible for cache
writes. Ordinary common background, suffix and
output cancel in the comparison. SymPy derives

```
T = p_i*(X+c) + p_w*(B+S-X) + p_o*S
compact_minus_keep_missing = T
compact_minus_keep_valid = T + alpha*D*p_w.
```

Therefore the OPEN region `-alpha*D*p_w < T < 0` requires compact for the
missing-file state and continue for the valid-file state. The width is the
expected replacement-write option alpha*D*p_w, not a claim that all future
file value is universally additive. This region explains the exact numerical
counterexample and remains a structural statement as its parameters change.
Additional recovery-model overhead, prefix survival and more remaining actions
replace these one-stage expressions by the full Bellman advantage, rather than
invalidate the general insufficient-state mechanism.

## Reproduction and proof scope

```
uv run python experiments/threshold_operator_analysis.py
uv run python experiments/structural_symbolic_analysis.py
uv run python experiments/structural_control_counterexample.py
uv run pytest tests/test_control_symbolics.py tests/test_structural_symbolics.py tests/test_structural_control_counterexample.py -q
powershell -File formal/verify.ps1
uv run python experiments/summarize_structural_theory.py
```

Generated formulas/ledgers/audits remain in .cache. Maintained English notes
state premises, exact counterexamples and references. SymPy checks explicit
finite expressions, Lean checks finite ledger/expectation/price/loop laws;
general measurable-state regularity and globally optimal production policies
have not been formalized or inferred. The old 126k result remains a historical
controlled numerical scenario, not a theoretical recommendation.

Published [structural metadata](structural-results.json) contains exact
expressions, zero symbolic residuals and the primal/dual certificate. An
independent endpoint/tail verifier checks 2,196 rational inequalities against
all 122 extracted price lines across all nine lower-envelope intervals.
Those inequalities certify the ENTIRE nonnegative read/write ratio axis in
that declared candidate family, rather than just its sampled price points.
The initial 21 Lean declarations were rechecked by the installed 4.33.1 kernel;
the continuum bridge adds a 22nd approximation-to-optimization transfer law.
Initial structural integration: 325 Python tests passed; Ruff passed.
