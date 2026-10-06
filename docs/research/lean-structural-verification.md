# Kernel-checked structural accounting and price geometry

Date: 2026-10-06. Maintained source: `formal/Structural.lean`.

## What was actually verified

Lean 4.33.1 checked 25 theorem declarations (22 structural/results laws and three finite-sum helpers) against its kernel. The file imports
only `Std`, without Mathlib, custom axioms, admitted proofs, or unsafe evaluation
as a proof substitute. Two deterministic fixture inequalities use `decide`, whose
finite computation produces kernel-checked proof terms.

The verification command completed with exit code zero, no warnings, and printed
all theorem axiom dependencies. Standard Lean dependencies were `propext`, `Quot.sound`, and `Classical.choice`
(the last occurs in the integer gate arithmetic and its dependent theorems).
There were no `sorryAx` dependencies.
These standard foundational axioms must not be confused with axiom-free arithmetic:
the two fixture inequalities and the zero-sum helper were reported as depending on no axioms at all.

## Domain and interpretation

A ledger is `Fin 4 -> Nat`, representing input, write, read, and output quantities.
Prices use nonnegative integer units. Any finite set of rational nonnegative prices
can be represented exactly by multiplying by a common positive denominator;
dividing invoice numerators by that denominator preserves equalities and order.
This rational reinterpretation is explained here, not a separately formalized
real-number division theorem.

Finite probability laws use nonnegative integer weights `w(x)`. The weighted ledger
numerator is `sum_x w(x) a(x)`. Dividing by `sum_x w(x) > 0` gives the normalized
expectation. The kernel verifies numerator linearity, not normalization positivity,
measure-theoretic integration, or exchange of infinite limits.

Ledger quantities are allowed to depend on every state variable and correlated
random event in the implementation. The algebra does not assume independence,
fixed reset size, an iid trajectory, or a constant reload quantity. Price geometry
requires the candidate ledgers to remain fixed while prices vary: changing the
policy in response to prices belongs in the optimization over candidates, not in
a purported fixed-policy derivative.

## Checked laws and their research use

