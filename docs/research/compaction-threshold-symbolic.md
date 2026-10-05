# Symbolic optimization of the compaction trigger

Recorded on 2026-10-06. This investigation optimizes API invoice price versus the compaction trigger, holding ordinary task requests and outputs fixed. Task quality and task-per-token efficiency are deliberately outside scope.

## Result

Let H be the context length that triggers compaction, S the rebuilt context length including immediately reloaded project documents, g the net context growth per ordinary request, and N the fixed number of ordinary requests. Prices are USD per token. Assume normal cache reads hit and the rebuilt block is written once per reset.

If the extra compaction and recovery cost is K(H)=k_0+k_1 H, then the continuous long-run total is

\[
C_N(H)=N\left[b+\frac{p_r}{2}(H+S-g)
+\frac{g\{k_0+k_1H+(p_w-p_r)S\}}{H-S}\right].
\]

Here b is ordinary request cost independent of H. It may include all normal uncached-input, new cache-write, output, and invariant prefix charges. The reset processing K can likewise incorporate all four token prices, but excludes insertion of the rebuilt S-token block.

SymPy gives

\[
\boxed{\frac{\partial C_N}{\partial H}
=N\left[\frac{p_r}{2}
-\frac{g\{k_0+(k_1+p_w-p_r)S\}}{(H-S)^2}\right].}
\]

Define A=k_0+(k_1+p_w-p_r)S. When A>0 and p_r>0,

\[
\boxed{H_*=S+\sqrt{\frac{2gA}{p_r}},\qquad
\frac{\partial^2 C_N}{\partial H^2}=\frac{2NgA}{(H-S)^3}>0.}
\]

This is a unique interior minimum on H>S. Apply at-least-one-call and capacity constraints, H>=S+g and H<=H_max. If the trigger is expressed as a fraction theta of a fixed window W, use H=theta W and partial C/partial theta = W partial C/partial H.

## Accounting convention and derivation

A cycle of m=(H-S)/g ordinary calls has pre-call retained lengths S, S+g, ..., S+(m-1)g. H is reached after the last call, before the next cycle. Defining H as the last pre-call length instead shifts the reported trigger by g; the underlying schedule is the same.

The retained-token sum is mS+g m(m-1)/2. The baseline read sum charges p_r S on its first call, but that call actually writes the rebuilt S block. Therefore add the incremental reset surcharge

\[
F(H)=K(H)+(p_w-p_r)S,
\]

not the full reset invoice K(H)+p_w S. The difference prevents double-counting the first read. Dividing the exact cycle cost by m and multiplying by fixed N gives the continuous expression above. Only a block whose cache must actually be rebuilt belongs in this rewrite surcharge; a stable cached prefix should remain outside it.

When the compactor's old-context input is entirely billed at the cached-read rate, k_1=p_r, giving the particularly simple optimum

\[
\boxed{H_*=S+\sqrt{\frac{2g(k_0+p_wS)}{p_r}}.}
\]

An uncached growth tail and fresh compression instructions may require price corrections in k_0. A miss over the entire old prefix changes k_1 rather than merely the constant. Normal task output pricing contributes to b and does not move the optimum if normal output remains fixed; summary output belongs in k_0 or k_1 and can move it.

The positive derivative term is the marginal cost of carrying a longer context. The negative term is the marginal saving from making resets less frequent. An interior optimum equalizes them. The square root applies to the gap H-S, not directly to H or the context-window utilization percentage.

## Variable recovery size

If S depends on H, use the derivative along S(H), not the constant-S partial derivative. For incremental surcharge F(H),

\[
\frac{dC_N}{dH}
=N\left[\frac{p_r}{2}(1+S')
+g\frac{F'(H-S)-F(1-S')}{(H-S)^2}\right].
\]

For S=s_0+rho H, 0<=rho<1, and K=k_0+k_1H, set

\[
J=(1-\rho)k_0+(k_1+p_w-p_r)s_0.
\]

Then

\[
\frac{dC_N}{dH}
=N\left[\frac{p_r(1+\rho)}{2}
-\frac{gJ}{\{(1-\rho)H-s_0\}^2}\right],
\]

and for J>0,

\[
H_*=\frac{s_0+\sqrt{2gJ/[p_r(1+\rho)]}}{1-\rho}.
\]

If both recovery and reset processing are purely proportional to H, s_0=k_0=0, then J=0 and the derivative is strictly positive. There is no interior sweet spot in this model. The smallest feasible trigger wins. Fixed reset overhead or a fixed recovered base is what creates the familiar square-root balance under these assumptions.

## Numerical example and actual outputs

