# Analytic renewal / four-price community study contract

Started and executed 2026-10-06. This is the integrated milestone contract, not a
claim that a general history model regenerates. Prior theory is reused rather
than discarded. Dominant restriction: every new cycle reconstructs the same
aggregate context S; stable warm base B is INSIDE S, not added to it.

Delivery status: analytical proofs and closed forms, pinned community calibration,
deterministic empirical renewal evaluation, raw IID/random-phase block comparisons,
finite-horizon independent confirmation, symbolic/Lean checks and an independent
four-category dynamic-programming comparison are executed. The integrated findings
are in [renewal-community-study.md](renewal-community-study.md), with portable
[numerical evidence](renewal-results.json) and [independent review](renewal-study-review.md).

## Mathematical layers

- Canonical regenerative law: iid nonnegative aggregate ordinary growth G,
  g=EG>0, positive context gap L=H-S. U(L)=ET_L, M(L)=expected pre-call growth
  area, D(L)=LU-M=integral_0^L U(x)dx. The four-price-free accounting theorem
  gives rate baseline+(A+cM)/U and the unique sign crossing cD=A.
- A density is unnecessary for the Stieltjes sign theorem. At a renewal atom
  x of mass w, the cost jump sign is c(xU-M)-A. Zero growth is retained.
- Closed-form and moment corrections belong in renewal-analytic-control.md
  and renewal-closed-forms.md, implemented by renewal_analytic.py.
- The macro ledger must retain the latest uncached post-call tail Z. For
  proportional marked sensitivity Z=theta G, its crossing expectation is
  zeta(L)=theta E G_T. Ignoring it is a quantified approximation, not a hidden
  assertion that generated output was cached when produced.

## Explicit physical ledger

Illustrative fixed USD/token rates pi,pw,pr,po. Each ordinary gap independently
has a matching-prefix hit with probability q, independent of G. No policy-extra
delay. Cache-eligible S is reconstructed with summary C and the remaining
declared material. No additional recovery model request in this primary lane;
its setup invoice is a separate future extension, not silently free.

```
c     = pw-q*(pw-pr)
kappa = pi-q*(pi-pr)
F0    = pi*compaction_instruction_tokens + po*C
A0    = F0 + (pw-c)*(S-B) + kappa*S
d     = q*(pi-pw)
rate  = pi*ordinary_suffix + po*E[ordinary_output]
        + (pw-c*theta+kappa)*g + c*S
        + (A0+c*M+d*theta*E[G_T])/U
```

theta is a declared timing/retention sensitivity, not identified by public
usage. It splits each G into current pre-call input (1-theta)G and appended
post-call tail theta G. The input-only observed increment already includes
prior output/tools; output marks contribute to output BILLING, never another
growth insertion. Initial reconstructed S is warm; no terminal compact.
Finite simulation bills the actual four categories, not just this rate formula.

For q=1,theta=1 the ordinary growth plus affine compactor constant is pw*g.
The terminal mark coefficient is pi-pw, not pi-pr: the last tail avoids a
normal cache write but is consumed by the compactor at uncached input price.
This is the engineering correction to an all-warm scalar carrying model.

## Community evidence / interventions

TraceLab pinned public source is already verified under .cache/community-data.
renewal_calibration.py extracts consecutive nonnegative full-input changes
outside the declared three-call large-drop recovery window. This is a
policy-conditioned monotone cohort, not true unfiltered task growth or a
causal compaction experiment. Marks and block weights are aligned.

- all-growth IID lane uses all accepted growth values;
- fair IID/block lane samples IID using block_marginal_weights, or uniformly
  samples intact 16-call blocks with an independent uniform initial phase;
  these have the SAME one-step marginal at every ordinary-action index;
- normal outputs use the aligned previous-output invoice mark, independent
  of the unidentified retained-tail split;
- q is scenario uncertainty, not the measured billed cache-read share;
- S=65,588,C=4,382 is the existing LangWatch median-anchored aggregate scenario,
  not a measured joint mean. B=0 or20k is a within-S decomposition intervention;
- larger C=20k scenario preserves non-summary material by increasing S by
  20k-4,382, rather than removing 15,618 tokens of documents implicitly.

## Value-focused verification

Do not add hundreds of implementation tests. Use actual symbolic identities,
the Lean renewal-ratio law, deterministic convolution/renewal residuals,
the disjoint invoice equality, and paired independent trajectory estimates.
Simulation investigates approximation/correlation/finite-horizon effects; it
does not substitute for the analytic derivation or identify a missing joint law.
Keep regenerated pools, traces, figures and logs under .cache; persist compact
source-backed results and explanatory English conclusions in docs/research.