| Lean declaration | Checked statement | Structural implication |
| --- | --- | --- |
| `invoice_compose` | `p dot (a+b) = p dot a + p dot b` | Every cost attribution must reconcile with the same four-component total. |
| `price_monotone` | `p <= q` implies `invoice(p,a) <= invoice(q,a)` | A fixed trajectory cannot become cheaper when nonnegative prices rise. |
| `ledger_monotone` | `a <= b` implies `invoice(p,a) <= invoice(p,b)` | Pareto-dominated expected ledgers can be removed before comparing prices. |
| `invoice_price_add` | `invoice(p+q,a) = invoice(p,a)+invoice(q,a)` | Fixed-policy cost is linear in the price vector. |
| `invoice_price_scale` | `invoice(k*p,a) = k*invoice(p,a)` | Common price scaling changes costs but not preferred policies. |
| `minimizer_price_add` | One candidate minimizing at both p and q also minimizes at p+q. | Optimal-policy price regions are closed under nonnegative rational combinations when combined with scaling. |
| `minimizer_price_scale` | A minimizing candidate remains minimizing at k*p. | Those regions are cones, rather than isolated price-point observations. |
| `optimized_price_superadditive` | `min_a p.a + min_a q.a <= (p+q).candidate` for every candidate. | The optimized lower envelope is superadditive and homogeneous, giving its concave price geometry under rational convex combinations. |
| `repriced_optimal_usage` | Raising one positive price component, then reoptimizing, weakly decreases optimized usage of that component. | Revealed preference orders resource usage, not compact thresholds. |
| `expected_invoice` | `p dot sum_x w(x)a(x) = sum_x w(x)(p dot a(x))` | Arbitrarily dependent finite task laws reduce to an expected ledger for price comparison. |
| `occupancy_exchange` | `sum_t sum_j resident(t,j) = sum_j sum_t resident(t,j)` | A request-centered cache-residency bill can be attributed to artifact lifetimes exactly. |
| `rational_cell_gate` | For integer x and a rational trigger in (k-1,k], num <= x*den iff k <= x. | Threshold gating depends on the ceiling, not on the sub-token position. |
| `tree_cell_ledger` | Every arbitrary finite threshold decision tree has the same ledger throughout a ceil cell. | Branch-dependent recovery and arbitrary future integer contexts do not invalidate quantization. |
| `same_cell_ledger` | Two rational triggers in the same cell return the identical ledger. | Exact schedule equivalence, not merely statistically indistinguishable costs. |
| `tree_cell_invoice` | Equivalent cell ledgers have the same invoice at every price. | In-cell price differences are identically zero. |
| `expected_tree_cell` | The weighted expected ledger is also constant in a cell for any fixed finite task law. | No independence or iid hypothesis is necessary. |
| `approximation_optimization_transfer` | Uniform surrogate error <= epsilon implies a surrogate minimizer has exact regret <= 2 epsilon. | Continuous or simplified models can guide the original optimization when an actual uniform error bound is supplied. |
| `renewal_adjacent_average` | Adding a positive atom at x lowers (A+cM)/U iff c*x*U <= A+cM. | Exact marginal condition for renewal-average threshold optimization. |
| `renewal_lag_advance` | After adding mass w at x and advancing by positive gap, lag increases by gap*(U+w). | Strictly growing cumulative lag underpins a single-crossing condition rather than a simulated minimum. |
| `strict_obstruction` | Every finite number of strict housekeeping steps fails to reach execution if restored size >= trigger. | A threshold can be infeasible independently of prices or request counts. |
| `threshold_not_decreasing` | Six-action fixture cost at h=3 is lower than at h=4. | Increasing the threshold is not universally cost-improving. |
| `threshold_not_increasing` | The same cost at h=3 is lower than at h=2. | Nor is decreasing it universally cost-improving. |

The cone and concavity interpretation follows from these integer algebra laws plus
common-denominator conversion. This file does not define topological closedness,
normal fans, or real convex sets, and does not claim Lean verified those definitions.

The occupancy identity accepts arbitrary nonnegative entries. Choosing
`resident(t,j) = d_j * 1{artifact j is resident at request t}` gives total carried
tokens as the sum of weighted artifact lifetimes. Actual cache-hit weights can be
included in the entries. The identity alone does not assert that every resident
token is cached, nor establish a particular cache replacement mechanism.

## Price increases under reoptimization: revealed preference

`repriced_optimal_usage` considers an old optimal policy and a policy optimal after
one component price increases by delta > 0. Let b0 and b1 be their invoices at the
original prices, and u0 and u1 their usage of the repriced component. Exact optimality
supplies the two inequalities

```
b0 <= b1,    b1 + delta*u1 <= b0 + delta*u0.
```

Lean derives `u1 <= u0`: replace the new policy's baseline b1 with the lower old
baseline b0, cancel the common baseline, and cancel the positive multiplier delta.
The proof is general order and arithmetic reasoning; it is not a pair of numerical
fixtures. Its axiom audit reports only the standard `propext` dependency.

For fixed correlated finite task weights, u is an expected ledger numerator and b
is the corresponding expected invoice numerator. Clearing common positive rational
denominators gives exactly the same usage ordering. The old and raised-price
optimizations must use the same feasible policy set, external task law, and ledger
semantics, with only one component price changed. Approximate solver optimality,
sample-selection error, changed task distributions, changed providers, and changed
feasibility contracts are not covered by the exact hypotheses.

Importantly, the theorem does not say that the chosen compact trigger increases or
decreases. A policy can change other controls or switch branches while reducing
only the repriced resource. Other ledger coordinates may rise. The threshold itself
can move in either direction; resource monotonicity is the robust structural law.
Together with price homogeneity and optimized-price superadditivity, this provides
finite/rational support for the lower-envelope interpretation of optimized costs.
No real-valued envelope derivative, differentiability, or full analytic sensitivity
model is formalized here.
## Central threshold quantization theorem

