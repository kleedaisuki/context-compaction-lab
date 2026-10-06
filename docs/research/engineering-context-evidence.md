# Engineering workload context magnitudes: evidence and calibration

Recorded 2026-10-06. Scope: publicly inspectable production implementations and first-party measurements relevant to restored context after compaction. This replaces an arbitrary `summary=2k, documents=12k` premise with a source-anchored **aggregate** working-state scenario; it does not invent a document-size distribution that the sources do not report.

## 1. The quantities that must not be conflated

Use four components for the full post-compaction prompt:

\[
S_{\mathrm{full}}=B+L+C+D.
\]

- `B`: stable system instructions, tool schemas, project guidance, and any unchanged initial prefix.
- `L`: verbatim retained user/agent messages, recent turns, or old working state.
- `C`: newly generated compaction summary; normally compactor output.
- `D`: reloaded code/documents and other recovery input.

An observed full prompt does not identify these components. Only `C` should automatically be charged as newly generated output. Preserved text and reread files incur later input charges, not summary-output charges. A tool-schema prefix can remain cached even when the conversation changes; whether it survives depends on the exact eligible prefix boundary, not on its semantic stability alone.

The important correction is therefore **not** “make the summary enormous.” It is “do not equate a small generated summary with a small restored engineering working state.”

## 2. Quantitative evidence table

`Measured` means the source reports an observation, not that we independently reran its private experiment. `Configured` means an implementation budget or target, not an observed percentile. `Constructed` is explicitly our scenario arithmetic.

