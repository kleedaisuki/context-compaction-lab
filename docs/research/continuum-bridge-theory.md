# Finite systems, continuous laws, and a controlled continuum bridge

Date: 2026-10-06. This corrects an overemphasis in the preceding threshold
analysis: exact integer structure is NOT an argument against continuous
probability, macroscopic derivatives, or continuum control. It is the
microscopic reference against which those models must be justified.

## 1. Continuous mathematics is not an ontological assertion of infinite matter

A finite sample, a finite state space and an infinite mathematical model are
different objects. Continuous laws model interval probabilities and expected
losses at a chosen resolution. They need not assert that infinitely many
physical states are realized, or that one random outcome realizes an infinite
collection of alternatives. Whether the physical universe is finite is not a
premise needed by this modeling argument.

For example, if Y_m is uniform on the m midpoints of [0,1], its CDF differs
from Uniform[0,1] by at most 1/(2m). Every approximating law has only m states.
Couple it to U~Uniform[0,1] by rounding U to its cell midpoint. Then

```
E|U-Y_m| = 1/(4m),
|E f(U)-E f(Y_m)| <= Lip(f)/(4m).
```

This proves the usefulness of a continuous law for every finite sufficiently
large m and Lipschitz loss f. The infinite limit organizes finite error bounds;
the real system does not have to reach infinity. Normal approximations to
finite binomial counts and fluid limits of discrete jump systems are other
instances, with their own assumptions. Neither independence nor a diffusion
law follows just from having many tokens.

## 2. A zero microscopic derivative can converge to a useful macro derivative

For a differentiable Lipschitz function f and quantum delta, define the right-
closed staircase f_delta(h)=f(delta*ceil(h/delta)). Then

```
sup_h |f_delta(h)-f(h)| <= Lip(f)*delta.
```

Every f_delta has ordinary derivative zero between grid points. Nevertheless,
its signed derivative measure has jump weights
`f((k+1)*delta)-f(k*delta)` at k*delta. On any bounded region, these measures
converge weakly to `f'(h) dh` under the usual regularity and boundary treatment.
The coefficients are approximately delta*f'(k*delta), giving a Riemann sum.
An elementary example is f(h)=a*h+b*h^2/2+c, whose exact jump is
`a*delta+b*k*delta^2+b*delta^2/2`.

Thus taking the classical microscopic derivative first and passing to the
limit loses the macroscopic slope. The earlier signed derivative is a BRIDGE
to continuous sensitivity, not an excuse to end the analysis. Continuous laws,
continuous states, continuous sample paths and a differentiable objective
must also be distinguished: a continuous-state jump process can retain jumps
and atomic reset distributions.

## 3. Continuous budget uncertainty gives an exact smooth response

Let J(h) be the original complete-task expected bill, including all endogenous
reloads, changed crossing times, cache expiry and output carries. Extend it
constantly below its minimum admissible threshold. Draw ONE independent budget
offset per whole task, and keep that threshold throughout execution:

```
H=max(1,h+sigma*Z), Z~Normal(0,1), sigma>0,
J_sigma(h)=E_Z[J(H)].
```

For a finite exact step curve with left-tail value J_0 and jumps Delta_j at b_j:

```
J_sigma(h)=J_0+sum_j Delta_j*Phi((h-b_j)/sigma),
J_sigma'(h)=sum_j Delta_j*phi((h-b_j)/sigma)/sigma.
```

This is convolution of the signed jump measure with a Gaussian density.
It yields an exact continuous sensitivity for a declared uncertain-budget or
randomized-threshold controller, without discarding any system dependence.
The interpretation matters: independently resampling a threshold at each
request is a DIFFERENT policy and is not represented by this convolution.
Random summary/file sizes at each reset are also different joint dynamics.
Their whole conditional kernel must change; they are not automatically
equivalent to a single threshold offset.

For a fixed task law and this mixture of deterministic threshold policies,
J_sigma cannot be below the original global minimum. Smoothing is neither
a free performance improvement nor proof of a new optimal deterministic h.

### 3.1 Exact local bias bound

At a nonjump point, the contribution of jump Delta_j to smoothing bias has
magnitude `|Delta_j|*Phi(-|h-b_j|/sigma)`. The triangle inequality gives

```
|J_sigma(h)-J(h)|
 <= sum_j |Delta_j|*Phi(-|h-b_j|/sigma).
```

At a jump, the right-closed endpoint convention produces the same half-mass
bound for that jump. As sigma tends to zero, its smoothing error tends to half
the jump magnitude. No sequence of continuous functions uniformly converges
to a genuinely discontinuous function on a domain containing the jump.
This does not invalidate continuum analysis: it says large physical/structural
jumps must be retained, rather than mislabeled microscopic lattice noise.

### 3.2 Resolution must be separated from macroscopic variation

