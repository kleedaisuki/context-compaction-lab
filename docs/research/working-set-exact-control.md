# Exact finite control of the production working-set simulator

Recorded 2026-10-06. Implemented control:
`experiments/working_set_exact_control.py`; maintained checks:
`tests/test_working_set_exact_control.py`. This note extends
[mandatory-reload-theory.md](mandatory-reload-theory.md) and uses the typed
[working-set contract](../working-set-contract.md). **All numerical workloads
below are declared synthetic controls, not measurements of production demand.**

## 1. Delivered result

The new `simulate_working_set` API has been run on all 256 eight-action iid
Bernoulli paths with their true probabilities, across six restoration,
preservation, guard, and stable-cache policies. Every positive integer threshold
from 1 through 299 was scanned, including the provably constant infinite tail.
The experiment runs the actual simulator, not another independently written
ledger or passive threshold clock. A second four-price sensitivity scan,
endogenous-cycle identity check, paired Monte Carlo control, and two-file
batching counterexample execute in the same experiment.

Important results:

1. The eight-action default-price control is cheapest **without compaction**:
   first-use minimum $0.002553517622 for all integer h >= 269. This is a real
   finite-horizon result, not a failed search or a reason to add a terminal bill.
2. With read price changed from $0.30 to $3.00 per million solely as a declared
   sensitivity test, the first-use optimum is the **whole interval 157..178**,
   with expected bill $0.004964155380. No provider-price claim is implied.
3. Retaining fewer reload tokens is not sufficient to reduce the complete bill.
   At h=100, retaining the file and read guard drops expected reloads from
   2.36175625 to 0.96813552, but increases price by $0.000130144444.
4. Actual first-use probability in the first threshold cycle is 0.725375.
   Substituting the cycle's marginal duration into an independent-demand formula
   gives 0.6399771875, an absolute error of -0.0853978125. The predictable carry
   identity remains exact.
5. A billed batched recovery round reverses the eager-versus-lazy ordering in a
   two-file fixture even though eager restores more file tokens.

## 2. Reproducible assumptions and method

Run from the repository root:

```powershell
uv run python experiments/working_set_exact_control.py
uv run pytest tests/test_working_set_exact_control.py -q
uv run ruff check experiments/working_set_exact_control.py tests/test_working_set_exact_control.py
```

The full per-integer expected curves, policy settings, token-ledger means,
plateaus, Monte Carlo estimates, and counterexample are saved in
`.cache/working-set-exact-control/results.json`. The cache file is regenerated,
not a required checked-in input. The measured run took 5.27 seconds; this is a
local execution measurement, not a performance guarantee. The three maintained
tests passed in 2.01 seconds; Ruff passed. Environment: the project's root uv
environment, Python 3.14, NumPy, and the in-repository simulator implementation.

| Declared parameter | Value |
| --- | ---: |
| Ordinary actions | 8 |
| File payload / wrapper | 24 / 2 tokens |
| Stable base / generated summary | 32 / 8 tokens |
| Non-file retained input / generated output per ordinary action | 20 / 10 tokens |
| Ordinary uncached suffix / compactor instruction | 2 / 4 tokens |
| Cache minimum / TTL | 16 tokens / no expiry |
| Initial stable base | Warm |
| Independent file demand probability per action | 0.35 = 7/20 |
| Mutations / automatic observations | None |
| Trigger / terminal compaction | Atomic / none |
| Input / write / read / output USD per million | 3 / 3.75 / 0.30 / 15 |

The path b in {0,1}^8 with k required-use actions has weight

\[
w_b=a^k(1-a)^{8-k},\qquad a=0.35.
\]

The computed finite expectation is

\[
E[C_\pi(h)]=\sum_{b\in\{0,1\}^8}w_b C_\pi(h,b).
\]

This is exhaustive enumeration, with ordinary floating-point rounding, not
Monte Carlo approximation. The total path mass and every action's demand
marginal are checked. The four disjoint invoice categories are reconstructed
from simulator-reported token totals and checked for every simulated path.
All trajectories must complete eight actions without loop failure. No cost
formula independent of the simulator drives the numerical curves.

The scanned upper bound is one plus the largest no-compaction maximum context
over all six policies. Any h above that bound cannot trigger the first reset,
and hence cannot trigger any reset. The scanned last point is checked pathwise
against infinity. This closes the search over unbounded h, not just a chosen
grid. The earlier start of the constant tail, 269, reflects the fact that the
last ordinary output cannot cause a terminal compact.

## 3. Complete invoice effects at h=100

