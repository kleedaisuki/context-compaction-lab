# Production compaction mechanisms and mandatory file restoration

Investigated 2026-10-06. Decision purpose: identify which restoration costs a
threshold/invoice model must represent, rather than infer that removing tool
history forces every previously read file to be re-input immediately.

Internal starting points: `mandatory-reload-research-plan.md` and
`engineering-context-evidence.md`. Evidence below separates documented
contracts, source-code observations, and modeling implications. No production
code was changed and no private sessions were inspected.

## 1. Operational answer

**Use a hybrid immediate-plus-first-use model, parameterized by harness,
version, model, tool, and permission conditions.** Claude Code documents
automatic selected-file restoration; its tools also implement conditional
read eligibility. Pi and OpenHands preserve recent tool history instead of
erasing all tool calls/results. Codex local and remote-v2 replacement history
remove old tool items but rebuild canonical initial context. None of these
observations establishes an unconditional immediate reread of all files.

Distinguish five mechanisms:

| Class | Meaning | Cost timing | Enforcement test |
| --- | --- | --- | --- |
| Immediate harness restoration | Harness inserts content without the agent choosing a read | First post-compaction input | Inspect replacement window before model continuation |
| First-use automatic guidance | Reading a trigger path inserts its scoped instructions | At first matching access | Compare read result and injected messages |
| First-use compulsory file read | Edit/write is refused unless a qualifying read happened | Before the first eligible operation | Directly attempt the same edit before and after compaction |
| Discretionary reconstruction | Agent chooses a read to regain detail or repair a stale match | Workload-dependent | Successful direct edit disproves a compulsory guard for that condition |
| Narrative reminder or warning | Prompt advises rereading or warns about forgetting | No guaranteed read by itself | Do not equate instruction wording with tool rejection |

An implementation-internal disk read is not a model-visible reload. For
example, an edit tool can read disk to match an old string and return only a
diff; its internal file bytes do not automatically become API input tokens.

## 2. Mechanism matrix

| System / route | Removed versus retained tools | Immediate restoration | Later compulsory or automatic access | Stable boundary |
| --- | --- | --- | --- | --- |
| Claude Code, current official docs | Conversation replaced by structured summary; ordinary historical reads summarized | Selected recent files and startup material; oversized file content excluded | Scoped guidance on matching read; conditional Edit/Write eligibility | System/tool layer can survive; changed conversation rebuilds |
| Codex local, pinned source | Retains real user messages, not tool call/output tail | Canonical initial context plus plaintext summary | Compactor itself schedules no all-file reread; downstream/task contracts must be checked separately | Base instructions are separate from history |
| Codex remote-v2, same pin | Selected user/client-developer/agent messages; tool items fail retention predicate | Canonical initial context plus opaque compaction item | No all-file reread loop in inspected replacement path | Reconstructed initial context, not proof of a fully cold request |
| Pi, pinned source | Older history summarized; recent tool call/result groups remain intact | Current system message carried into checkpoint; file *paths* appended to summary | Built-in edit matches current disk content without a prior-read registry check | System message preserved; provider cache outcomes not measured |
| OpenHands SDK condenser, pinned source | Middle events summarized; head and recent tail preserved at atomic boundaries | Summary inserted at removed middle; leading system event protected | No reread of files in condenser; tool-level constraints remain separate | Original head/system event, not regenerated whole prompt |

## 3. Claude Code: selected eager restoration and versioned guards