| Source and scope | Quantitative quantity | Evidence class | Correct modeling use |
| --- | --- | --- | --- |
| [LangWatch case study](https://langwatch.ai/research/finding-the-optimal-context-window), one engineer over 162 days; 287,748 deduplicated calls, 873 compactions | Median full post-compaction context **65,588 tokens**; median generated summary **4,382** | Measured, observational, single practitioner | Anchor aggregate restored state and generated-summary scale; not a documents-only estimate |
| Same case study | Fresh subagent about **30k**; growth **3,200/call below 50k**, **1,470/call above 200k** | Measured, conditional magnitudes | Initial-full-prompt and growth sensitivity; not a universal unconditional mean |
| [Factory production compression evaluation](https://factory.com/news/evaluating-compression), 36,611 messages | Removed tokens **99.3% OpenAI, 98.7% Anthropic, 98.6% Factory** | Measured aggregate reduction; vendor evaluation | Small compression products can coexist with much larger runnable prompts; no absolute recovered-token distribution supplied |
| [Claude Code context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Summary plus **five most recently accessed files** | Described production mechanism | File working-set count; file count is not a token statistic |
| [Pi compaction implementation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/compaction.md), inspected 2026-10-06 | Default **20,000-token** recent-history retention target, plus system prompt and generated summary | Configured target, not observed summary size | Include retained history separately; valid tool-call boundaries can alter the actual retained size |
| [Codex local compact implementation](https://github.com/openai/codex/blob/3f1ccb7ceb814e54314826f68d61c892e2f5a48e/codex-rs/core/src/compact.rs#L59) | Retained user-message budget **20,000 approximate tokens**, plus summary | Configured cap | Separate `L` from `C`; not a 20k summary target |
| [Codex remote-v2 implementation](https://github.com/openai/codex/blob/3f1ccb7ceb814e54314826f68d61c892e2f5a48e/codex-rs/core/src/compact_remote_v2.rs#L74) | Retained-message budget **64,000**, eligible agent message at most **10,000**, then append compaction item | Configured caps, route-dependent | Larger retained-state scenarios; never interpret the cap as median use |
| [OpenHands SDK condenser](https://github.com/OpenHands/software-agent-sdk/blob/39d34ec006f3f92f39863ca890afa5d90720a8ec/openhands-sdk/openhands/sdk/context/condenser/llm_summarizing_condenser.py#L552) | Standard constructor: **80 events**, **4 head events**; event-pressure target **40 events** | Configured event counts | Substantial retained recent history; cannot convert to tokens without event-size data |
| [Token-cost attribution preprint](https://arxiv.org/html/2609.22114v1), small real-file tasks | `jinja2/filters.py` about **14k tokens**, `rich/text.py` about **10k**; Claude tool schemas about **29k** without MCP and **44–65k** with MCP | Authors' measurement in their configuration; non-peer-reviewed | Whole-file and fixed-prefix sensitivity anchors, not typical post-compaction recovery |
| [Codex issue #36665](https://github.com/openai/codex/issues/36665), user-supplied 5.9-hour log analysis | **74 compactions**; **70/74** followed within 2 minutes by reread/retest; **119** outputs near **40,000 characters** | Primary user incident report, not representative sample | Long-running reconstruction failure mode; characters must not be relabeled tokens |

### The high-yield calibration point

The LangWatch measurement is the closest available public evidence for the requested long-lived engineering scope. Its full-context metric sums fresh input, cache writes, and cache reads, deduplicated by message identifier. The page and companion blog link no raw transcript dataset or analysis-code download that we located. Consequently they anchor a representative scenario, not a fitted joint distribution or confidence interval. [Study](https://langwatch.ai/research/finding-the-optimal-context-window), [companion methods](https://langwatch.ai/blog/context-tax-when-to-compact).

The published **28 step-equivalent** recovery proxy is excess ingestion over 25 post-compaction steps relative to each agent's own median growth. It is not 28 observed extra calls and is not a direct measurement of reread-document tokens. Do not automatically add it to a fixed-call invoice experiment. [Methods](https://langwatch.ai/blog/context-tax-when-to-compact).

## 3. Translate the evidence into parameters without fabricating a split

For a first median-anchored representative scenario, set:

\[
C_{\mathrm{scenario}}=4{,}382,\qquad
S_{\mathrm{scenario}}=65{,}588,\qquad
A_{\mathrm{scenario}}=S-C=61{,}206.
\]

Here `A` is **aggregate non-summary restored input**, not “documents reread.” It may contain `B`, `L`, and `D`. The calculation is a declared model construction from two reported marginal medians. In general,

\[
\operatorname{median}(S-C)\ne
\operatorname{median}(S)-\operatorname{median}(C).
\]

Thus **61,206 is not a measured residual median**. The original summary and full-prompt medians are also not empirical means: inserting them as fixed values defines a scenario whose expectation can be computed, not the population expectation of the source corpus.

Practical implementation implications:

1. Expose an aggregate-restored-input slot. Do not fill the documents-only field with `61,206` and describe it as measured rereading.
2. Preserve a separate generated-summary variable for output pricing.
3. Do not add another 30k stable prefix to this aggregate scenario without first subtracting its assumed share from `A`; that would double count full prompt components.
4. Treat a fully cold aggregate rebuild as one declared accounting scenario. A surviving stable prefix is an alternative, not an observed decomposition supplied by the case study.
5. With no raw trace dispersion, concentrated noise such as CV 0.05 remains the user's concentration premise/sensitivity assumption, not a fitted LangWatch parameter.
6. If using growth 1,470, label it as the study's large-context reference, and retain smaller-context/high-growth sensitivity instead of treating the band-specific statistic as universal.

A useful follow-up is a constrained split sensitivity: choose an assumed `B` inside `A`, keep total restored size fixed, and compare cold versus genuinely surviving cache boundaries. This investigates an unidentified but price-relevant component without pretending to estimate it. Selection results should identify both the size scenario and cache-survival assumption.

## 4. What implementation inspection actually teaches

Recent frontier comparison: [Beyond Token Savings](https://arxiv.org/abs/2609.32961)
(2026-09-26 preprint, not peer-reviewed) varies what/when/how much to compress
over nearly 35,000 runs on SWE-bench Verified and Terminal-Bench 1.0. Its
model- and task-dependent results reinforce separating policy mechanisms from
workload parameters. Benchmark runs are not measurements of this user's
multi-hour engineering context, so none of their configured budgets replace
the engineering recovery anchors or silently change our fixed-call objective.

### Codex: distinguish compaction routes

Pinned source commit `3f1ccb7ceb814e54314826f68d61c892e2f5a48e` was fetched on 2026-10-06. Local compact retains recent user text within its 20k budget and appends a generated summary; canonical initial context is reinjected. Remote-v2 retains selected user/agent/client-developer material within its 64k budget and then appends a compaction item. It does not preserve all old tool outputs under that budget. Agent completion/progress filtering and feature flags affect what survives. These are two mechanisms, not additive budgets.

The [official API compaction guide](https://developers.openai.com/api/docs/guides/compaction) describes an opaque compaction item, so plaintext output-length assumptions do not automatically describe every Codex/API route. [Local source](https://github.com/openai/codex/blob/3f1ccb7ceb814e54314826f68d61c892e2f5a48e/codex-rs/core/src/compact.rs), [remote-v2 source](https://github.com/openai/codex/blob/3f1ccb7ceb814e54314826f68d61c892e2f5a48e/codex-rs/core/src/compact_remote_v2.rs).

Codex's default combined project-guidance limit is **32 KiB**, not 32k tokens. It constrains only project guidance and is not a full system/tool-prefix estimate. [Official AGENTS guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

### OpenHands: a short summary is not the whole reset

Pinned SDK commit `39d34ec006f3f92f39863ca890afa5d90720a8ec` was fetched on 2026-10-06. The class-level defaults are 240 events/2 head events, but `create_default_condenser` explicitly overrides them to 80/4. Event-pressure compaction targets half the event cap, giving a nominal allocation of four head events, 35 recent events, and one summary before tool-boundary adjustment. Token-pressure removal targets the configured/effective input cap divided by two; the newly generated summary is an additional payload, not a guaranteed exact half-cap final prompt. Summary calls inherit the chosen LLM configuration rather than supplying a universal small output cap here. [Pinned source](https://github.com/OpenHands/software-agent-sdk/blob/39d34ec006f3f92f39863ca890afa5d90720a8ec/openhands-sdk/openhands/sdk/context/condenser/llm_summarizing_condenser.py).

### Claude/Factory: restore working artifacts, not just narrative

Five recent files can be much larger than a brief generated summary. Combining the described file count with the measured 10k/14k example files yields a **constructed 50–70k whole-file workload**, not a measured usual five-file set: snippets, partial reads, and small files can change it substantially. Keep that construction separate from the 65,588 full-prompt observation. [Claude mechanism](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), [file-size measurements](https://arxiv.org/html/2609.22114v1).

Factory's [compression design](https://factory.ai/news/compressing-context) separates fill threshold, retained-suffix threshold, and generated-summary cap. Its production evaluation does not supply a universal absolute default for the latter two. This is useful architectural evidence for separate variables, not permission to invent token statistics.

## 5. Engineering sessions are not a single benchmark issue

The strongest recovered-size anchor comes from real development over months with sessions, subagents, and forks, while the primary incident spans hours. Neither proves every project needs 65k restored context. Conversely, a short issue-fixing benchmark's compactable history cannot establish a multi-hour system-development working set.

As a recent research comparison, [CliffCompaction](https://arxiv.org/html/2609.26779v1) evaluates 8k/16k/32k thresholds on SWE-bench and Terminal-Bench and much longer optimization trajectories on KernelBench. Those are configured context budgets and experimental policies, not post-compaction document-size percentiles. Its comparison is relevant to threshold economics but does not override a measured full recovery payload for a different workload.

## 6. Next useful measurement

For each actual compaction, collect the pair `(generated_summary_tokens, first_post_compact_full_input_tokens)` plus preserved-item tokens, system/tool prefix tokens and eligible cached boundary, and reloaded-file/tool-result tokens over a declared recovery interval. Record both immediate landing and subsequent reconstruction rather than adding all recovery to the first request by assumption.

Deduplicate usage by message ID. Separate opaque compaction accounting from visible summary text. Estimate `E[S]`, `E[C]`, their covariance, paired residual quantiles, and cache-surviving prefix size from complete sessions. A source-anchored aggregate scenario delivers an immediately useful scale correction; these minimal joint observations are what would turn it into the requested distribution-calibrated expected-cost research result.

### Inspection reproducibility

Raw pinned files were downloaded under `.cache/research/engineering-context/` only. They are disposable upstream inspection artifacts, not vendored production code. Reproduce by fetching the pinned raw GitHub URLs corresponding to the links above, then inspect the named constants, `build_compacted_history_with_limit`, `build_v2_compacted_history`, `is_retained_for_remote_compaction_v2`, `_get_forgotten_events`, and `create_default_condenser`. The Markdown records the permanent evidence, exact upstream commits, distinctions, and calibration arithmetic; no local production source was edited during this investigation.
