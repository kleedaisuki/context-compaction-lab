# Conditional invoice economics versus successful-task efficiency

Recorded 2026-10-06 during the expanded manuscript revision. The substantive
question is whether compaction saves resources while preserving useful task
completion, not whether fixed simulated action counts finish their ledger.

## Estimands and assumptions

Fix the task population, model, tools, evaluator, initial repository state,
stopping/resource limits and retry protocol. Let Y be externally verified
success and ell the full disjoint input/write/read/output token ledger of an
attempt, including failures. T = 1^T ell and C = p^T ell. With finite resource
means and repeated iid (or appropriately ergodic) attempts, pooled completed
tasks per billed token and per dollar converge to E[Y]/E[T] and E[Y]/E[C].
They are not E[Y/T] and not resources averaged only over successes.

Cached replay counts in billed-processing tokens; unique information or output
tokens are different denominators. Dollar efficiency additionally weights the
four categories by price. Reporting both ratios, success rate and the ledger
avoids treating all tokens as economically interchangeable. Keep task mix
fixed; switching to easier tasks can inflate throughput without improving an
agent. Independent whole-attempt retries with fixed policy cost E[C]/s until
success, even when cost and success are dependent within an attempt. Adaptive
retries require their own conditional transition law.

## Exact decision structure

For positive expected resources r(h) and success s(h), eta = s/r gives

    eta' = (s' r - s r') / r^2.

An interior efficiency optimum balances relative success and resource slopes.
A cost-only optimum with C'=0 has efficiency slope s'/C; only s'=0 makes it
stationary for efficiency. Policy A is worse per dollar than B whenever
s_A/s_B < C_A/C_B. Thus a 20% bill saving can tolerate at most a 20% relative
success loss before throughput declines; this is algebra, not an observed
quality estimate for the trace cohort.

If policy-indexed success and occupations are price-independent, C=p^T m(h),
F=s'C-sC', and a smooth nondegenerate active root gives

    dh*/dp_j = -(s' m_j - s m_j') / (s'' C - s C'').

Constant success recovers the ordinary cost-optimum response. Common positive
price scaling preserves the chosen ratio-optimal policy and inversely scales
dollar efficiency. A success constraint s>=tau leaves price-envelope concavity,
monotonicity and homogeneity intact over its price-independent feasible set.
It can exclude the previously unconstrained cost optimum.

For a finite policy family with positive expected expense, lambda*=max s/C
is characterized by max_pi(s_pi-lambda* C_pi)=0. This is the classical
fractional-programming reduction, not a new algorithm. In a finite task-state
model, terminal verified-success reward and stage reward -lambda*p^T m permit
Bellman evaluation; missing obligations and policy-dependent future work belong
in the joint transition law, not an independent quality penalty.

## Executed symbolic verification

`uv run python experiments/task_efficiency_derivation.py` verified seven exact
SymPy residuals: quotient derivative, stationary-root derivative, four category
price derivatives and common scaling. Output is
`.cache/paper/task-efficiency-symbolics.json`. No dependency, simulator or success
dataset was changed. Algebra checks do not supply empirical success gradients
or certify attainment/nondegeneracy for an actual coding agent.

## Measurement that would resolve the objective gap

Run compact-policy interventions over fixed issue instances and an external
test-based evaluator. Pair instances across policies; allow subsequent calls,
tokens, recovery and retries to differ. Include failures and exhausted budgets.
Report success, pooled tasks/token, tasks/dollar, latency and success/expense
frontiers; bootstrap task instances as clusters, not individual requests.
Usage-only public traces identify the resource side, not the success response.
This task-level experiment remains future work, not a newly executed result.

## Primary grounding

- Dinkelbach (1967), Management Science 13(7), 492-498:
  https://doi.org/10.1287/mnsc.13.7.492 (fractional programming).
- Jimenez et al. (ICLR 2024), SWE-bench:
  https://proceedings.iclr.cc/paper_files/paper/2024/file/edac78c3e300629acfe6cbe9ca88fb84-Paper-Conference.pdf
  (test-based issue resolution, not action counts).
- Liu et al. (TACL 2024), Lost in the Middle:
  https://doi.org/10.1162/tacl_a_00638 (context use depends on information
  placement; additional context need not monotonically improve retrieval).

The manuscript develops the objective problem in Discussion only, with the
detailed derivation in its task-efficiency appendix. The public repository link
appears in the artifact/reproduction appendix, not the main narrative.
