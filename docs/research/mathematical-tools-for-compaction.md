# Mathematical tools for stateful context compaction

Recorded 2026-10-06. This extends
[compaction-model-selection.md](compaction-model-selection.md), rather than
repeating its method list. The decision is how to obtain structural statements
and correct sensitivities for a finite task with dependent events. A fitted
Gamma marginal or a Monte Carlo minimum is not the mathematical answer.

The core deliverables proposed here are now executed in v0.3: see
[threshold/operator theory](threshold-operator-theory.md),
[exact symbolic analysis](structural-symbolic-analysis.md),
[joint-law control and LP certificate](general-stochastic-control-theory.md),
and [kernel-checked Lean scope](lean-structural-verification.md).

## 1. Decision: an exact control representation before a distribution family

The primary object is a finite-horizon controlled stochastic process on a
measurable history/state space. Ordinary action boundaries are the clock;
compaction and recovery can be folded into a macro-transition only if their
complete costs, delays, failures and state changes are retained. A hybrid or
impulse-control representation is appropriate when these events must be
resolved individually.

Choose the following hierarchy:

1. **History-state control and occupancy measures:** retain an arbitrary joint
   conditional law, prove accounting and policy-comparison identities, and
   expose when a scalar threshold is an insufficient policy restriction.
2. **Nonsmooth threshold calculus:** first use exact policy differences and
   signed derivative measures; specialize to a boundary-density derivative
   only after establishing regularity.
3. **Adjoint/backward value propagation:** compute the *full future value* of
   changing a decision, not just its immediate invoice.
4. **Continuous hybrid sensitivity:** use saltation/event-time corrections only
   for a justified differentiable fluid approximation. Do not backpropagate
   through discrete token threshold comparisons as if they were smooth.
5. **Renewal, queueing and scalar closed forms:** reductions with explicit
   regeneration/scaling assumptions, not the foundation of the general model.

These are not five competing ways to invent marginal distributions. They are
compatible representations of probability flow, cost-to-go, event boundaries
and restricted special cases.

## 2. Dependence is represented by conditional kernels, not many iid draws