| Policy | Expected USD | Compactions | Reload events | Reload tokens | Ordinary context area |
| --- | ---: | ---: | ---: | ---: | ---: |
| First use | 0.003353095734 | 3.000000 | 2.361756 | 61.405662 | 687.255913 |
| Eager catalog | 0.003536400000 | 3.000000 | 4.000000 | 104.000000 | 792.000000 |
| Retain file, lose guard | 0.003860417571 | 3.558291 | 2.629645 | 68.370767 | 780.998400 |
| Retain file and guard | 0.003483240178 | 3.000000 | 0.968136 | 25.171523 | 754.547885 |
| First use + surviving stable prefix | 0.003021895734 | 3.000000 | 2.361756 | 61.405662 | 687.255913 |
| Retain file and guard + stable prefix | 0.003152040178 | 3.000000 | 0.968136 | 25.171523 | 754.547885 |

The surviving stable prefix's savings are independently interpretable:

\[
3\cdot32\cdot(p_w-p_r)=\$0.0003312.
\]

The trajectories and file restoration counts are unchanged. Ninety-six tokens
move from writes to reads in expectation. Stable prefix survival is therefore
not interchangeable with preserving semantically valid but cold file text.

Preserving the file plus guard avoids semantic recovery, but retains the file
from the beginning of each reset cycle instead of waiting for demand. It must
be rewritten as a cold tail and carried through earlier requests. Expected
write tokens increase from 381.4056625 to 411.7399386 and read tokens from
629.415 to 684.0513615. These full-ledger increases exceed the saved reloads.

When guards are discarded, an available file observation can still fail the
qualifying-read contract. The new read appends another observation while the
retained old text continues to occupy context. More context can change the
next compaction time; the higher compaction count in the table is a physical
stopping-state consequence, not an isolated reload fee.

## 4. Threshold structure and finite optimum

### Exact statement

Assume a finite number of ordinary actions, finite exogenous support, integer
token counts and fixed policies. Assume h enters the ledger only through
comparisons of integer context length x with h, and not through a proportional
summary or another h-valued fee. For each demand path, and for every real h>0,

\[
C_\pi(h,b)=C_\pi(\lceil h\rceil,b).
\]

**Proof.** For integer x, `x >= h` is equivalent to `x >= ceil(h)`.
The two runs start in the same state. Induct over the request/event sequence:
their comparison results agree, so their reset, retention, recovery, cache,
and billing transitions agree. Their next integer state therefore agrees.
Finite weighted summation preserves this equality. No independence between
restoration and stopping times is used. The same reasoning applies to bounded
strict-mode transitions, though unsuccessful points must remain infeasible.

Consequently the exact expected invoice is a step function of the physical
threshold. Its derivative is zero away from jumps, which does **not** make all
thresholds equivalent. Smooth surrogate derivatives describe an approximation,
not the exact finite argmin. Report the minimizing threshold cells/intervals
and jump differences instead. For fixed h and policy, the expectation is a
polynomial of degree at most eight in a; this follows directly from the finite
Bernoulli weights, not from a renewal assumption.

### Actual minimizing intervals

| Policy | Default-read minimum USD | Default integer optimum | $3/M read stress minimum USD | Stress integer optimum |
| --- | ---: | --- | ---: | --- |
| First use | 0.002553517622 | h >= 269 | 0.004964155380 | 157..178 |
| Eager | 0.002570400000 | h >= 269 | 0.005196000000 | 157..178 |
| Retain, lose guard | 0.002553517622 | h >= 269 | 0.005326293357 | 179..182 |
| Retain + guard | 0.002553517622 | h >= 269 | 0.005071671439 | 157..178 |
| Stable first use | 0.002553517622 | h >= 269 | 0.004940155380 | 157..178 |
| Stable retain + guard | 0.002553517622 | h >= 269 | 0.005047671439 | 157..178 |

For real h the first-use stress optimum is (156,178]; for integer-token policy
configuration it is 157..178. The default optimum is (268,infinity) for real
h. The stress no-compaction first-use price is $0.005691137297, so the finite
interval lowers the full bill by $0.000726981917 (about 12.77%).

Neither curve should be presumed unimodal. Default first-use has five upward
and sixteen downward nonzero integer jumps; the stress version has nine
upward and twelve downward jumps. For example the default expected cost rises
from $0.002791064468 at h=178 to $0.002797940778 at h=179. Token-triggered
cycle regrouping and the unfinished last cycle explain why simply pushing h
up need not decrease price at every step.

