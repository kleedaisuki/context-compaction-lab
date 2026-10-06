# Independent review of price sensitivity mathematics and interventions

Recorded 2026-10-06. Scope: `price_sensitivity.py`,
`price-sensitivity-theory.md`, and the forthcoming executable price study.
The reviewer does not modify production files. The objective remains expected
four-price invoice for a fixed ordinary-action law, not cross-model task quality.

## Early finding: an atom has directional branches, not a single Jacobian

`core_sensitivity` differentiates the canonical representative
`L=D^{-1}(A/c)`, not the full marked-law or integer/grid-selected optimum.
Away from a renewal atom, its price/material/cache/growth calculations pass
the independent checks below. Originally, at an atom it always used the
**right-hand D slope** for every parameter direction. That is not a classical
gradient, and it is not the positive-parameter directional derivative when
that direction decreases `A/c`.

Exact counterexample: deterministic `G=1`, `q=0`, `S=10`,
`B=C=K=0`, and `(p_i,p_w,p_r,p_o)=(1,1,0,0)`. Then `A/c=10` and the
canonical gap is exactly **4**. `D'_-(4)=4`, `D'_+(4)=5`.

- Returned write-price gradient: **-2**. Increasing write price decreases
  `A/c`, so the true right directional derivative in that parameter is
  **-2.5**. A `+1e-6` numerical perturbation gives **-2.49999750**.
- Returned growth-scale gap elasticity: **0.5**. Increasing the growth scale
  decreases the inverse argument and requires the left D slope, giving
  **0.375**. A `+1e-6` perturbation gives **0.37499999994**.

Required correction identified at initial review: either explicitly reject/report nonsmooth atom roots
for an ordinary-gradient API, or return both inverse branches/directional
metadata and select the slope according to the sign of the induced inverse
argument. A right-branch vector may be useful, but must not masquerade as
all ordinary coordinate derivatives. No present empirical-result failure is
inferred: its canonical root will generally be inside a lattice interval.
The theory note already limits classical derivatives to continuity points;
the executable API should enforce or faithfully expose that distinction.

## Independent checks completed

### Full expected category basis

Compared `expected_category_rates` with the independent **category-level**
residual-state DP in `experiments/renewal_ledger_crosscheck.py`, rather than
only repricing the same expanded analytic formula. The finite constructed law
is `G={0,1,3,8}` with probabilities `{.2,.2,.3,.3}`; 5 gaps, 3 cache-hit
probabilities and 3 pre/post timing fractions give 45 comparisons.

Maximum absolute differences in `(I,W,R,O)` tokens/action were
`(8.53e-14, 2.84e-14, 4.26e-14, 8.88e-16)`. The basis is nonnegative and
price-independent on these cases. Its negative separated write-tail term
removes an unperformed final cache write; it does not imply negative actual
usage. Source-level expansion agrees with the independent ledger timing.

For a fixed workload/cache/reset mechanism, prices do not alter token
categories. Repricing their four-coordinate totals with a dot product is
therefore exact; regenerating trajectories for every price would only add
avoidable comparison noise. A changed q, growth law, S/B/C path or timing
fraction is a **new mechanism**, not merely a price-vector substitution.

### Smooth/interpolated-core numerical gradients

At `S=100,B=20,C=10,K=128,q=.63`, the same finite law yields the canonical
gap **57.8792116261**, strictly between lattice atoms. Directly expanded
`A=p_i[K+(1-q)S]+qp_w(S-B)+qp_rB+p_oC` and `c=(1-q)p_w+qp_r` were inverted
numerically; the checker does not call the target sensitivity formulas.

| Intervention | Finite-contrast result | Returned analytic result |
| --- | ---: | ---: |
| q, fixed prices/material/law | 67.32528258 | 67.32528255 |
| B reclassification, fixed S | -0.0795543173 | -0.0795543183 |
| Add stable material, increase both B and S | 1.0475459220 | 1.0475459211 |
| Increase C preserving other material, increase S equally | 1.6761293523 | 1.6761293515 |
| Scale whole G law, gap elasticity | 0.4702005590 | 0.4702005590 |