Let delta be the token quantum in scaled units, sigma a declared uncertainty
or coarse-graining scale, and L a scale over which the envelope changes.
The useful regime is delta << sigma << L, when such a separation exists.
For a midpoint lattice approximation to Uniform[0,1], convolution-gradient
error can conservatively be bounded using the coupling above and
`Lip(phi_sigma)=1/(sigma^2*sqrt(2*pi*e))`:

```
gradient_error <= delta/(4*sigma^2*sqrt(2*pi*e)).
```

Hence delta/sigma^2 -> 0 is one sufficient joint scaling, followed by removing
boundary effects. This is conservative, not a necessary optimal bandwidth rule.
Taking sigma much smaller than delta instead creates narrow derivative peaks
between near-zero regions. No useful continuum derivative is recovered by
that order of limits. The executed lattice/control examples are recorded in
[continuum-symbolic-results.md](continuum-symbolic-results.md).

### 3.3 A sharper general gradient bridge from a cost envelope

If a full-system cost envelope J_c has L_1-Lipschitz derivative and the valid
extensions satisfy `||J_delta-J_c||_infinity<=epsilon_delta`, then Gaussian
regularization has the GENERAL derivative bound

```
||J_(delta,sigma)' - J_c'||_infinity
 <= sqrt(2/pi)*(epsilon_delta/sigma + L_1*sigma).
```

Proof: split the difference into the derivative of
`(J_delta-J_c)*phi_sigma` and `(J_c'*phi_sigma)-J_c'`. Bound the first by
epsilon_delta times `||phi_sigma'||_1=sqrt(2/pi)/sigma`. Bound the second by
`L_1*E|sigma*Z|=L_1*sigma*sqrt(2/pi)`. Appropriate boundedness/tail conditions
justify the convolution and derivative exchange. A compact candidate interval
requires a valid extension or an explicit boundary/tail remainder.

Thus BOTH smoothing noise and surrogate bias matter. When L_1>0, balancing
the two terms gives `sigma=sqrt(epsilon_delta/L_1)` and a sufficient gradient
error bound `2*sqrt(2/pi)*sqrt(epsilon_delta*L_1)`. These are mathematical error
parameters, not an estimated optimal threshold or a fitted workload law.

This establishes exactly how a zero microscopic derivative can produce a
stable, nonzero macroscopic derivative. It applies to the complete expected
cost, with all correlations and endogenous resets already incorporated, IF
its uniform envelope approximation is first established. Large surviving jumps
prevent that smooth-envelope premise on domains crossing them.

For the scalar midpoint-law example there is also a sharper alternative:
Kolmogorov CDF error epsilon and integration by parts give density error at
most `2*epsilon/(sigma*sqrt(2*pi))`, because the Gaussian density's total
variation is `2/(sigma*sqrt(2*pi))`. With epsilon=delta/2 this is
`delta/(sigma*sqrt(2*pi))`; therefore sigma=sqrt(delta) works in that example.
This stronger CDF-based statement is not a replacement for a whole-controlled-
system cost bound.

## 4. Whole controlled systems: couple before the first differing decision

Scalar distribution approximation alone is not enough because a threshold
can alter every later recovery and crossing. The following finite-horizon
coupling bound addresses that amplification without iid assumptions.

Assume exact and approximate systems share primitive randomness and at most M
decision epochs. Before their first different action, compared threshold scores
differ by at most epsilon_delta. Other logical/contract mechanisms agree, or
their comparison guards are included in the bound. On paths with identical
decisions, total cost differs by at most e_delta. Costs lie in [0,C_max].

A first different threshold decision can occur only when the reference score
lies within epsilon_delta of h. Therefore, with the reference predecision
law nu_t^h and a union bound,

```
|J_delta(h)-J_cont(h)|
 <= e_delta + C_max * min(1,
      sum_(t=0)^(M-1) nu_t^h{|X-h|<=epsilon_delta}).
```

Proof: split the coupling into agreement and first-divergence events. On
agreement use e_delta. On divergence use the invoice range C_max. Before the
first divergence, opposite comparisons imply membership of the boundary band;
the union bound completes the argument. All subsequent behavior may differ
arbitrarily and is already covered by C_max.

If each score law has density bounded by L_t near h, its boundary probability
is at most 2 L_t epsilon_delta. If it has reset/file atoms, add their probability
in the band. For cache eligibility, TTL and any other approximated numerical
guard, include their own boundary bands; controlling X alone does not prove
those mechanisms agree. There is no iid or independent first-use assumption.

This bound is conditional on an actual stable coupling and ledger approximation.
It does NOT establish those premises for the calibrated simulator. Large file
payloads, cache-prefix identity changes and state-dependent outputs need a
justified approximation map. For unbounded bills replace C_max with tail/UI
control, not an invented finite cap. The union bound can be loose for long tasks.

## 5. Approximation must transfer to optimization, not merely to a plot