Represent a positive trigger exactly as `num / den`, with `den > 0`, and let k be
its ceiling. The cell assumptions are `(k-1)*den < num <= k*den`. For every natural
context size x, Lean proves

```
num <= x*den  <->  k <= x.
```

This is not limited to one fixed-growth cycle. `ThresholdTree` has terminal ledger
leaves and internal nodes carrying an integer context x and two arbitrary subtrees:
compact and proceed. Nodes in different branches may have completely different
future x values and terminal ledgers. The tree can encode all finite unrolled state
transitions after fixing a task's external event sequence, including correlated
observations and recovery-dependent context growth.

Structural induction proves `tree_cell_ledger`: evaluating any such tree with the
rational gate produces exactly the ledger obtained using the integer gate k.
`same_cell_ledger` then proves equality between two rational triggers, including
triggers with different denominators, in the same cell. `tree_cell_invoice` turns
ledger equality into invoice equality for every price vector. `expected_tree_cell`
lifts the pathwise equality to arbitrary finite nonnegative weighted task laws.

Assumptions matter: the decision tree must be threshold-independent before its
gates are evaluated. All threshold dependence must enter through integer context
comparisons. A continuous threshold directly used to choose summary size, retention
budget, recovery delay, prices, or stochastic event distributions is outside this
representation unless those additional choices are separately quantized and encoded.
Finite loop limits can be unrolled, but unbounded recursion is outside the tree type.
The leaf type here is a ledger, not a feasibility flag: this proof does not turn a
truncated failed task into a valid full-task invoice.

Consequently, in this model class, searching fractional-token triggers gives no
additional policies. Ordinary real derivatives within cell interiors would be zero
for the real extension, while jumps need discrete differences or distributional
analysis. The Lean proof establishes exact rational cell constancy, **not** a
formalized real derivative or a measure-theoretic derivative theorem. The extension
from arbitrary pointwise equal outcomes to an infinite correlated task law is a
separate standard integration argument, not a theorem checked in this finite file.

No claim is made that the Python simulator has been mechanically translated into
this tree representation. The theorem verifies a broad finite threshold-program
abstraction with clearly stated interface assumptions, not simulator refinement.
## Uniform approximation and optimization transfer

The discrete threshold theorem is not an argument against continuous distributions
or continuous analysis. A physically finite system may admit a useful continuous
approximation. The relevant mathematical obligation is to control approximation
error sufficiently to transfer the resulting decision back to the exact system.

`approximation_optimization_transfer` handles arbitrary candidate type alpha and
arbitrary nonnegative cost functions E (exact) and A (approximate). Suppose, for
every candidate x, the two-sided uniform error assumptions are

```
E(x) <= A(x) + epsilon,    A(x) <= E(x) + epsilon.
```

If chosen minimizes A over the same candidate domain, Lean proves, for every y,

```
E(chosen) <= E(y) + 2*epsilon.
```

The proof composes E(chosen) <= A(chosen)+epsilon <= A(y)+epsilon <=
E(y)+2epsilon. It is general cost-map algebra, not a numerical example. Natural
numbers represent common rational numerator units; division by a common positive
scale gives the corresponding rational cost bound. The file does not formalize
real-valued function spaces, absolute values, a continuum limit, or integration.

Crucially, this theorem does **not** establish a uniform epsilon for the simulator,
a diffusion approximation, a smoothed threshold objective, or a fluid control
model. It says what a successfully established error bound would buy: an explicit
original-system regret guarantee rather than an imagined surrogate optimum. The
candidate sets must coincide; discretizing or projecting a continuous minimizer
onto a different feasible set requires a separate additional bound.
## Renewal-average marginal comparison and cumulative lag