All four price-coordinate gradients also matched finite differences (relative
discrepancy below `3e-10`), and full-threshold price elasticities summed to
`6.25e-17`, as required by degree-zero radial policy homogeneity. Scaling G
was evaluated using `D_a(L)=a D(L/a)`, not by rounding infinitesimally changed
increments back into the same empirical bins.

## Mathematical interpretation requirements

1. Canonical D-inverse gradients, full marked rates, and discrete controller
   flips are three distinct objects. The core root can move inside a plateau
   without changing the optimal token controller or invoice.
2. For a fixed finite candidate set and price-independent expected usage,
   `V(p)=min_h p dot m(h)` is concave, nondecreasing in each nonnegative price,
   and homogeneous of degree one. Its active usage is a supergradient; it is
   an ordinary gradient only where the optimized value is differentiable.
   Concavity concerns the **optimized value**, not a universal direction of
   optimal threshold changes. Threshold flips do not violate that geometry.
3. Keep the candidate set the same across price vectors when testing those
   finite-envelope properties. A different sampled/generated candidate set
   for each tariff could manufacture an apparent violation or advantage.
4. At a fixed threshold, each price-only invoice is exactly linear. Uniform
   scaling changes all invoices by the same factor and preserves minimizers;
   it does not establish equal behavior, tokenization or performance across
   differently priced models.
5. q-by-write contrasts and thin-volatile-prefix write/read reversals must
   evaluate the **marked** optimum separately. The analytic core sign surface
   need not survive a terminal correction, finite horizon, or serial dependence.
6. Explicit material paths are essential: B inside fixed S differs from added
   stable B; C at fixed S removes other material, while preserving required
   non-summary material increases S. Scaling G by two changes the whole law
   and its support/moments, not just a displayed mean parameter.

## Bounded reproduction

The disposable numerical checker is `.temp/price_review_probe.py`, runnable
with `uv run python .temp/price_review_probe.py`. It loads no trace and calls
no API. The maintained independent category DP is reproduced with
`uv run python experiments/renewal_ledger_crosscheck.py`. The atom example
above specifies its entire law, ledger, perturbations and expected slopes,
so it remains reproducible without the disposable checker.

The maintained bounded experiment is
`experiments/price_sensitivity_crosscheck.py`; execute
`uv run python experiments/price_sensitivity_crosscheck.py`. Its compact
artifact is `.cache/price-sensitivity-crosscheck/results.json`. It requires
no community pool or network. Ruff checks and formatting passed. No pytest
suite or generic-prior/Sobol study was added.

## Corrected atom API and value Hessian

The integrator now rejects canonical roots at/within numerical tolerance of
a positive renewal atom. The nearest-grid comparison checks both sides, and
an endpoint guard requests a larger bracket before inspecting the next slope.
The maintained experiment confirms the deterministic gap-4 atom is rejected,
while separately reproducing its true positive-price and positive-growth
directional values. The counterexample is retained above for future API design.

The theory's optimized-value Hessian
`-u/(c U^3) * alpha alpha^T`, with `alpha=a-(A/c)v`, is correct for one
smooth, locally stable active threshold branch and a price-linear fixed-law
ledger. Independently evaluating the directly minimized exponential-core
value and taking finite price second differences gives relative matrix error
**3.32e-7**. The predicted singular values are approximately
`(5.55e6, 2.23e-10, 7.21e-12, 4.58e-28)`, confirming rank one numerically.
Radial repricing error is exactly zero in the constructed check; a finite
common-policy concavity example has positive gap **9.29e-7 USD/action**.

These results do not give a global Hessian across policy ties, atoms,
constrained optima or transitions between separated marked minima. Concavity
survives those transitions, but ordinary derivatives may not. For a full marked
smooth active branch the general identity `-j_pL j_Lp / j_LL` is the correct
replacement; the unmarked core coefficient cannot simply be reused.

## Executable study: controls and confirmation

Reviewed `experiments/run_price_sensitivity.py` after its initial implementation:

- Full marked-rate predictions are checked against four-category dot products.
  The price envelope uses the same candidate grid for every price vector.
  The binned empirical lane distinguishes core and marked thresholds and now
  records an unbounded-right-tail cost certificate, not merely an interior
  finite-grid minimizer. The certificate is valid for the finite support:
  the core is nondecreasing beyond its bracket and a negative terminal term
  is bounded below by `d*theta*maximum_growth/U_end`.