Official [context-window documentation](https://code.claude.com/docs/en/context-window)
accessed 2026-10-06 describes immediate rereading of at most five read/edited
files, newest modification first. Files exceeding 5,000 tokens return as path
references, not contents. Root CLAUDE.md, unscoped rules, auto memory and plan
reload from disk; scoped rules and nested CLAUDE.md reload on demand. Invoked
skills have 5,000-token individual and 25,000-token aggregate reinjection caps.
Compact-matching SessionStart hooks can add further input. These are documented
implementation budgets, not measured file-size distributions.

The official [tool contract](https://code.claude.com/docs/en/tools-reference)
is conditional: older models require a qualifying read; newer models can bypass
it only with Read available and no read permission prompt. Edit relaxation
starts at v2.1.208; Write relaxation starts at v2.1.228. Before that Write version,
every model required reading existing files before overwrite. Notebooks and
PARTIAL-view files still require a read for Write on all models. Exact unique
string matches are independently necessary for Edit. Thus version/model/tool
must be recorded before labeling first-use rereads mandatory.

[Issue #85488](https://github.com/anthropics/claude-code/issues/85488), filed
2026-08-10, reports v2.1.220 rejecting Edit and Write after read-state loss.
That version's Write rejection agrees with the versioned contract. Its Edit
claim requires checking permission conditions or a defect; later documentation
does not invalidate reported operational failures. Treat the incident as a
configuration-specific observation, not universal current behavior. See the
separate incident artifact for transcript frequencies and sample limitations.

Official [prompt-caching documentation](https://code.claude.com/docs/en/prompt-caching)
distinguishes conversation, project context, and system layers. Compaction
invalidates conversation history but normally reuses the system layer. Disk
guidance reload hits cache only when unchanged; a resumed session's first
compact can refresh a previously held old system prompt. Summary generation
uses the original prefix with an appended summarization instruction, so warm
and expired-cache compact requests have different input bills. Stable semantic
content alone is insufficient; exact prefix, TTL, model and routing matter.

## 4. Codex: inspect routes, do not infer file reads from deleted tool items

Source pin: `3f1ccb7ceb814e54314826f68d61c892e2f5a48e`, reused from the internal
engineering evidence investigation. Relevant files:

- [`compact.rs`](https://github.com/openai/codex/blob/3f1ccb7ceb814e54314826f68d61c892e2f5a48e/codex-rs/core/src/compact.rs):
  `collect_annotated_user_messages`, `build_compacted_history_with_limit`,
  `build_compaction_initial_context`,
  `insert_initial_context_before_last_real_user_or_summary`.
- [`compact_remote_v2.rs`](https://github.com/openai/codex/blob/3f1ccb7ceb814e54314826f68d61c892e2f5a48e/codex-rs/core/src/compact_remote_v2.rs):
  `build_v2_compacted_history`, `is_retained_for_remote_compaction_v2`,
  `truncate_retained_messages`.

Local replacement selects latest user text backward under a 20,000 approximate
token budget, restores chronological order, and appends generated summary text.
The builder does not copy historical function calls/results or assistant tool
tail. Both routes explicitly build current canonical context and insert it
before the last real user message or compaction item. This is positive evidence
of immediate initial-context reinjection, **not** evidence that all formerly
read code files are reread.

Remote-v2 selects user messages, optional client-authored developer messages,
and eligible agent messages; descendant progress and completion messages are
excluded, agent messages over 10,000 estimated tokens are excluded, and selected
messages have a combined 64,000-token budget. Non-message tool items return
false from the retention predicate. Then one compaction item is appended.
These budgets are alternatives to local retention, not additive defaults.

The local compactor emits an accuracy warning after replacement. The warning
does not trigger mandatory reading. Pre/post compact hooks and executed-call
bookkeeping are separate mechanisms; existence of harness-side call state does
not mean the original tool payload remains model-visible.

Official [API compaction guidance](https://developers.openai.com/api/docs/guides/compaction)
accessed 2026-10-06 says standalone compact output is the canonical next window,
can contain retained items beyond its encrypted compaction item, and must not
be pruned. Server-side streaming compaction is another route, pruning during
inference. An opaque item's visible string size is not a plaintext summary
token count. There is no documented guarantee here that every old tool item
is deleted, or that local filesystem files are automatically restored by the
API. Harness replacement semantics and API endpoint semantics must not be
merged into a single rule.

Scope limit: this inspection establishes compactor behavior, not a proof about
every downstream Codex editing tool. A user/project read contract can impose
first-use rereading even without a compactor-scheduled read.

## 5. Pi: file provenance survives without file content reload

Source pin fetched from public main on 2026-10-06:
`28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9`.

- [`compaction.ts`](https://github.com/earendil-works/pi/blob/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9/packages/coding-agent/src/core/compaction/compaction.ts):
  defaults `reserveTokens=16384`, `keepRecentTokens=20000`; cut points avoid
  splitting tool-result groups. Older content is summarized. File-operation
  paths from older checkpoints accumulate; `formatFileOperations` appends them
  and returns `details` without reading those paths from disk.
- [`utils.ts`](https://github.com/earendil-works/pi/blob/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9/packages/coding-agent/src/core/compaction/utils.ts):
  file provenance is sets of paths, not recovered contents. Compactor
  serialization truncates individual tool results to 2,000 **characters**.
  This truncation affects the summarization request, not every retained tool
  result in the next working window.
- [`session-manager.ts`](https://github.com/earendil-works/pi/blob/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9/packages/coding-agent/src/core/session-manager.ts):
  `appendCompaction` carries current `systemMessage`; `buildContextEntries`
  yields checkpoint plus entries from `firstKeptEntryId` and later entries.
- [`edit.ts`](https://github.com/earendil-works/pi/blob/28dcce2ba45ce4a9efeb0f5b686f0be830fd89b9/packages/coding-agent/src/core/tools/edit.ts):
  `execute` reads current bytes internally, normalizes them, checks unique
  non-overlapping matches, writes updated bytes and returns edit information.
  No prior conversation-read eligibility check appears in this built-in path.

Configured recent retention is approximate and atomicity can exceed its target.
Generation caps are separate: normal history summary uses the smaller of model
output maximum and `floor(0.8*reserveTokens)`; split-turn prefix uses
`floor(0.5*reserveTokens)` and can need a second summary call. Neither configured
cap is a measured output length. One-off summaries set `cacheRetention: none`;
this request option is not evidence that the continuing agent's stable prefix
is destroyed. Extensions can replace or cancel the policy.

**Consequence:** path-preserving summaries reduce rediscovery but cannot supply
exact lost file bytes. A model may need a later read for content correctness;
that is not the same thing as a universal built-in read-before-edit guard.

## 6. OpenHands SDK: preserve prefix and tail, remove atomic middle

Source pin reused:
`39d34ec006f3f92f39863ca890afa5d90720a8ec`.
[`llm_summarizing_condenser.py`](https://github.com/OpenHands/software-agent-sdk/blob/39d34ec006f3f92f39863ca890afa5d90720a8ec/openhands-sdk/openhands/sdk/context/condenser/llm_summarizing_condenser.py),
especially `_get_forgotten_events`, `condense` and `create_default_condenser`.

Default constructor factory sets 80 maximum events and four kept head events
(class defaults are different). Event pressure targets half the event limit:
nominally four head events plus 35 recent events plus one summary. Manipulation
indices move deletion boundaries to valid atomic locations. The leading system
event is protected even when `keep_first=0`. Token pressure instead computes
required reduction to half the effective input cap; generated summary is an
additional payload. Multiple triggers choose the strictest removal.

The condenser records forgotten event IDs and summary offset rather than
reloading every file mentioned by removed events. It can refuse condensation
when a long tool loop leaves no removable atomic middle. Therefore tool-output
loss is selective, not an all-tools reset. Kept events can carry exact file
content without any new read; count them as retained input, not file restoration.

## 7. Concrete model contract

For compaction epoch `k`, let `A_k` be files actually restored eagerly, `V_k`
files whose exact relevant bytes remain in retained history, and `M_k` files
covered by a compulsory read condition for this configuration. Define the
first post-compaction qualifying use of file `f` as `tau(k,f)`.

Model explicit extra restoration input as:

\[
D_k(j)=D_k^{\mathrm{immediate}}+
\sum_{f\in M_k\setminus(A_k\cup V_k)}
r_{kf}\,\mathbf 1\{\tau(k,f)\le j\}+D_k^{\mathrm{discretionary}}(j).
\]

`r_kf` is the content actually exposed to the model, not disk file size. Partial
reads, path references, changing files and tool truncation make them differ.
The formula assumes a once-per-epoch compulsory restoration; mutation or
partial-view guards require a richer state. Immediate guidance and stable
prefix belong in the existing `B` component; retained content belongs in `L`;
generated summary in `C`. Never charge these again inside `D`.

Extra rounds are independent of file payload: harness reinjection may add
no model-chosen tool round, a direct failed edit adds an error/retry round,
and multiple reads may share one model response. Under fixed ordinary task
actions, add only policy-induced requests and outputs, not hypothetical task
quality improvements. Reread bytes then remain in context for later calls,
so invoice impact is not just the initial input price.

## 8. Discriminating probe and reproduction

Use a disposable fixture under root `.temp` with six small files, one file
larger than 5,000 tokens, nested guidance, and unique editable markers. Avoid
personal files or private transcript export.

1. Record harness version, model, provider, tools, permissions, hooks and policy.
2. Read files; save only fixture-relevant public message categories and usage.
3. Compact; inspect the first model input before requesting any new file read.
4. Directly request an Edit and, separately, Write of each marker. Distinguish
   automatic bytes, path-only references, successful unread operation, and
   explicit guard error followed by qualifying read.
5. Repeat with a file known to remain in the retained recent tail and one known
   to have been removed. Add a partial-read and notebook control if testing Write.
6. Compare same-system-prefix/cache TTL conditions. Count actual visible token
   usage and rounds, not filesystem bytes or error counts relabeled as tokens.

This inexpensive factorial probe separates eager constant reload from delayed
first-use restoration and distinguishes information need from enforced guards.
For source reproduction, fetch the pinned raw GitHub files listed above into
`.cache/research/community-mechanisms/`; prior Codex/OpenHands pins are already
in `.cache/research/engineering-context/`. Inspect the named functions. The
investigation performed source checks, not a live multi-provider experiment;
all numerical limits above are configured/documented, not measured locally.
