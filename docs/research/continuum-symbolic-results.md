# Executed continuous-control and coarse-graining bridge

Recorded 2026-10-06. This corrects an overly restrictive interpretation of the
earlier discrete control: **finite realized systems do not preclude continuous
probability laws, continuous controller sensitivities, or useful continuum
approximations**. A microscopic integer reference is a starting point for
error-controlled approximation, not a reason to stop the analysis.

General bridge proofs are in [continuum-bridge-theory.md](continuum-bridge-theory.md).
This note owns the executable symbolic Gaussian calculus, actual-engine curve
regularization, and the controlled uniform-lattice quadrature results.

Maintained implementation:

* `src/context_compaction_lab/continuum_symbolics.py`
* `experiments/continuum_threshold_analysis.py`
* `tests/test_continuum_symbolics.py`

No simulator, dependency, configuration, version, or previous experiment output
was changed. The source occupations are the exact actual-engine polynomials
from [structural-symbolic-analysis.md](structural-symbolic-analysis.md), not
another independent ledger or newly invented workload simulation.

## 1. Two legitimate continuum constructions, with different meanings

| Construction | Mathematical object | What is exact? | What needs additional justification? |
| --- | --- | --- | --- |
| One uncertain task budget | H=max(1,h+sigma Z), one independent Z for the whole task | The continuously differentiable response of this randomized/uncertain-budget controller, using the original endogenous dynamics | Interpreting sigma as real budget uncertainty; transferring its preferred mean to a deterministic controller |
| A macroscopic continuum family | Finite lattice quantum delta shrinks relative to a fixed macroscopic scale | Finite error bounds and derivative limits under the specified family | Establishing a continuum envelope and approximation error for the actual whole controlled system |

The first is a genuine continuous objective, not an assertion that the
original deterministic system has become continuous. The second can explain
why a macroscopic derivative is useful even when each microscopic law is
finite. Neither requires infinitely many physical states to be realized.

The exact eight-action fixture has conspicuous atoms because file, summary,
and ordinary append sizes were fixed by construction. Those atoms are not
evidence that a real heterogeneous workload's expected threshold response is
necessarily nonsmooth. Real size variability and continuous joint laws must
be modeled through their own kernels, rather than inferred from this fixture.

## 2. Exact whole-task Gaussian controller

Let J(h) be the complete original task expected bill, including every changed
stopping time, cache state, mandatory recovery, compactor invoice, and output
carry. Extend it constantly below its lowest admissible budget 1. Draw

\[
H=\max(1,h+\sigma Z),\quad Z\sim N(0,1),\quad \sigma>0,
\]

**once per whole task**, independently of its demand path, and keep H fixed
for that task. This is not per-request jitter. Resampling at each ordinary
action would change the joint transition law and is not represented below.

For the original exact step law, write

\[
J(H)=J_0+\sum_b\Delta_b\mathbf1\{H>b\}.
\]

Every existing boundary b is at least 1, so clipping gives
`P(H>b)=P(h+sigma Z>b)`, including b=1 under the strict exceedance convention.
Thus

\[
\boxed{J_\sigma(h)=J_0+\sum_b\Delta_b\Phi((h-b)/\sigma).}
\]

With `phi_sigma(x)=exp(-x^2/(2 sigma^2))/(sigma sqrt(2 pi))`,