Let H_t contain the observations and decisions available before ordinary action
t. Let a_t be continue or compact, with a restoration/retention action if the
policy controls it. The law is K_t(dh' | h,a), and the expected macro-cost is
l_t(h,a). These objects include correlation between demand, output, mutation,
cache survival and the task phase. There is no independence assumption in

V_t^pi(h) = l_t(h,pi_t(h)) + integral V_(t+1)^pi(h') K_t(dh'|h,pi_t(h)),

with V_N=0 when there is no terminal charge.

The full history is always a safe state representation for the specified
conditional law. A smaller state S_t=phi(H_t) is valid only if, for every
admissible action, conditional next-state and cost laws agree for all histories
mapped to the same S_t. A tuple of token length, live files and cache age does
**not** become sufficient merely because those variables are convenient.
Unobserved phase may require a belief state; an action-dependent output law
must be kept action-dependent. A fixed-trace intervention instead declares
ordinary work invariant under the policy, and studies a narrower estimand.

An arbitrary joint law does not mean arbitrary independent marginals. It also
does not mean it can be inferred from existing aggregate data: the law is an
explicit input/assumption, and structural claims should distinguish those
holding for every law from those requiring regularity or particular dynamics.

### 2.1 Impulses do not consume an ordinary-work tick

There is an important modeling distinction hidden by a simulator's event loop.
If compaction alone does not complete an ordinary action, it must not silently
decrement the remaining horizon. Define the continuation operator

C_t V(s) = ordinary_cost_t(s) + integral V_(t+1)(s') K_t^ordinary(ds'|s)

and an intervention operator, including all reset randomness and delay,

M_t V(s) = inf_k [reset_cost_t(s,k) + integral V_t(s') R_t(ds'|s,k)].

Then the optimal cost satisfies V_t=min(C_t V, M_t V), with the intervention
branch evaluated at the SAME ordinary-work index t. This is an obstacle/fixed-
point problem unless intervention is fully folded into a macro-action that
subsequently completes one ordinary step. The impulse cost includes compactor
input/output and restoration calls; the reset kernel carries cache and file
state. History-dependent reset laws belong in R_t, not a constant reset size.

Admissibility must exclude infinite reset loops that complete no work. If each
impulse costs at least kappa>0, every policy with finite expected cost has
expected impulse count at most J/kappa; infinite impulses with positive
probability imply infinite cost. A strict threshold below its reconstructed
working set can therefore be infeasible, rather than a cheap early termination.
Positive-cost impulse assumptions in [R1] address this kind of issue; our
finite-work completion contract must still be stated separately.

In a justified continuous-time approximation, the corresponding obstacle
equation couples a generator-based continuation equation with M V-V. This is
the origin of an impulse-control quasi-variational inequality, not a reason to
assume a diffusion or smooth generator exists for the discrete token system.

## 3. Occupation measures: probability conservation and an LP dual certificate

The following finite-state derivation is self-contained. It extends to suitable
Borel spaces using measures, but existence/disintegration/duality then need
additional conditions.

Define m_t(s,a)=P(S_t=s,A_t=a) and initial distribution mu. For t=0,...,N-1:

sum_a m_0(s,a) = mu(s),

sum_a m_(t+1)(s,a) = sum_(z,b) m_t(z,b) K_t(s|z,b).

Then the task invoice is a linear functional:

J(pi) = sum_(t,s,a) m_t(s,a) l_t(s,a).

Optimizing over nonnegative m subject to these conservation equations is a
finite-horizon linear program for randomized Markov policies. Recover a policy
by normalizing each positive state marginal. Hard threshold policies are a
restricted, generally nonconvex subset of these feasible measures: replacing
threshold selection with this LP changes the policy class, and must be labeled.

The dual uses functions u_t(s), u_N=0, satisfying

u_t(s) <= l_t(s,a) + sum_s' K_t(s'|s,a) u_(t+1)(s')

for every feasible action. Multiplying by m and telescoping proves

sum_s mu(s) u_0(s) <= J(pi).

Thus an approximate value function with *verified Bellman inequalities* gives
a lower bound on every policy, not just another noisy curve. The gap between
a threshold policy's invoice and this bound measures how much room remains
for improvement. At an optimum, positive-occupancy actions have zero dual
slack. This is the structural link between occupation geometry and Bellman
optimality.

The corresponding four-price accounting is J(pi;p)=p dot q(pi), where q(pi)
is expected input/write/read/output exposure. For a fixed policy and price-
independent dynamics, its price gradient is exactly q(pi). Comparing two fixed
policies produces a half-space p dot(q(pi)-q(pi'))<=0. Over finitely many
candidates, price-optimal regions are polyhedral and the lower-envelope value
is concave in prices. These facts require no Gamma fit and no smoothness in h.
Price-dependent agent behavior would invalidate the fixed-q premise.

Peer-reviewed impulse-control work establishes occupation-measure LPs and
strategy recovery under specific assumptions, including positive impulse costs
and regularity of the dynamical system. It supports this tool choice, not an
automatic strong-duality claim for our unbounded history space. [R1]

## 4. Policy differences reveal the missing term in a threshold derivative

Use cost-minimization notation

Q_t^pi(s,a) = l_t(s,a) + K_t^a V_(t+1)^pi(s),

A_t^pi(s,a) = Q_t^pi(s,a)-V_t^pi(s).

For two policies with the same initial law and conditional environment kernels,
telescoping conditional expectations gives the exact finite-horizon identity

J(pi')-J(pi) = sum_t E_(pi')[A_t^pi(S_t,A_t)].

Proof: expand Q-V, sum the stage costs, and cancel successive V terms using
the transition law. The initial V expectation is J(pi), and V_N=0. This proof
needs integrability but neither independence nor differentiability. A changed
environment law requires a separate kernel-change term.

For deterministic thresholds, compact iff x(s)>=h. Raising h to h+epsilon
changes the action only in the slab h<=x<h+epsilon. Therefore

J(h+epsilon)-J(h)
 = sum_t integral_(h<=x<h+epsilon)
     [Q_t^h(s,continue)-Q_t^h(s,compact)] nu_(t,h+epsilon)(ds),

where nu_(t,h+epsilon) is the predecision state distribution under the NEW
threshold. This is exact even when all future crossings change. It is not the
same as counting immediate saved cache reads in that slab.

If nu has a density rho_(t,h)(x,z), the slab average has a well-defined trace,
and perturbed occupancy converges with enough uniform integrability, then

J'(h) = sum_t integral rho_(t,h)(h,z)
    [Q_t^h(h,z,continue)-Q_t^h(h,z,compact)] dz.

The derivative is boundary visitation density times **full future decision
advantage**. Occupancy dependence has not been ignored: it is absorbed by the
exact telescoping identity before taking the limit. A scalar optimum can balance
opposite advantages across different cache/file states even though a state-aware
policy could choose the better action at each state. This exposes a potential
structural limitation of the scalar threshold, not a new universal optimum.

For a differentiable score g(s) rather than x, coarea calculus replaces the
integral with a surface integral on g(s)=h, weighted by 1/||grad g||. This
requires a genuine continuous state density and a regular level surface.
Integer-token atoms do not satisfy these premises. There, finite contrasts and
the signed distributional derivative of J are the primary objects; a sampled
path's almost-everywhere zero derivative is not an unbiased gradient.

## 5. Weak differentiation and adjoints: what SymPy can and cannot do

For a differentiable kernel parameter theta, with initial law fixed, define
nu_t=mu K_(0,theta)...K_(t-1,theta). Differentiating the backward recursion and
telescoping gives

dJ/dtheta = sum_t nu_t [d l_(t,theta)/dtheta
                      + (d K_(t,theta)/dtheta) V_(t+1,theta)].

This is a forward-occupancy/backward-value adjoint identity. Finite matrices
make it exactly symbolic; arbitrary dependence is preserved by the matrices or
history kernels. Signed kernel derivatives can be evaluated by their positive
and negative parts, suggesting coupled branch/phantom estimators rather than
finite differences through invalid smooth arithmetic.

Heidergott and Vazquez-Abad give a finite-horizon product rule for measure-valued
kernel differentiation, with test-function and integrability conditions. [R2]
However, for a deterministic threshold at a fixed s, K_h(s,.) is itself a step
function of h: ordinary pointwise differentiability hypotheses fail. The hard
threshold requires the slab/distributional treatment above, or a *declared*
randomized smooth controller. A smooth sigmoid controller is a different
policy, not a proof that the original derivative exists.

Use SymPy for finite-state kernel recursions, exact exposure coefficients,
price-region boundaries, and rigorously derived continuous special cases. It
cannot prove an interchange of derivative and expectation merely by applying
diff() to an expected-value symbol. Use Lean for finite sums, conservation,
telescoping and exact rational examples first; measure-theoretic assumptions
must be formalized rather than hidden behind an axiom named 'regularity'.

The 2026 peer-reviewed stationary IPA paper explicitly requires differentiable
kernel/input structure and stability bounds to interchange limiting operations.
Its worked recursive model uses independent iid input streams. It is useful
for checking assumptions, not a license to import a stationary IPA estimator
into our dependent finite task. [R3]

## 6. The legitimate vector-calculus / field connection

Probability occupancy is a field over state space, not physical space. In a
continuous approximation with drift b_a and jumps, a forward equation can have
the form

partial_t rho + div(b_a rho) = jump_gain - jump_loss.

At a continuous threshold surface, probability exits via a normal flux and is
reinjected through a reset kernel. Occupation conservation in Section 3 is the
discrete analogue. The adjoint equation transports future cost backward. These
are real links to vector calculus and conservation laws.

They do **not** establish a spatial geometry, locality, differentiable file
identity, or a thermodynamic energy. A classical field theory or stochastic PDE
is not justified just because there are many random variables. A measure on
file/version configurations with jump kernels is normally more faithful than
a fictitious Euclidean field. A diffusion limit needs an explicit scaling of
small increments and control of jump/overshoot errors; rereading a 20k file is
not automatically a small-noise fluctuation.

For a smooth deterministic hybrid approximation, event timing matters. With
guard g(x,t)=0, reset R(x,t), vector fields f-/f+, the state-perturbation update
is the saltation matrix

Xi = D_x R + [(f+ - D_x R f- - D_t R) D_x g]
                / [D_t g + D_x g f-].

The second term accounts for perturbed event time. It vanishes neither because
the reset is known nor because automatic differentiation can differentiate R.
The 2024 Proceedings of the IEEE review requires differentiable guards/reset
maps and transversal crossings, and explains why grazing/intersecting guards
need other analysis. [R4] Our integer-token discrete requests do not meet this
continuous crossing model. Use this only to validate a future fluid model,
not as an ornamental matrix added to the current simulator.

## 7. When renewal and queueing are legitimate

A compaction is not regeneration if task phase, file versions or stable cache
state carry over. Iid renewal-reward requires the post-reset future to restart
from the same law independently of the past. Under that condition a long-run
cost per ordinary action is E[cycle invoice]/E[cycle actions]. A Markov-renewal
model can carry a reset-state chain instead, provided its stationary law and
ergodicity exist. Neither ratio is the exact finite-N invoice with terminal
effects. Queueing analogies can explain setup-versus-holding exposure, but a
queue with exogenous arrivals does not automatically describe recovery that
both costs tokens and changes the next compaction stopping time.

The mathematical question worth answering is: which transition features are
needed for monotonic compact-vs-continue advantage, and hence a valid scalar
threshold theorem? Without such conditions, equal x can hide different live
file values and cache states, and threshold optimality must not be presumed.

## 8. Production reality and academic frontier

| Evidence | What it establishes | Mathematical consequence / transfer limit |
| --- | --- | --- |
| Claude Code engineer, 2026-04-30: cache-safe compaction forks, prefix identity, reattached files, figure with approximately 20k summary [R5] | Implementations can avoid an uncached full-history compactor invoice by preserving the parent prefix; reset content is not merely a scalar | Kernel must carry prefix identity and fork action. The old S=4382 scenario is not this product's documented default. No universal summary-size claim follows. |
| Anthropic context engineering, 2025-09-29: compaction preserves selected information and recently accessed files; external notes can be reloaded [R6] | Logical usability and retained material are policy-dependent | Restore/retain is an action, not an independently fitted reset-size draw. Its effect on task quality needs a separate law/constraint. |
| CDMem, NAACL Industry 2025, inspected full paper [R7] | Context-dependent task/environment memory and retrieval are tested on 134 ALFWorld environments and 50 ScienceWorld tasks | Supports phase/environment-dependent state representations. These are not four-price engineering compaction thresholds; success results do not identify our joint event law. |
| Active Context Compression, 2026-01 arXiv preprint [R8] | Model-directed memory management explored on five SWE-bench Lite instances | Motivates endogenous control, but the tiny evaluation and preprint status cannot validate threshold optimality or a distribution family. |
| Hybrid saltation review, peer reviewed 2024 [R4], and stationary IPA, peer reviewed 2026 [R3] | Modern tools connect event sensitivities and stochastic-gradient regularity | Ready as mathematical tools when assumptions hold; not ready-made LLM context models. |

### Concrete next theoretical deliverable

Prove the finite-horizon occupancy and performance-difference identities for
the actual four-price ledger. Derive signed threshold sensitivity without
assuming independent marginals. Then construct a finite-state dependent law
with exact SymPy cost-to-go, exposing when same-length states require opposite
decisions. Compare a threshold to a state-aware policy using an LP dual bound.
These deliver mechanisms and certificates even if no globally smooth sweet
spot exists. Simulation should test these results, not substitute for them.

## References and access record

All sources checked 2026-10-06. Source claims above are separated from our
self-contained finite-horizon derivations and proposed applications.

- **R1:** Piunovskiy, A.; Zhang, Y. (2021). *Aggregated occupation measures and
  linear programming approach to constrained impulse control problems*.
  Journal of Mathematical Analysis and Applications 499(2), 125070.
  [DOI](https://doi.org/10.1016/j.jmaa.2021.125070).
  [Author preprint, full PDF inspected](https://arxiv.org/pdf/2010.04601).
- **R2:** Heidergott, B.; Vazquez-Abad, F. (2008). *Measure valued
  differentiation for Markov Chains*. Journal of Optimization Theory and
  Applications 136, 187-209. [DOI](https://doi.org/10.1007/s10957-007-9297-7).
  [University record](https://research.vu.nl/en/publications/measure-valued-differentiation-for-markov-chains/).
  [Accessible earlier finite-horizon report, inspected](https://www.eurandom.tue.nl/reports/2000/033-report.pdf).
- **R3:** Heidergott, B. (2026). *IPA for stationary problems*.
  Discrete Event Dynamic Systems 36, article 12, published 2026-03-27.
  [Open full text](https://doi.org/10.1007/s10626-026-00438-9).
- **R4:** Kong, N.J.; Payne, J.J.; Zhu, J.; Johnson, A.M. (2024).
  *Saltation Matrices: The Essential Tool for Linearizing Hybrid Dynamical
  Systems*. Proceedings of the IEEE.
  [DOI](https://doi.org/10.1109/JPROC.2024.3440211).
  [Author manuscript, full text inspected](https://arxiv.org/html/2306.06862v3).
- **R5:** Shihipar, T. (2026-04-30). *Lessons from building Claude Code:
  Prompt caching is everything*. First-hand Claude Code engineering report.
  [Official report](https://claude.dev/blog/lessons-from-building-claude-code-prompt-caching-is-everything/).
- **R6:** Anthropic (2025-09-29). *Effective context engineering for AI agents*.
  [Official engineering report](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- **R7:** Gao et al. (2025). *An Efficient Context-Dependent Memory Framework
  for LLM-Centric Agents*. NAACL Industry Track.
  [Proceedings and PDF](https://aclanthology.org/2025.naacl-industry.80/).
- **R8:** Verma, N. (2026). *Active Context Compression: Autonomous Memory
  Management in LLM Agents*. arXiv preprint, v1 2026-01-12; abstract/method
  scope inspected, no peer-review status asserted.
  [Primary manuscript record](https://arxiv.org/abs/2601.07190).