Because this fixture's token-state transitions do not depend on price, each
fixed policy/threshold has expected bill linear in the four prices. Changing
read price is thus a legitimate ledger sensitivity experiment on unchanged
path mechanics, not a re-fit of the workload. The minimum over the finite
effective policy/threshold set is a lower envelope of these linear prices.

## 5. Endogenous first-cycle check

At h=100 and first-use restoration, the experiment obtains first-cycle length
T through **actual simulator prefix reruns**. If the first compact appears
before ordinary action j, the initial cycle contains j-1 actions. If none
appears, T=8 because there is no terminal compact. No separate growth ledger
is implemented to infer T.

Let K be the first required-use action. Exhaustive means give

\[
E[T]=2.4225,\quad
u=P(K\le T)=0.725375,\quad
E[(T-K)_+]=0.35.
\]

The predictable stopping identity from the earlier theory note is exact:

\[
E[T]-u/a=2.4225-0.725375/0.35=0.35.
\]

In contrast, the independence shortcut gives

\[
1-E[(1-a)^T]=0.6399771875\ne0.725375.
\]

Loading the 26-token observation changes threshold crossing. Thus the marginal
distribution of T is insufficient to reconstruct the required joint law.
This confirms the existing theoretical warning in the implementation's own
physical state model, not only in a hand-made two-action counterexample.

## 6. Batched-recovery ordering reversal

The two-file deterministic control also calls the same simulator. There are
eight ordinary actions, 32 base tokens, 8 summary tokens, two 20-token files,
zero wrappers, no ordinary generated output, and 80 retained non-file tokens
on action 1 only. Requirements: file a on action 1, b on action 2, a on
action 3; later actions require neither. Set h=120, one actual compact,
8 generated recovery-command tokens and 80 uncached recovery-instruction
tokens per model recovery round. All prices remain the default four rates.

| Recovery mechanism | First-use USD | Eager USD | Cheaper policy |
| --- | ---: | ---: | --- |
| Tool restoration only, no extra model request | 0.0010422 | 0.0011292 | First use |
| Full billed model recovery round per batch | 0.0022830 | 0.0019476 | Eager |

With model recovery, first-use has three rounds and eager has two. Eager still
restores 80 total file tokens versus first-use's 60, but saves one complete
request including current-context processing, instruction input, generated
command output, and later command-token carries. Its full bill is lower by
$0.0003354 (14.69%). No fixed per-file restoration fee is used. This is why
fixed-cycle lazy dominance cannot be generalized to batched recovery calls.

## 7. Paired Monte Carlo control and scope

The same simulator is run on 16,384 iid Bernoulli trajectories with seed
20261006, sharing ordinary-action demand across every policy at h=100. This
is a reproducibility/control check, not another empirical dataset.

| Quantity | Exact USD | Monte Carlo USD | Monte Carlo standard error USD |
| --- | ---: | ---: | ---: |
| First-use bill | 0.003353095734 | 0.003352175940 | 0.000000829738 |
| Preserve + guard minus first use | 0.000130144444 | 0.000129659766 | 0.000000725932 |
| Stable first use minus first use | -0.000331200000 | -0.000331200000 | Numerically zero |

All six means and their paired differences fall within the predeclared five
standard-error control bounds. The exact stable-prefix paired delta has zero
sampling variance because every trajectory has three compactions at h=100;
tiny floating residual variance is not substantive uncertainty.

These controls establish the mechanism and finite objective in a small,
checkable scenario. They do not estimate file demand probabilities, corpus
payload sizes, TTL distributions, provider availability, or task quality.
Next useful investigation is to retain the same full-ledger inference but
substitute observable versioned file demand and phase-dependent locality from
real traces. Do not replace the empirical workload with these tiny token
settings or conclude that first-use is universally cheaper.

## 8. Connection to prior understanding

The existing theory note already relates this problem to Denning's working
set, renewal/compensator identities, and production just-in-time retrieval.
This experiment supplies the missing bridge: those first-use mechanisms now
run through the actual shared cache and versioned-file ledger. The practical
design implication is to keep semantic file/guard state separate from prefix
warmth, compare complete paired invoices, and optimize effective threshold
cells rather than extrapolating a continuous derivative.

Relevant foundations, reused rather than researched again:
[Denning, CACM 1968](https://doi.org/10.1145/363095.363141),
[Opderbeck and Chu, SIAM Journal on Computing 1975](https://doi.org/10.1137/0204031),
and [Anthropic's production context-engineering discussion](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).
The mathematical results here are finite-enumeration and elementary induction
consequences under stated assumptions, not a claim of a new general theorem.