\[
\boxed{J_\sigma'(h)=\sum_b\Delta_b\phi_\sigma(h-b),}
\]
\[
\boxed{J_\sigma''(h)=-\sum_b\Delta_b\frac{h-b}{\sigma^2}
                                      \phi_\sigma(h-b).}
\]

These are actual smooth derivatives of the declared whole-task controller,
not zero derivatives of a microscopic staircase. SymPy differentiates the
erf representation of the full actual-engine cost expression and verifies
both kernel identities exactly, with demand alpha and all four prices still
symbolic. The kernel interpretation connects the earlier signed derivative
measure to continuous sensitivity rather than discarding that measure.

The randomized expected bill is a convex combination of original cell bills.
Therefore it cannot be below the original global minimum. A smoothing-selected
mean is not proof of a better deterministic policy or a production sweet spot.

## 3. Local bias and unavoidable macroscopic jumps

At a nonjump mean h, each jump's contribution to bias has magnitude

\[
|\Delta_b|\Phi(-|h-b|/\sigma).
\]

The triangle inequality yields

\[
\boxed{|J_\sigma(h)-J(h)|\le
B_\sigma(h):=\sum_b|\Delta_b|\Phi(-|h-b|/\sigma).}
\]

This is a local, computable bound; signed jumps may cancel, so the sum is not
always attained. If `V=sum_b abs(Delta_b)` is total jump variation, the generic
global bound is V/2. Far from every jump, Gaussian tails make the local bound
much smaller.

At a jump h=b, right-closed J(b) is the left value, while its own smoothing
term contributes Delta_b/2. As sigma tends to zero, the cost approaches the
mean of the two adjacent values, not the selected left endpoint. The error
there remains `abs(Delta_b)/2`. Thus fixed nonvanishing jumps forbid uniform
convergence of this smooth response to the original discontinuous law on a
domain containing them. A successful continuum family must control jump
amplitudes or declare a resolution that retains macroscopic jumps.

The implementation evaluates the bound both normally and in log space.
Numerical underflow to zero is not reported as a mathematical zero. Its
signed derivative and curvature logs likewise preserve evidence of tiny
nonzero sensitivities.

## 4. Actual-engine continuous response at four scales

The exact source is `.cache/structural-symbolic-analysis/results.json`:
22 first-use occupation cells with symbolic demand alpha and integer token
ledgers. The experiment uses alpha=7/20 and exact rational prices before any
numeric conversion. It examines the previous default prices and a declared
read-price sensitivity ($3/M rather than $0.30/M). All other mechanisms remain
unchanged. Sigma is 0.25, 1, 4, or 12 **in this fixture's token units**, not a
calibrated production uncertainty.

Numerical evaluation uses SciPy normal CDF/density functions. Independent cell
integration computes Gaussian probability mass for each original band and
pairs it with that band's cost. It agrees with the jump-CDF formula throughout
the h=1..320 grid to within 2e-17 USD. No Monte Carlo estimate is needed to
validate this finite integral. All grid biases satisfy the local bound, and
every smoothed bill remains above the original global minimum up to the
declared floating evaluation tolerance.

### Read-price sensitivity: the stable valley becomes a smooth response

The deterministic first-use minimum is $0.004964155380143262 on the entire
real cell (156,178]. The best detected local smooth valley is:

| Sigma | Mean h at detected valley | Smoothed bill USD | Bias above deterministic cell bill USD | log10 absolute curvature |
| ---: | ---: | ---: | ---: | ---: |
| 0.25 | 167.000815 | 0.004964155380 | Below floating resolution | -421.45 |
| 1 | 167.013037 | 0.004964155380 | Below floating resolution | -29.13 |
| 4 | 167.201916 | 0.004965108998 | 9.53618e-7 | -6.30 |
| 12 | 166.453451 | 0.005022490446 | 5.83351e-5 | -6.30 |

At sigma=0.25 the local bias bound is approximately 10^(-425.94) USD, rather
than exactly zero. At sigma=1 it is 6.0883e-32 USD. A mathematically isolated
stationary point with curvature near 10^(-421) does not provide a practically
identifiable unique budget. Selecting one mean from that almost-flat region
would confuse numerical precision with controller robustness.

To show this explicitly, the grid means within 1e-8 USD of its sampled minimum
span approximately 157.00..177.05 at sigma=0.25, 159.90..174.20 at sigma=1,
167.05..167.40 at sigma=4, and 166.30..166.65 at sigma=12. These are numerical
indistinguishability regions on a declared grid, not exact minimizing sets.

The centered valley does not move monotonically with sigma. Wider kernels
combine more distant jumps and can change the balance of the entire cost
curve. The sigma=12 center is therefore not obtained by simply averaging the
deterministic cell endpoints.

Stationary points are located through derivative-sign changes on a 0.05-token
grid followed by Brent root refinement. Log-normalized signed kernels prevent
underflow from creating spurious zero-gradient regions. This is a numerical
feature investigation, not a proof that every root has been isolated. Two
minimum and two maximum sign changes were detected for the stress case at
each of the four scales in the searched range.

### Default prices: local valley is not the global answer

Under default prices, the original global minimum is the no-compaction tail
with bill $0.002553517621514472 for h>268. For any finite sigma and finite h,
the Gaussian budget can enter worse cells, so its infimum is approached in
the h-to-infinity tail; the finite local valley is not globally optimal.

The detected local valley shifts from h=167.0093 at sigma=0.25 to h=183.5670
at sigma=12. Its sigma=12 bill $0.002801703928 remains above the global tail
bill despite being below the deterministic bill at that particular mean.
This distinguishes a local smoothing improvement at one mean from a global
policy improvement, which convex averaging cannot deliver.

Figure: `.cache/continuum-threshold-analysis/comparison.png`. It displays both
actual-engine price regimes, the four continuous controller curves, and their
true kernel gradients. All points still contain the original endogenous
restoration and stopping-state effects through the exact source occupations.

## 5. A genuine continuum family: uniform moving-boundary quadrature

This is a **separate analytic approximation example**, not a new surrogate
claimed to fit the working-set simulator. Let U be uniform on [0,1] and let
one-event cost be `1{U>=h}`. For 0<h<1,

\[
J_c(h)=1-h,\qquad J_c'(h)=-1.
\]

Approximate U by m equiprobable midpoints `u_k=(k+1/2)delta`, delta=1/m. Every
approximating law is finite. Its cost is the staircase

\[
J_\delta(h)=\delta\sum_{k=0}^{m-1}\mathbf1\{h\le u_k\}.
\]

Its uniform cost error is at most delta/2; its classical derivative is zero
off the midpoints, yet its signed derivative measure has weights -delta at
those points and converges to the uniform-law derivative measure.

Draw one task-level threshold `clip(h+sigma Z,0,1)`. Because all midpoints lie
strictly inside [0,1], clipping leaves their exceedance probabilities unchanged:

\[
J_{\delta,\sigma}(h)=\delta\sum_k\Phi((u_k-h)/\sigma),
\]
\[
J_{\delta,\sigma}'(h)=-\delta\sum_k\phi_\sigma(h-u_k).
\]

The corresponding continuous-law expectation is

\[
J_{c,\sigma}(h)=\int_0^1\Phi((u-h)/\sigma)\,du,
\]

with exact antiderivative `sigma[Psi((1-h)/sigma)-Psi(-h/sigma)]`, where
`Psi(v)=v Phi(v)+phi(v)`. SymPy checks its derivative:

\[
\boxed{J_{c,\sigma}'(h)=
-\{\Phi(h/\sigma)-\Phi((h-1)/\sigma)\}.}
\]

It tends to -1 at interior h as sigma tends to zero. Thus a microscopic finite
law can recover a useful continuum gradient when approximation, bandwidth,
and boundary effects are controlled together.

### Executed two-scale comparison

Probe h=1/2, a cell gap, and h=1/2+delta/2, a neighboring midpoint. Compare
sigma=sqrt(delta) with sigma=delta/8:

| m | Raw uniform cost error bound | Coarse gradient at h=1/2 | Lattice-resolving gradient at cell gap | Lattice-resolving gradient at midpoint |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 0.03125 | -0.95506110 | -0.00214128 | -3.19153824 |
| 64 | 0.0078125 | -0.99993735 | -0.00214128 | -3.19153824 |
| 256 | 0.001953125 | -1.00000000 | -0.00214128 | -3.19153824 |
| 1024 | 0.00048828125 | -1.00000000 | -0.00214128 | -3.19153824 |

Costs converge in both regimes. In the fine-bandwidth regime the density
peaks and intervening near-zero slopes remain, regardless of m. **Cost
convergence alone does not imply derivative convergence.** Taking bandwidth
small enough to resolve every lattice jump answers a different question from
macroscopic sensitivity. This is not a defect of continuous mathematics; it
is an order-of-limits and scale-separation issue.

For this scalar midpoint law, the CDF error is delta/2. Integration by parts
against the Gaussian density yields the sharper gradient approximation bound

\[
|J_{\delta,\sigma}'-J_{c,\sigma}'|
\le \frac\delta2\operatorname{TV}(\phi_\sigma)
=\frac{\delta}{\sigma\sqrt{2\pi}}.
\]

This justifies sigma=sqrt(delta) for this example, followed by removal of
interior boundary tails. It is **not** a universal sufficient condition for
every endogenous controlled system. A whole-system cost approximation or a
strong enough coupled state-law bound must first be established. The more
general proofs and conservative coupling alternatives live in the root bridge
note. Figure: `.cache/continuum-threshold-analysis/lattice-gradient.png`.

## 6. Whole-objective approximation gives a real gradient theorem

The root bridge note additionally establishes a useful route that does not
depend on the uniform-law example. If an actual finite-system objective
J_delta and a continuum envelope J_c satisfy a valid uniform error
`||J_delta-J_c||_infinity <= epsilon_delta`, and J_c' is L1-Lipschitz under
the chosen extension, Gaussian convolution gives

\[
\|J_{\delta,\sigma}'-J_c'\|_\infty
\le\sqrt{\frac2\pi}
\left(\frac{\epsilon_\delta}{\sigma}+L_1\sigma\right).
\]

For positive epsilon_delta,L1 the bound is minimized at
`sigma=sqrt(epsilon_delta/L1)`, with value
`2 sqrt(2/pi) sqrt(epsilon_delta L1)`. The new tests independently verify the
Gaussian constants `||phi_sigma'||_1=sqrt(2/pi)/sigma` and
`E|sigma Z|=sigma sqrt(2/pi)`, and this exact bandwidth minimization in SymPy.

This is the substantive answer to the finite-versus-continuous tension:
establish the whole controlled cost approximation, choose a resolution with a
quantified gradient error, and only then use continuous sensitivity. Smoothing
an arbitrary large-jump fixture without that approximation does not supply
the missing premise.

## 7. Reproduction and verification artifacts

From the repository root, generate the exact source if its cache is absent:

```powershell
uv run python experiments/structural_symbolic_analysis.py
uv run python experiments/continuum_threshold_analysis.py
uv run pytest tests/test_continuum_symbolics.py -q
uv run ruff check src/context_compaction_lab/continuum_symbolics.py experiments/continuum_threshold_analysis.py tests/test_continuum_symbolics.py
```

Outputs stay under `.cache/continuum-threshold-analysis/`: `results.json`,
`comparison.png`, and `lattice-gradient.png`. The JSON includes exact erf
expressions, exact original jump coefficients, all four-scale actual-curve
features, local bias bounds/logs, independent band-integral discrepancies,
and the continuum quadrature table. Numeric evaluation is explicitly separate
from symbolic derivation.

The recorded final full run took approximately 6.30 seconds. Twelve maintained
tests passed in 2.46 seconds, and Ruff passed. The plots were visually
inspected; axes, scales, labels, legends, and distinct controller semantics are
visible. Maintained tests regenerate an actual-engine curve without depending
on the cache, check clipping atoms, exact kernel derivatives, tail probability
stability, bias bounds, underflow logs, continuum derivatives, persistent
lattice-gradient oscillations, and the whole-envelope bound's constants.

These results deliver an executable bridge rather than a categorical defense
of discreteness: continuous control can be exact under a declared random law,
and a finite lattice can approximate a continuous moving boundary with useful
derivatives. The unresolved production task is to obtain an appropriate joint
state law or whole-objective approximation from actual variable workloads,
not to argue that a finite universe forbids such models.