- Confirmation groups mechanisms by S/C/B/q/theta/growth scale. Within each
  group, ONE token ledger is simulated and every price vector reprices the
  same category array. Shared ordinary-action fields also pair mechanism
  contrasts. Only prices vary inside a price-only group.
- Growth scale two multiplies the entire sampled increment law; ordinary
  billed output is intentionally held fixed. Stable reclassification keeps
  S fixed; adding stable material increases B and S together; summary growth
  preserves non-summary material by increasing S. The stable-heavy sign
  regime is a separate constructed mechanism, not a silently inferred
  decomposition of the aggregate prompt median.
- Confirmation trajectories use seeds separate from prior discovery. Their
  paired intervals condition on the public empirical pool and declared
  mechanisms. They do not include corpus/source-selection uncertainty.
  A long-run analytic retuning is not asserted to optimize finite-N/block
  invoices; a negative empirical saving is possible and must remain visible.
- The finite confirmation field `price_gradient_at_retuned` contains full-
  horizon expected categories, matching its stated unit. It is the gradient
  of that **fixed retuned policy's** invoice, not automatically the envelope
  gradient of a finite-horizon optimum. The analytic optimized category vector
  has the separate long-run/unit-per-action meaning.
- Official quoted price vectors are applied to the SAME controlled token
  counts. Cache TTL metadata does not silently change q. A comparison of
  these projections does not claim real provider performance or tokenizer
  equality. Break-even q is a required hypothetical cache gain, not a measured
  gain from selecting a 1-hour TTL.

The integrator tightened sign-regime reference policies:
pure price-retuning savings within a q/B/theta family must be compared against
the old-price optimum of that **same mechanism**, not the global default
113k policy. Otherwise changing q/B can dominate the apparent price effect.
The global default threshold remains a meaningful explicit unchanged-policy
control for material/timing/growth interventions.

## Final corrected-study status

Inspected the corrected source and the completed **35-case**, independent
512-trajectory by 4,000-action IID/block results; this is an artifact/source
audit, not a duplicate full study run. All four sign-regime families now use
their own unchanged-price, same-mechanism marked optimum as `old_threshold`.
The family references are respectively **91,003; 79,368; 80,248; 76,703**
tokens. Every factor-1 baseline has exactly zero analytic regret and exactly
zero paired confirmation difference/halfwidth under both IID and block laws.
This closes the reference-policy confounding issue.

The Sonnet 4.6/5.5 quote projections have identical category vectors and
identical chosen/unchanged thresholds. Both IID/block confirmation mean rates
scale exactly by **2/3**; retuning contrasts are exactly zero. Because the
categories are shared at the sample level, all per-trajectory costs scale by
2/3 and variances by **4/9** algebraically. Zero retuning contrasts do not
separately provide evidence about nonzero Monte Carlo variance; the common
immutable ledger is what guarantees the identity.

The added tariff comparison now pairs TOTAL expenses of short-tariff q=.8
with long-tariff q=.8/.95, using common growth/output/uniform cache fields.
It does not merely compare each tariff's retuning benefit:

| Conditional block contrast | Long minus short USD/action | Paired 95% MC halfwidth |
| --- | ---: | ---: |
| Same q=.8, higher-write long tariff | +0.0278259834 | 0.0000634353 |
| Hypothetical long-tariff q=.95 versus short q=.8 | -0.0169031452 | 0.0001051715 |

IID contrasts have the same respective signs. The optimized analytic
break-even is **q=0.895035158** from short-tariff q=.8; the fixed-short-threshold
break-even is **0.896281229**. These are different controlled decisions, and
the result labels preserve that distinction. At short q=.98, the short
optimized rate **0.0391280213** is below even the long-tariff q=1 minimum
**0.0391699376**, so no feasible cache-hit gain pays for that tariff in this
specified lane. None of these numbers estimates actual TTL survival.

Final recommendation: **the corrected mathematics/API and declared repricing
study pass this bounded independent review.** No further required production
fix was found. Retain conditional-pool uncertainty, finite-horizon policy,
atomic-direction and price-quote-versus-performance qualifications. The
maintained crosscheck and this review are the independent verification
artifacts; the integration track owns the full simulation outputs.
