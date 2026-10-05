# Context compaction and prompt caching economics

Recorded on 2026-10-06. This note develops a decision model for API-billed coding agents. It is not an account-specific price estimate or an implementation benchmark.

## Main conclusion

Choose compaction by comparing future context-carrying charges with the incremental cost of compaction and knowledge recovery. A small prompt is not necessarily cheap, and a large cached prompt is not free. Preserve valuable reusable state, discard obsolete observations, and make external knowledge inexpensive to recover.

## Billing semantics

In the OpenAI and Claude prompt-caching mechanisms reviewed here, billing is based on input, cache writes, cache reads, and output rather than an independent cache storage rental. Reusing an eligible prefix refreshes its lifetime without another write charge, but the read is still billed. Cache write pricing is a replacement rate, not a charge to add to ordinary input for the same tokens.

Prompt caching reuses a matching prefix, not arbitrary documents by filename or semantic equivalence. Changing earlier history can therefore prevent reuse of identical documents later in the prompt. An unchanged earlier prefix can survive compaction if its cache entry and a supported matching boundary remain available. A cache hit does not remove content from the logical context window.

Model rates, minimum eligible lengths, supported cache boundaries, and retention rules vary. Do not generalize a ten-percent read rate to every model. API pricing also does not establish subscription quota accounting or intermediary billing.

For a provider whose input categories are mutually exclusive, the task ledger is

\[
C_{\mathrm{API}}=\sum_t(p_i I_t+p_w W_t+p_r R_t+p_o O_t)+C_{\mathrm{tools}}.
\]

Here prices are per token and I, W, R are normalized disjoint uncached, written, and cached-read input counts. Normalize the provider usage schema before applying this expression; some schemas include cached tokens inside total input. Include compaction and recovery calls in the ledger. Output should include whatever generated or reasoning tokens the provider bills.

## A fixed-block break even model

Assume the current branch-specific context block has L tokens and is already warm. A compacted replacement has S tokens, including both its summary and every immediately reloaded document. Stable context shared by both branches is excluded. Let n be the number of future model requests, counting the first request after the decision. Assume subsequent reads hit cache, prices remain fixed, ordinary task additions and outputs are equal across branches, and there is no second compaction in this horizon.

Let K cover the incremental summary-generation and recovery overhead outside the replacement block. This includes the actual input and output billing of the compaction call, extra retrieval calls, and task-state reconstruction. It excludes the first write of S, which appears explicitly below. Do not count document insertion twice in K and S.

\[
C_{\mathrm{keep}}=np_rL
\]

\[
C_{\mathrm{compact}}=K+p_wS+(n-1)p_rS.
\]

Thus compaction is cheaper if

\[
np_r(L-S)>K+(p_w-p_r)S.
\]

For L greater than S and a positive read price, the real-valued crossing is

\[
n_\star=\frac{K+(p_w-p_r)S}{p_r(L-S)}.
\]

The first strictly cheaper integer horizon is floor(n_star)+1. Already-paid cache writes are sunk costs and must not be charged again to the keep branch. If replacement tokens are not cached, substitute the actual uncached-input charges instead of assuming this write-and-read pattern.

## Numerical example

Use the Claude Sonnet 4.6 rates observed in the official cache table: uncached input USD 3 per million tokens, five-minute writes USD 3.75, cached reads USD 0.30, and output USD 15. These are illustrative model-specific rates, not a claim about the user's selected model.

Set L=100,000, S=20,000, and K=USD 0.05. K is an invented scenario parameter, not an observed compaction cost. The branch-specific costs are

\[
C_{\mathrm{keep}}=0.030n,\qquad
C_{\mathrm{compact}}=0.119+0.006n.
\]

| Future requests | Keep USD | Compact USD |
| --- | --- | --- |
| 1 | 0.030 | 0.125 |
| 5 | 0.150 | 0.149 |
| 20 | 0.600 | 0.239 |

The crossing is 4.958333 requests, so compaction first wins at five. If recovery inflates S to 60,000 with other parameters unchanged, the crossing is 21.416667 and compaction first wins at 22. This captures why summary length alone is a misleading measure.

Arithmetic was checked using PowerShell double arithmetic in the workspace on the recorded date. This checks the example, not the behavioral assumptions.

## Extensions for actual trajectories

