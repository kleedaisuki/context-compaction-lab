# Independent derivation: compaction trigger versus API price

Recorded on 2026-10-06. This is a mathematical review of the repeated-cycle model, not an empirical claim about real task behavior. It extends `context-compaction-economics.md`. The user explicitly excludes task-quality/token-efficiency optimization for this investigation.

## Definitions and exact cycle accounting

Rates `p_i, p_w, p_r, p_o` are mutually exclusive ordinary input, cache write, cache read, and output prices per token. `g > 0` is retained-context growth per normal request. Threshold `H` triggers a reset to `S(H)`, including the summary and immediately reread documents. A cycle has `m = (H-S)/g` calls, initially assuming this is an integer. Pre-call retained lengths are `S, S+g, ..., S+(m-1)g`; the threshold is reached **after** the final call. A last-pre-call threshold convention shifts H by g.

Normal per-call cost `b` includes new input/output charges independent of H, e.g. `p_i i + p_w w + p_o o` for disjoint new-token categories. Appended tokens become the later cached prefix; their initial write is in b, their later reads are in the retained-length sum. Fixed stable prefixes are excluded from H and S or absorbed as an invariant per-call charge.

Let `K(H)` be additional compaction/recovery cost excluding the initial insertion of S. It can incorporate all four prices: `p_i I_c(H) + p_w W_c(H) + p_r R_c(H) + p_o O_c(H)` for mutually exclusive compaction-input counts. Additional recovery calls and outputs also belong in K if not already charged elsewhere.

There are two distinct reset-cost definitions:

- **Full reset cost:** `Q(H) = K(H) + p_w S(H)`.
- **Incremental reset surcharge:** `F(H) = Q(H) - p_r S(H) = K(H) + (p_w-p_r)S(H)`.

The read credit is necessary: the baseline retained-length sum already includes the first S-token read, but that first call writes S instead. Therefore the exact cycle price is

\[
C_{\rm cycle}=mb+p_r\left[mS+\frac{gm(m-1)}2\right]+F(H).
\]

This accounts for reread documents once at insertion and then at each subsequent read. Do not also charge their insertion in K. If only part of S is rewritten, replace `p_w S` and its read credit with the actual bill for that part; an unchanged cached prefix must not be charged as rewritten.

## Continuous long-run derivative

For a fixed number N of normal requests, ignoring the terminal incomplete cycle,

\[
C_N(H)=N\left[b+\frac{p_r}{2}(H+S(H)-g)+\frac{gF(H)}{H-S(H)}\right].
\]

Write `D=H-S(H)>0`. Holding N, g, prices, and b fixed gives

\[
\boxed{\frac{\partial C_N}{\partial H}
=N\left[\frac{p_r}{2}(1+S')
+g\frac{F'D-F(1-S')}{D^2}\right].}
\]

Any interior stationary threshold must satisfy

