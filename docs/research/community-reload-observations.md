# Community observations: rereading after compaction

Recorded 2026-10-06. Decision: whether engineering compaction costs should be a
constant immediate reload or file-specific restoration at later first use.
Scope: primary community incidents, public data availability, and a cheap probe.
Mechanism contracts are owned by community-compaction-mechanisms.md.

## Decision-ready findings

1. **Actual refusal can force restoration**, but only for touched files under a
specific tool/model/version/permission contract. Do not make all previously read
files mandatory.
2. **Repeated discovery and mandatory recovery are different.** Public incidents
contain both. Classify errors and successful tool calls separately.
3. **Strong public cost data now exists.** SyFI supplies per-call token/cache/tool
metadata, but removes file identity. SWE-chat supplies real public transcripts
and Git history; access/schema completeness must be checked before joining the
two types of measurement.
4. **A structural compaction detector can censor the failure of interest.**
SyFI rejects drops that rebound quickly; rapid reload loops need explicit
boundary markers or a separate fast-rebound stratum.
5. **Byte counts do not identify billed recovery tokens.** Count returned ranges,
truncation, and actual API usage, not physical file bytes.

## 1. Primary incident evidence

| Primary report | Observed / author-reported quantity | What it supports | What it does not support |
| --- | --- | --- | --- |
| [Claude Code #85488](https://github.com/anthropics/claude-code/issues/85488), TomasBihari, Aug 10, 2026, v2.1.220 | Read-before-write error in 340/5,096 transcript files; two windows report 155/2,006 versus 231/1,084 occurrences/transcripts | Prior successful reads can cease satisfying a subsequent write; first-use refusal creates an extra round trip | Population incidence, independently audited raw corpus, or unconditional present-day Edit requirement |
| [Claude Code #68709](https://github.com/anthropics/claude-code/issues/68709), gtapps, Jun 15, 2026, v2.1.178 | Repro sketch: approximately 15 files collectively cross the threshold before cross-file editing; subsequent full reads refill context | A feasible multi-file restoration/compaction feedback trap | Exact tokens, universal threshold, or maintained reproducible fixture |
| [Codex #16839](https://github.com/openai/codex/issues/16839), r0b0c0ck, Apr 5, 2026, gpt-5.3-codex/xhigh | A 610 KB specification read 53 times, 93 KB analysis 24 times, 58 KB plan 17 times; three files approximately 90% of reads | Highly concentrated repeated file working set; grep/sed mitigation reportedly reduces it | Bytes returned per read, tokenizer counts, proven 10–20x API invoice inflation, or representative distribution |
| [Codex #29354](https://github.com/openai/codex/issues/29354), SocialK, Jun 21, 2026 | Bounded builder/validator/schema task in roughly 30 case folders; after 6+ hours only one file changed (+173 lines) | Multi-file engineering reconstruction loop can block delivery without a huge repository | That every read was mechanically mandatory, or verified paid-token costs |
| [Codex #33498](https://github.com/openai/codex/issues/33498), eah3699, Jul 16, 2026 | Author's seven-document QA with explicit reuse instruction reportedly used roughly 8% of available context | Control condition: redundant reading also happens without loss of available context and can respond to policy | Causal compaction evidence, absolute tokens, paired API invoices |
| [Codex #36665](https://github.com/openai/codex/issues/36665), daveladouceur, Aug 3, 2026, CLI 0.146.0 | 74 compactions in 5.9 h; 70/74 followed by reread/retest within 2 min; 119 tool outputs near 40,000-character ceiling | Long sustained reconstruction tail; recovery interval must include repeated tests and not only files | A dataset of 74 independent sessions, per-file tokens, or a general 95% recovery probability |

These are author reports, not independently rerun experiments. Their reproducibility
ranges from an operational sketch to author-derived log summaries. No raw complete
sanitized transcript artifact was linked in the inspected issue bodies. No substantive
maintainer confirmation of the claimed root causes appeared in the fetched renderings.
Closure as stale/not-planned/duplicate is administrative evidence, not a technical
disproof or proof. #36665 is duplicate of #36664; count them as one incident.

### Contract/version correction for #85488

Its Write complaint is consistent with the official transition timeline found by
the mechanism track: Write relaxation starts at v2.1.228, after the reported v2.1.220.
Edit relaxation starts at v2.1.208 but is conditional on model and read/permission
availability. The report names Opus 5/4.8 and alleges both tools failed. Therefore
do not collapse Write and Edit or dismiss the report from newer documentation.
For current source links and precise conditions, see
[official tools reference](https://code.claude.com/docs/en/tools-reference) and
community-compaction-mechanisms.md. A discriminating repro must record the exact
tool, model, version, permissions, hooks, prior full/partial read, and unchanged
file content hash.

## 2. Counterexamples and community mitigation

The reuse-policy result in #33498 is an important negative control: compaction is
not necessary for redundant reads. It suggests separating discretionary rediscovery
from tool refusal, rather than assigning every repeated read to compulsory reload.

The upstream [Token Optimizer project](https://github.com/alexgreensh/token-optimizer)
describes structural summaries for unchanged rereads, checkpoint digests, and a
disk archive with selective expansion. This is a **proposed/implemented community
alternative**, not verified production-scale savings. An archive can avoid
rerunning an expensive command but expanding the full archived bytes still adds
model input. A skeleton may support navigation but cannot be assumed to satisfy a
tool's write guard or preserve exact edit strings. Claims of 8–30% savings or
180k-to-250-token substitution are README claims without a inspected paired
compaction benchmark; do not use them as calibration. Hash validity, partial-read
coverage, and a guard-respecting escape hatch are essential.

A recent retained tool-result tail is another counterexample to universal rereading:
if the required payload survives and the tool contract accepts it, reload is zero.
Source-pinned tail mechanisms are in the mechanism track, not inferred from issues.

## 3. Public data that can answer different parts of the question

### SyFI TraceLab: usable public per-call invoice metadata

[Release v0.0.2](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2),
published July 24, 2026, supplies 665,453 model-call rows, 8,058 sessions,
52 pseudonymous users, and 743,819 tool calls. Assets are CC BY 4.0:

- [DuckDB, 160,182,272 bytes](https://github.com/uw-syfi/TraceLab/releases/download/v0.0.2/syfi_coding_trace.duckdb),
  SHA-256 `a7bab286bc640844560850965ccf47975cf66407154132abaab90f27ec9be744`.
- [JSONL.GZ, 100,939,722 bytes](https://github.com/uw-syfi/TraceLab/releases/download/v0.0.2/syfi_coding_trace.jsonl.gz),
  SHA-256 `11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65`.
- [Paper](https://arxiv.org/abs/2606.30560).
- [Pinned schema](https://raw.githubusercontent.com/uw-syfi/TraceLab/v0.0.2/artifacts/utils/DB_SCHEMA.md).
- [Small public sample](https://raw.githubusercontent.com/uw-syfi/TraceLab/v0.0.2/example_sessions/sanitized/round_trace.jsonl).

The release metadata is more current than its README, which still describes
v0.0.1. Do not combine stale README denominators with v0.0.2 statistics.

Schema: `rounds` has total input, prefix, newly appended, output, reasoning,
Claude uncached/cache-creation/cache-read counts, event-size counts, and trigger.
`tool_calls` has tool names, error flags, input/result characters, timestamps,
and command continuation relationships. File paths, tool arguments, raw outputs,
and prompts are deliberately stripped. Thus it estimates cost/context/cache
distributions, **not same-file reread probability**.

Join children with surrogate `round_pk`; source `round_id`, `trace_key`,
and `(session_id, round_index)` are not unique. Ordering is
`round_index, ingest_seq`. The schema warns that indiscriminate deduplication
changes the preserved dataset. Audit duplicate identities before any invoice sum.

[Published compaction analysis](https://tracelab.cs.washington.edu/exp/session/session_compaction_counts/)
detects a drop of at least 64k, preceding input at least 75% of the observed
session peak, and no rebound to 75% of the pre-drop level in the next three steps.
This is an inference, not an explicit boundary field. It reports 2,520 events,
712/8,058 sessions with compaction, and conditional mean 3.5 events.
**Our inference:** it is unsuitable as the only detector for rapid forced-reload
loops, because such loops can satisfy the drop criterion and fail the slow-rebound
criterion. Preserve both slow and fast recovery strata.

### SWE-chat: real public file-access identities and Git history

[Project website](https://www.swe-chat.com/) reports V2 data through Sep 4, 2026:
approximately 18K sessions, 707 public repositories, 2M tool calls, and 54.9K
checkpoints. It links complete session transcripts to resulting Git history.
[Dataset](https://huggingface.co/datasets/SALT-NLP/SWE-chat);
[paper](https://arxiv.org/abs/2604.20779);
[project code](https://github.com/SALT-NLP/SWE-chat).

Access limit on this investigation: the linked dataset page returned 503 through
web fetching; direct README retrieval returned 401. The upstream project README
explicitly requires requesting dataset access and a Hugging Face token from an
authorized account; it estimates approximately 7 GB download space and 4 GB RAM.
Thus this is an access-controlled research dataset, not an anonymously available
small download. Its precise V2 counts are 17,819 sessions, 229,909 prompts, and
2,028,951 tool calls. We did **not** inspect a row,
verify cache-usage completeness, or discover actual compaction reread rates.
This is a high-value candidate requiring a small authorized public sample check,
not yet a fitted distribution. Public sharing selection also differs from all
professional developer sessions.

### Small public benchmark traces: instrument tests, not workload calibration

[Yi30's 20 DeepSeek V4/mini-swe-agent traces](https://huggingface.co/datasets/Yi30/deepseek-v4-swebench-trajectories)
document full command/output histories and assistant response usage; ten tasks
under each of two thinking modes. Useful for parser/repeated-file detector tests.
They are SWE-bench tasks with a particular harness; no demonstrated natural
multi-hour compaction events or representative recovery measurements. Do not
substitute benchmark trajectory totals for engineering restoration.

## 4. Actual cheap probe performed

Downloaded only the public SyFI example and schema to
`.cache/research/community-reload/syfi-sample-v0.0.2.jsonl` and
`syfi-schema-v0.0.2.md`. PowerShell parsed JSONL and selected accounting fields.
There are 19 rows: 10 Claude and 9 Codex. No >=64k drop occurs; this validates
schema/accounting, not a compaction distribution.

| Public sample step | Total input | Cached prefix | Newly appended | Output |
| --- | ---: | ---: | ---: | ---: |
| Codex round 2 | 10,058 | 9,856 | 202 | 59 |
| Codex round 3 | 10,152 | 3,456 | 6,696 | 233 |

Total context grows by 94 while fresh append grows by 6,494. This is direct
sample evidence that fresh-prefill/append spikes need not imply newly restored
files or compaction. Possible explanations include cached-prefix loss/replay;
the sanitized sample cannot identify a specific cause. Never interpret append
mass alone as file restoration.

Reproduce without scanning private sessions:

```powershell
$base = 'https://raw.githubusercontent.com/uw-syfi/TraceLab/v0.0.2/'
Invoke-WebRequest ($base + 'example_sessions/sanitized/round_trace.jsonl') -OutFile .cache/research/community-reload/syfi-sample-v0.0.2.jsonl
$rows = Get-Content .cache/research/community-reload/syfi-sample-v0.0.2.jsonl | ForEach-Object { $_ | ConvertFrom-Json }
$rows | Select-Object provider,round_index,input_tokens_total,prefix_tokens,newly_append_tokens,output_tokens
```

## 5. Minimal project replay and decisive next measurement

Use public or fabricated fixtures inside this repository, not unrelated private
session directories. Fix a source revision, files, intended edits, and task-action
sequence. Compare four replay conditions:

| Condition | Purpose |
| --- | --- |
| No compaction | Baseline action plan and repeated-read policy |
| Forced compaction before first edit | Separate immediate restoration from first-use refusal |
| Same boundary with accepted read state / retained tail | Zero-reload counterexample |
| Same boundary with unchanged-file skeleton/targeted range | Test minimum payload, not assumed full-file reload |

Record explicit boundary marker, immediate landing prompt, file pseudonym and
content hash, prior coverage ranges, first-use distance, tool rejection, actual
returned payload tokens, cached/fresh/output usage, and edits completed.
Use a targeted file with an exact-string edit plus a large unrelated file;
then a 15-file fixture that exceeds headroom if blindly reloaded. This cheaply
distinguishes `all files immediately`, `touched files at first use`, and
`no restoration required`. Include a changed-file condition to ensure the
cache does not hide a stale-data correctness failure.

The theory-ready record is `(file_id, size_returned_tokens, next_use_distance,
read_required, restored_in_tail, refusal_rounds)` per compaction, plus the
per-call invoice fields. Measure shell-result/output truncation separately.
Freeze ordinary edits/searches; restoration-only tool calls are an explicit
additional-call component, not silently added to fixed-call work.