The rate constants reuse the earlier pricing example rather than identifying the user's account: p_i=USD 3/M, p_w=USD 3.75/M, p_r=USD 0.30/M, p_o=USD 15/M. Workload parameters are invented: N=400, g=2,000, S=20,000, k_0=USD 0.05, k_1=p_r. The ordinary per-call baseline is b=USD 0.018, from 1,000 uncached input tokens, 2,000 new cache-write tokens, and 500 billed output tokens. This baseline shifts all costs equally.

| Trigger H | Long-run total USD | Derivative USD per 1,000 trigger tokens |
| --- | --- | --- |
| 30,000 | 20.320000 | -0.940000 |
| 40,000 | 15.920000 | -0.190000 |
| 60,000 | 14.620000 | -0.002500 |
| 60,824.829046 | 14.618979 | 0.000000 |
| 100,000 | 15.770000 | 0.044375 |
| 180,000 | 19.945000 | 0.056094 |

The continuous optimum is H=60,824.829046 tokens, corresponding to m=20.412414523 requests per cycle. The derivative units concern increasing the trigger, not adding 1,000 input tokens to a single request.

The stationary threshold rises with the recovered context:

| Recovered S | Stationary H |
| --- | --- |
| 10,000 | 44,156.502553 |
| 20,000 | 60,824.829046 |
| 40,000 | 91,639.777949 |

## Exact finite horizon

For integer period m and a warm initial S-token context, let q=floor(N/m), r=N-qm, and E=floor((N-1)/m). The exact aligned-trigger ledger is

\[
C_N(m)=Nb+p_r\left[NS+
\frac g2\{qm(m-1)+r(r-1)\}\right]
+E F(S+mg).
\]

E counts actual resets before subsequent requests; no reset is charged after the task ends. An initially cold rebuilt block would require another initial insertion charge, which is a different initial condition.

The executable enumerated all m=1,...,400, including the no-compaction candidate m=400. It found m=20, an actual reached trigger H=60,000, total USD 14.483000, and 19 resets. The unconstrained no-compaction candidate costs USD 57.480000; its required context length might exceed a separately imposed model capacity. The finite total differs from the long-run total because the initial state is warm and the terminal reset is omitted.

With constant S and fixed g, a nominal real trigger corresponds to m=ceil((H-S)/g). Thus the finite invoice is a staircase: the classical derivative is zero between schedule changes and is not defined at jumps. Use the smooth derivative for locating the long-run region, then evaluate admissible discrete schedules and no-compaction directly. An arbitrary starting context X instead of S needs a separately sized first cycle.

## Reproduction and verification

Environment: uv 0.12.9, CPython 3.14.6, SymPy 1.14.0, matplotlib 3.11.2, NumPy 2.5.3 on Windows. The environment and package caches are inside the workspace's .cache. The dependency snapshot is .temp/requirements.txt.

This is a historical record of the deterministic exploratory calculator. Its temporary scripts and generated files were not published as supported interfaces. The formal stochastic package now uses the standard root .venv, src/, and 	ests/; use the root README commands to reproduce current experiments.

SymPy asserts the general, fixed-S, proportional-S, second-derivative, stationary-point, and cycle-sum identities. Eight unittest cases passed, including numerical differentiation, exact finite sums against a separately constructed per-request ledger, no terminal reset, the warm one-call case, and invariance to fixed normal-output costs. An independent agent also derived and checked the central expressions; see compaction-threshold-independent-review.md.

Artifacts:

- .temp/compact_threshold.py: executable derivation, finite ledger, and figure generation.
- .temp/test_compact_threshold.py: focused verification.
- .cache/compaction/symbolic.txt: exact SymPy and LaTeX expressions.
- .cache/compaction/results.json: numerical parameters, results, and environment.
- .cache/compaction/threshold-cost.png: total-price and derivative curves, visually inspected.

## Scope and sources

The model does not estimate the actual recovery size, compression invoice, growth, or cache-hit rate of a real session. Stable pricing, warm reads, fixed growth, immediate recovery, and H-independent normal output are explicit assumptions. If cache hit probability, prices, growth, or ordinary output vary with H, their derivative terms must be included. This is an API billing model, not subscription quota accounting.

The prior note context-compaction-economics.md contains the production and literature background. Industry prompt caching motivates explicit prefix and write/read accounting; recent compaction-policy research motivates variable S(H) and K(H), but does not establish these workload parameters. The value of this result is the symbolic structure and a reproducible calculator, not an empirically universal 60k threshold.

- SymPy official calculus documentation: https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html
- Claude cache rates used as scenario constants: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic production context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- AutoCompact, a 2026 preprint relevant to adaptive S and K: https://arxiv.org/abs/2610.02163v1