On the SAME feasible candidate domain H, suppose

```
sup_(h in H) |J_cont(h)-J_delta(h)| <= epsilon.
```

If h_c minimizes J_cont, then

```
J_delta(h_c) - inf_H J_delta <= 2*epsilon.
```

Proof: for any candidate y,
`J_delta(h_c)<=J_cont(h_c)+epsilon<=J_cont(y)+epsilon<=J_delta(y)+2epsilon`;
take the infimum. An approximate solver with tolerance tau adds tau.
If a domain restriction/rounding projection changes the feasible set, its
additional loss needs a separate bound. Price, quality and completion
constraints must agree before comparing policies.

The general common-rational-unit inequality is now kernel-checked as
`approximation_optimization_transfer` in Lean; there are 22 checked declarations.
Lean does not assert that epsilon has been established for a specific continuous
compaction model. That is the next model-validation obligation, not something
hidden inside the theorem's hypotheses.
The real-valued bound is proved by the analytic inequality chain above; Lean
currently verifies its common-rational-unit algebra, not a representation of
Gaussian expectations as natural numbers. Rational outward bounds can certify
real-valued comparisons only when their additional enclosure error is included.

Cost-regret convergence does not automatically locate the minimizer. If a
separate quadratic-growth condition holds,
`J_cont(h)>=J_cont(h*)+kappa*(h-h*)^2/2`, then surrogate error also controls
argmin displacement. A broad flat sweet region can have stable cost but poorly
identified exact location. This explains why exact-token optimum claims are
less useful than a cost-tolerant region when modeling uncertainty dominates.

## 6. Continuous control with essential jumps retained

The useful continuous candidate is a hybrid process: a real-valued scaled
context coordinate and cache ages, coupled to discrete file/version/guard
configurations. Large restoration and compact resets remain finite jumps.
With a justified sufficient-state law, between-request drift b, jump rate
lambda and mark law Q, its generator on smooth test functions is

```
L f(s)=b(s) dot grad f(s)
      +lambda(s)*integral [f(Psi(s,y))-f(s)] Q(dy|s).
```

Cache ages can have deterministic drift; x need not drift between completed
requests. On an augmented state including completed ordinary count n, ordinary
jumps advance n, while compactor/recovery interventions do not. A paid reset
operator is `M V(s)=c_comp(s)+integral V(s') R(ds'|s)`. Bellman continuation
and intervention remain coupled, with zero terminal bill when n=N.
The permitted decision epochs must also survive the approximation: a harness
allowing compaction only before requests does not grant a continuous controller
permission to intervene between them. Changing action timing changes the
feasible policy class and invalidates an unlabeled optimum comparison.

A diffusion term requires an additional small-jump/high-rate limit with
moment and dependence conditions. A 20k-file reload is not made infinitesimal
by calling the context coordinate continuous. Likewise deterministic reset
sizes can create atoms even in a continuous-state model.

Some large atoms in the previous control are modeling choices: summary and
file sizes were set EXACTLY constant and accesses used a small finite corpus.
The user's practical premise is concentration NEAR constants, which can have
nonzero spread. These artificial atoms are not evidence that the real engineering
objective cannot have a useful smooth macroscopic approximation. Such spread
belongs in the JOINT reset/transition law, preserving its correlations and
contracts, rather than assigning independent Gaussian noise to every variable.

## Sources and transfer limits

- Probability weak convergence and continuity-set conditions:
  [Aldous/Chewi, Berkeley graduate notes](https://www.stat.berkeley.edu/users/aldous/205B/chewi_notes.pdf),
  Lecture 7. Continuous mapping needs zero probability on discontinuity sets;
  weak law approximation alone does not preserve threshold events at atoms.
- Discrete-to-continuous jump-process limits:
  [Kurtz, Journal of Applied Probability 1970](https://doi.org/10.1017/S0021900200026929).
  This establishes a classical route under its scaling assumptions; those
  hypotheses are NOT verified for our context process merely by citation.
- Randomized smoothing:
  [Duchi, Bartlett and Wainwright, SIAM J. Optimization 2012](https://doi.org/10.1137/110831659),
  [author-hosted full paper](https://web.stanford.edu/~jduchi/projects/DuchiBaWa12.pdf).
  Their convex nonsmooth optimization rates are not imported into the generally
  nonconvex/discontinuous threshold curve. Our finite-jump convolution and bias
  expressions are directly derived.
- Production reset/caching semantics remain grounded in the official sources
  documented in [mathematical-tools-for-compaction.md](mathematical-tools-for-compaction.md).
  The continuum representation preserves those contracts; it does not turn
  semantic availability into a continuous token-size variable.

The theoretical contribution of this extension is the bridge and its failure
criteria: scale separation, boundary mass, whole-system coupling, and transferred
decision regret. Exact discreteness is a reference layer, not the end of research.