1. Use the sum of retained lengths over subsequent requests, not the initial length or final length alone. Cached token area, measured in token-requests, determines carrying cost at a fixed read rate.
2. If a reloaded document stays for m requests, it incurs its initial write or input charge and up to m-1 later reads. If it is reloaded again after another compaction, that is another event. Recovery also creates output, search actions, and possible extra task steps.
3. For a block with hit probability h, a simple expected input rate is h*p_r+(1-h)*p_miss. The miss price depends on whether the block is cached on a miss. Prefix changes and expiry affect h; h need not be identical in both branches.
4. If compaction changes outputs, task length, pricing tiers, or tool usage, keep those differences rather than canceling them. Especially expensive output and rework can dominate input savings.
5. Quality and latency are separate axes. A cache hit avoids repeated prefix processing, not all dependence on the retained context during generation. End-to-end latency need not vary monotonically with prompt length or cache hit rate.

For a deliberately simplified repeated-cycle model, suppose obsolete history grows by a tokens per request, compaction occurs every T requests, and each reset has constant incremental overhead F. Ignoring shared base context and ordinary additions, average overhead is approximately

\[
\bar C(T)=F/T+p_ra(T-1)/2.
\]

Its continuous minimizer is sqrt(2F/(p_r*a)). This is a hypothesis-generating toy model, not a production threshold: real F, recovery, quality, and hit rates depend on T. It shows why a universal percentage-full compaction rule is not an economic optimum.

The follow-up `compaction-threshold-symbolic.md` derives the trigger-length derivative with explicit recovered context, affine reset-processing cost, and the cache write/read correction. It includes an executable uv + SymPy calculator, a finite-horizon ledger, and numerical outputs. The earlier constant-overhead expression here is a special case rather than the complete accounting model.

## Engineering implications

Keep a compact stable prefix for durable instructions and frequently reused project contracts. After it, maintain a task handoff state and the recent working set. Append volatile observations later. Summarize obsolete logs and resolved branches, not repeatedly needed source facts. A stable block is useful only when the provider can match a previously written eligible boundary.

Durable notes should preserve decisions, rationale, unresolved questions, file paths, version or content identifiers, test commands and observed outcomes, and the next executable action. Store detailed evidence externally with an index so recovery targets a section rather than rereading the entire repository. Updating external notes need not rewrite an earlier prompt prefix every request; promote a new stable snapshot at a deliberate boundary.

Observation masking also changes prompt prefixes. It is not intrinsically cache preserving. Batch old-result removal at justified boundaries rather than rewriting early history on every request without considering lost reuse.

## Evidence and frontier directions

Anthropic's production context-engineering guidance combines compaction with structured external notes. This supports a layered working-state design rather than treating the conversation as the only memory.

Liu et al., TACL 2024, found position-sensitive long-context retrieval on their evaluated tasks and models. This establishes that availability in context and effective use are distinct; it does not determine degradation for a particular 2026 model.

The Complexity Trap, a NeurIPS 2025 DL4Code workshop paper, compares masking and summarization in coding-agent settings. Its results motivate a simple masking baseline and a hybrid policy. They do not prove cost superiority under every vendor cache scheme.

AutoCompact, submitted on 2026-10-01 as an arXiv preprint, jointly learns compaction decisions and continuation. It motivates adaptive timing. The reviewed abstract establishes neither peer-reviewed status nor optimization against the specific four-rate invoice used here.

## A useful next experiment

Compare late compaction, phase-boundary compaction, and observation masking followed by occasional summaries on matched repository tasks. Use one model version and harness configuration, identical initial repository snapshots, and report cache TTL, temperature, reasoning setting, and price schedule. Run separate warm-cache and expiry-prone cohorts; replaying traces only measures invoice counterfactuals, not altered agent behavior.

Record disjoint input categories, billed output, compaction overhead, reloaded content volume and residence, extra recovery actions, time to first token, total completion time, and accepted task outcomes. The primary economic measure is total spend divided by accepted completions, with correctness and compatibility checks and a latency guardrail. Include incomplete attempts in spend. For interaction-heavy tasks, avoid attributing human waiting time to model latency.

Research question: Can phase-aware context selection reduce cost per accepted task by preserving repeatedly useful invariants while evicting expensive low-value history, compared with a fixed occupancy trigger? Start with a rule-based controller before training a learned policy.

## References

- OpenAI official prompt caching documentation: https://developers.openai.com/api/docs/guides/prompt-caching
- Claude official prompt caching documentation and rates: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic production context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Liu et al., Lost in the Middle, TACL 2024: https://aclanthology.org/2024.tacl-1.9/
- Lindenbauer et al., The Complexity Trap, 2025 workshop camera-ready: https://arxiv.org/abs/2508.21433v3
- Zhang et al., AutoCompact, 2026 preprint: https://arxiv.org/abs/2610.02163v1