For a finite renewal measure, let U > 0 be accumulated pre-crossing mass, M its
nonnegative first-location moment, A a nonnegative reset surcharge, and c a
nonnegative carry price. Adding a positive mass w > 0 at location x updates
(U,M) to (U+w,M+x*w). The old and new average numerators/denominators are

```
old = (A+c*M)/U,    new = (A+c*(M+x*w))/(U+w).
```

`renewal_adjacent_average` proves the exact cross-product comparison

```
(A+c*(M+x*w))*U <= (A+c*M)*(U+w)
    <-> c*x*U <= A+c*M.
```

The difference of the cross products is governed by the positive atom w and the
marginal advantage `c*(x*U-M)-A`. The formal proof does not represent a negative
advantage using saturating natural subtraction: it expands both nonnegative cross
products, cancels their common term, and cancels positive w. Positive U is included
as a semantic precondition for ratio interpretation, although the cross-product
algebra itself does not need that hypothesis. Fractions and positive-denominator
order conversion are not separately encoded as Lean rational-number operations.

For cumulative lag D = x*U-M, require M <= x*U, which holds when the accumulated
measure is supported at locations no greater than x. Adding mass w at x gives it
zero initial lag. Advancing to x+gap, with gap > 0, then gives

```
D_new = (x+gap)*(U+w) - (M+x*w)
      = (x*U-M) + gap*(U+w) > x*U-M.
```

`renewal_lag_advance` verifies both this identity and strict increase. Here natural
subtraction is safe because its nonnegative-lag precondition is explicit; it is
not used for a potentially negative optimization advantage.

These are general atomic renewal-average laws, not numerical fixtures. With a
positive carry price, strictly increasing cumulative lag supplies the algebraic
basis for a marginal condition that crosses a fixed reset surcharge at most once.
The source does not construct a renewal measure from an iid increment distribution,
prove existence of the crossing, identify all boundary minimizers, or formalize
continuous integration or differentiability. Those analytic steps remain separate
from the checked finite/rational comparison structure.
## Strict-loop theorem: explicit transition assumptions

The abstract controller has three phases: `missing`, `ready`, and `done`.
Restoration moves `missing -> ready`. In `ready`, the strict controller rechecks
whether `h <= restoredSize`. If true, compaction erases the prerequisite and returns
to `missing`; otherwise it executes and reaches `done`. `done` is absorbing.

By induction over an arbitrary number of microsteps, `h <= restoredSize` implies
that starting from `missing` never reaches `done`. The proof is general in h,
restored size, and attempt bound. It formalizes the contract's repeated prerequisite
erasure scenario, not every possible strict controller: atomic read/edit operations,
retaining the prerequisite, or permitting overshoot break its assumptions.

## Deterministic threshold counterexample

For six ordinary actions, context starts at zero and grows by one after each action.
An action pays current context occupancy. Before an action whose current length
reaches h, context resets to zero and adds an overhead of four. Exact invoices are:

| Trigger h | Invoice |
| --- | ---: |
| 2 | 11 |
| 3 | 10 |
| 4 | 11 |

The two inequalities are kernel-checked finite computations. They refute universal
monotonicity, not smoothness over the real line. Integer triggers have a discrete
domain; a real-threshold extension would need a separate definition and proof.
This fixture is a mechanism counterexample, not a calibrated optimum prediction.

## Reproduction and boundaries

From the repository root, with an already installed Lean executable:

```powershell
./formal/verify.ps1
```

The script writes only `.cache/lean/Structural.olean` and
`.cache/lean/verification.log`. It performs no dependency download and no toolchain
installation. Direct equivalent: `lean -o .cache/lean/Structural.olean formal/Structural.lean`.

The result does **not** prove Python/Lean refinement, simulator accounting correctness,
continuous threshold derivatives, stochastic optimal-control existence, a globally
optimal experimental threshold, or general measure-theoretic expectation identities.
Those questions require their own contracts and proofs. The useful contribution here
is a verified finite structural layer shared by richer stochastic/control models,
not an attempt to certify the entire research project by attaching a proof assistant.