\[
\boxed{p_r(1+S')D^2+2gF'D-2gF(1-S')=0.}
\]

For full reset Q instead, substitute `F=Q-p_r S`, `F'=Q'-p_r S'`. Using Q directly in the baseline formula would double-charge the first read.

## Constant reset length and affine compaction overhead

Let S be constant and `K(H)=k_0+k_1 H`. Define

\[
A=k_0+(k_1+p_w-p_r)S.
\]

Then

\[
\boxed{\frac{\partial C_N}{\partial H}
=N\left[\frac{p_r}{2}-\frac{gA}{(H-S)^2}\right],\qquad
\frac{\partial^2 C_N}{\partial H^2}=\frac{2NgA}{(H-S)^3}.}
\]

For `A>0, p_r>0`, the unconstrained continuous minimum is

\[
\boxed{H_*=S+\sqrt{\frac{2gA}{p_r}},\qquad
m_*=\sqrt{\frac{2A}{p_r g}}.}
\]

Although affine compaction processing contributes `g k_1` as a threshold-independent cost, it also contributes `k_1 S` to A: retained base state is reread at every compaction, while new growth is read once per cycle. If the compactor reads H entirely from warm cache, `k_1=p_r` and `A=k_0+p_w S`; this cancellation is exact. If it reads ordinary uncached input, `k_1=p_i`, producing a different optimum. If summary output grows with H, its output-price contribution belongs in k_1.

If full reset is parameterized instead as `Q=f_0+f_1 H`, then `A=f_0+(f_1-p_r)S`, the same result with a different intercept. If A is nonpositive, the derivative is positive everywhere and the smallest feasible threshold is best within this model. Threshold caps and at-least-one-call constraints must be applied.

For integer m, average cost differs between neighboring cycles by

\[
\bar C(m+1)-\bar C(m)=\frac{p_r g}{2}-\frac{A}{m(m+1)}.
\]

The optimal integer m is the first m >= 1 satisfying `m(m+1) >= 2A/(p_r g)`, subject to caps; equality gives a tie with m+1. Equivalently compare floor and ceil of the continuous optimum, with constraints. This minimizes long-run average, not necessarily a short finite task.

## Reset length grows proportionally with threshold

Let `S(H)=s_0+rho H`, `0<=rho<1`, still with `K=k_0+k_1 H`. Feasibility requires `D=(1-rho)H-s_0>0`; at least one normal call requires D>=g. Set

\[
J=(1-\rho)k_0+s_0(k_1+p_w-p_r).
\]

Then

\[
\boxed{\frac{\partial C_N}{\partial H}
=N\left[\frac{p_r(1+\rho)}2-\frac{gJ}{((1-\rho)H-s_0)^2}\right].}
\]

If J>0, the unconstrained optimum is

\[
\boxed{H_*=
\frac{s_0+\sqrt{2gJ/[p_r(1+\rho)]}}{1-\rho}.}
\]

The second derivative is `2NgJ(1-rho)/D^3 > 0`. If J<=0, the smallest feasible threshold is best. In particular, with **purely proportional** retention `s_0=0` and purely proportional overhead `k_0=0`, J=0 and there is **no interior sweet spot**. Increasing H merely increases average context carrying; reset overhead per call is independent of H. An interior square-root optimum requires a fixed component of reset/retention overhead (or some other nonlinear mechanism). This is a useful counterexample to assuming a sweet spot must always exist.

## Finite horizon and no compaction

For constant S, suppose N calls start at an already warm S-token state. Let `q=floor(N/m)`, `r=N-qm`, and `k=ceil(N/m)` be the number of nonempty cycles. No compaction is done after the final call. The exact aligned-threshold invoice is

\[
\boxed{C_N(m)=Nb+p_r\left[NS+
\frac g2\{qm(m-1)+r(r-1)\}\right]+(k-1)F(S+mg).}
\]

The `k-1` excludes the already-paid initial reset. If the initial state must instead be freshly built, replace it by k; this is a different initial condition. If the actual initial warm context is X rather than S, use a first cycle of length `ceil((H-X)/g)`, then cycles of `ceil((H-S)/g)`; an exact simulator is less error-prone than silently assuming X=S.

For integer calls a nominal threshold is crossed by an overshoot: the actual compaction context is `S+g ceil((H-S)/g)`. Costs are a staircase in H for constant S. A smooth derivative is an approximation to long-run average, not a derivative of the exact finite invoice. If S itself varies continuously with H, the finite invoice can be piecewise smooth but still has changes in reset count and cycle length.

The **no-compaction** candidate `m>=N` is

\[
C_{\rm no\ reset}=Nb+p_r\left[NS+\frac{gN(N-1)}2\right].
\]

Always compare this candidate to compacting policies; amortized analysis can propose a threshold that never repays its reset cost before the task ends. A task starting from another warm X has the same expression with X in place of S. A hard context capacity may make no-compaction infeasible.

## Verification and scope

`../../.temp/verify_threshold_derivation.py` verifies the general, constant-S, and proportional-S identities using SymPy. Run with uv and workspace-local cache configuration. These are symbolic identities, not estimates of unknown workload parameters. The model assumes stable prices, steady growth, immediate recovery, successful cache matching, H-independent normal outputs, and no task-quality effect. Variable cache-hit rates, context-dependent price tiers, or H-dependent g/b must be added explicitly; otherwise their derivatives are being assumed zero.
