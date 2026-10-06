# Compaction, external memory, and first-use restoration: selected literature

Recorded 2026-10-06. Scope: seven selected academic works and their leverage
for the project's **expected four-price API invoice with fixed ordinary
actions**. This is a mechanism study, not a benchmark reproduction or a
proposal to optimize quality per token. Read alongside
[mandatory-reload-research-plan.md](mandatory-reload-research-plan.md),
[stochastic-model.md](stochastic-model.md), and
[engineering-context-evidence.md](engineering-context-evidence.md).

## Decision-relevant result

The useful abstraction is **demand restoration of versioned artifacts**, not
an unconditional tax for every file ever observed. Compaction can destroy an
in-context observation while leaving the repository, a tool's editor state,
or a content-addressed external artifact intact. Mandatory restoration needs
a contract about the next operation's prerequisites. It need not happen at
the compaction boundary, need not include the whole file, and need not require
an extra model invocation. Conversely, restoring a payload once does not make
its later input appearances free.

The literature supports separating three mechanisms:

```text
ordinary fixed action -> prerequisite missing? -> restoration payload/round
                            | no
                            v
                       ordinary execution

semantic artifact residency != exact-prefix cache eligibility
```

Recent papers frequently study endogenous agent trajectories. Their measured
total savings cannot be imported into a replay that holds ordinary actions
fixed. Transfer the representation and accounting mechanisms, not their
benchmark-optimal policies, configured context budgets, or trajectory-length
changes.

## 1. Selected works and exact leverage

### 1.1 Beyond Token Savings — compression primitives versus cache layout

Satish et al., *Beyond Token Savings: A Systematic Study of Context Compression
in LLM Agents*, [arXiv:2609.32961v1](https://arxiv.org/html/2609.32961v1),
2026-09-26; inspected preprint. Sections 2 and A.5.2 separate truncation,
tool-result clearing, summarization, trigger, and depth. Clearing preserves
surrounding interactions; summarization requires an additional model call.
Its input-cost estimate is fresh agent input + 0.1 cached input + summarizer
input. Outputs are explicitly excluded. Cache counts are reconstructed, not
provider bills; Qwen serving disabled prefix caching. SWE-bench recovery from
code/patches is offered as a workload explanation, not a proved mandatory
reread rule. No explicit first-use restoration ledger or separate write/TTL
price is supplied.

**Leverage:** represent the compression primitive separately from threshold;
identify the earliest rewritten prefix boundary. Use this paper to reject
token-count-only cost proxies, not to fit four-price coefficients or an
immediate reload constant. Re-exploration that changes ordinary actions stays
outside our intervention.

### 1.2 The Complexity Trap — masking need not pay for generated summaries

Lindenbauer et al., *The Complexity Trap*,
[arXiv:2508.21433v3](https://arxiv.org/html/2508.21433v3), 2025-10-27.
The arXiv record identifies the DL4C workshop camera-ready version associated
with NeurIPS 2025, **not the NeurIPS main track**. Section 2 keeps reasoning and
actions while masking old observations with placeholders. Section 3 uses a
ten-turn tail; this is an experimental configuration, not a production
median. Appendix A reports Vertex API-returned costs for Gemini and post-hoc
Alibaba-price estimates for locally served Qwen; Qwen3-32B estimates do not
distinguish cache hits/misses. Summarization overhead and changed trajectory
lengths enter its comparisons. It does not identify compulsory rereads by
file/version or first-use delay.

**Leverage:** a deterministic masking control removes summary-generation
charges while retaining action metadata and artifact handles. Do not infer
zero restoration cost or unchanged prefix hits from “no summarizer.” Masking
inside the prefix can invalidate subsequent cached tokens. Match removed
content and fixed ordinary actions before attributing savings to mechanisms.

### 1.3 TokenPilot — the most direct artifact-restoration bridge

Xu et al., *TokenPilot: Cache-Efficient Context Management for LLM Agents*,
[arXiv:2606.17016v2](https://arxiv.org/html/2606.17016v2), 2026-08-28.
The current arXiv record states **EMNLP 2026 Findings**; that accepted-venue
statement was checked, but an ACL proceedings page was not located. Section
3.2 places a structural preview in context and preserves the full payload in
a content-hash artifact registry. A recovery tool recalls it when signals
are missing, then disables further truncation for that path. Section 3.3
tracks active/completed/evictable segments and batches eviction. Section 4.1
states that hit/miss counts come from provider metadata. Appendix A.2's
Eq. 11 is hit + miss + output pricing, without independent write/TTL pricing.
The estimator's continuous PinchBench cost is separately reported as below
$0.03; inclusion in table totals is not made explicit by that equation.

**Leverage:** an artifact's identity, availability, restored status, and next
required use belong in state. Import the fallback mechanism, not its
utility-ratio objective. Byte-identical prefixes confer matching eligibility,
not unconditional hits when TTL, routing, or eviction can intervene.

### 1.4 MemGPT — retrieval changes control flow, not merely reset size

Packer et al., *MemGPT: Towards LLMs as Operating Systems*,
[arXiv:2310.08560v2](https://arxiv.org/html/2310.08560v2), 2024-02-12;
the inspected arXiv record does not establish a peer-reviewed venue. Section
2 separates main context from external recall/archival storage. Only
explicitly moved information reaches the processor. Memory operations use
function calls; pagination limits retrieval payloads, and function chaining
can return control to the model repeatedly within one user interaction.
Evaluations cover conversation and document retrieval, not fixed-action
software restoration or a four-price invoice. The paper also notes that
models can stop paging before exhausting the database.

**Leverage:** separate retrieval size from additional inference count. A
tool's local lookup does not itself generate billed model output, whereas
model-generated retrieval arguments and chained invocations can do so.
For our first study, retrieval events must be driven by declared fixed-action
prerequisites rather than a learned retrieval policy. Artifact availability
does not prove that the correct item will be found.

### 1.5 SWE-agent — durable repository state plus automatic observation refresh

Yang et al., *SWE-agent: Agent-Computer Interfaces Enable Automated Software
Engineering*, [NeurIPS 2024 proceedings](https://papers.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html),
with inspected [arXiv v1 text](https://arxiv.org/html/2405.15793v1), Sections
2–3. The interface provides file viewing, search, editing, and concise
history processing. Old observations beyond five are collapsed. Successful
edits automatically display updated file content, without an additional
command; lint failures return diagnostic snippets. This establishes a
concrete refresh pathway whose observation comes from the operation already
being performed. The paper does **not** impose a universal post-compaction
read-before-edit rule. Its per-instance $4 cap is a configured experimental
budget, not a measured cost median.

**Leverage:** track the observed file version, selected range, and which
ordinary operations already emit a refreshed observation. Count an
automatic post-edit view as that action's result, not as both ordinary growth
and a separate restoration. File-system persistence and lost prompt text
must remain distinct.

### 1.6 Denning — working sets and demand paging rather than blanket preloading

Denning, *The Working Set Model for Program Behavior*, **Communications of
the ACM 11(5), 323–333 (1968)**,
[DOI](https://doi.org/10.1145/363095.363141),
[author-hosted original paper](https://denninginstitute.com/pjd/PUBS/WSModel_1968.pdf).
Section 3 defines recently referenced information over a process-time
window; reentry occurs when a referenced item is absent. The interreference
derivation assumes iid intervals. Section 4 warns that interactive blocking
can coincide with radical working-set changes and make preloading futile.
Objects need not be literal pages, but the original setting assumes exact
program references and recoverable backing storage, not lossy summaries.

**Leverage:** estimate recent artifact/range demand and first-use delays in
ordinary-action time. Treat wall-clock cache TTL as a separate clock. A
recent-file list is a predictor, not proof that every listed file must be
preloaded. For phase-changing software work, condition demand on task phase
before fitting a stationary iid model.

### 1.7 Mattson et al. — trace-based reuse distance and its limits

Mattson, Gecsei, Slutz, and Traiger, *Evaluation Techniques for Storage
Hierarchies*, **IBM Systems Journal 9(2), 78–117 (1970)**,
[DOI](https://doi.org/10.1147/sj.92.0078),
[archival original-paper scan](https://www.bitsavers.org/pdf/ibm/IBM_Systems_Journal/092/ibmsj0902B.pdf).
The abstract and an [IBM Research primary follow-up](https://research.ibm.com/publications/efficient-stack-distance-computation-for-priority-replacement-policies)
establish the stack-processing connection: inclusion policies permit
miss-count evaluation across capacities on a fixed address trace. The
archival scan was located; the web extractor failed to open its complete
text. For conventional unit-size LRU, count distinct intervening objects
since an object's previous reference to determine its residency at a given
capacity.

**Leverage:** a cheap artifact-reference trace characterizes locality before
fitting reload probabilities. Do not translate its miss curve directly into
API cache hits: prompt-prefix matching is order-sensitive, files have unequal
sizes, summaries are lossy, and batch compaction is not unit-page LRU.
Variable-size retention or non-stack policies require explicit replay.

## 2. Coverage matrix: which mechanisms are actually accounted for?

`No` below means not supplied as the mechanism needed for this project's
estimand, rather than proof that the authors' implementation lacks it.

| Work | Monetary cache categories | Named demand restoration | Extra inference control flow | Transferable part |
| --- | --- | --- | --- | --- |
| Beyond Token Savings | Estimated fresh/cached input; output excluded | No | Summarizer calls | Primitive/trigger/depth; mutation boundary |
| Complexity Trap | Model-dependent observed/estimated cost | No | Summarizer; endogenous ordinary turns | Non-generating masking control |
| TokenPilot | Provider-metadata hit/miss plus output; no write/TTL split | Hash-registry fallback, not compulsory file-use ledger | Estimator and recovery pathway | Artifact handles; eviction lifecycle |
| MemGPT | No four-price model | Explicit external-memory retrieval | Chaining/pagination | Payload and invocation separation |
| SWE-agent | API cost metric, not four-price restoration ledger | Current-file views, not universal mandatory reread | Existing actions can refresh view | Contract-sized refreshed observations |
| Denning | No API pricing | Demand reentry to backing storage | Paging stall, not LLM rounds | Working-set and reuse-time law |
| Mattson et al. | Storage hierarchy, not API pricing | Trace cache misses | No LLM control flow | Reuse-distance diagnostic |

## 3. Original modeling implications for the existing invoice study

These are project deductions under explicit assumptions, not claims of new
theorems or empirical results from the papers.

### 3.1 Use two orthogonal state spaces

Keep the existing cache state (`matching prefix lengths`, entry ages,
provider eligibility) and add an artifact state:

```text
artifact key = (logical identity, version/content hash, required range)
artifact state = (external availability, in-context coverage,
                  prerequisite satisfied, refresh operation)
```

The state can initially be reduced to a small number of declared file classes
instead of tracking every repository path. A backend editor handle may remain
valid after an observation is masked; an external content hash may preserve
an old version even after the live file changes. Those cases cannot be
represented by a single scalar recovered-token count.

### 3.2 Define first-use restoration without double counting ordinary reads

At compaction event `e`, let `E_e` be evicted artifact-version ranges. For
each `f` define `tau_(e,f)` as the first subsequent fixed ordinary action
whose declared prerequisites require that missing information. Set it to
infinity when it is never required. Let `b_(e,f)` be the required payload
size, not necessarily the whole-file size. Partition each resulting read:

- An immediate compulsory reinjection is explicit boundary recovery.
- An extra read needed before a fixed ordinary edit is delayed mandatory
  restoration.
- A read already present in the fixed ordinary action stream is ordinary
  work, even if it also restores knowledge.
- A changed agent search strategy is discretionary/endogenous rediscovery
  and is excluded from this intervention.

For a declared post-compaction segment of length `L`, the newly restored
payload is

\[
D_e(L)=\sum_{f\in E_e} b_{e,f}\,\mathbf 1\{\tau_{e,f}\le L\}.
\]

If sizes are fixed,
`E[D_e(L)] = sum_f b_(e,f) P(tau_(e,f) <= L)` for fixed `L`. For a random
next-compaction time use the joint event, not a product of marginals:
`E[sum_f b_(e,f) 1(tau_(e,f) <= L_h)]`. Restoration itself changes retained
size and can change `L_h`; this coupling belongs in the transition kernel.
Repeated eviction of the same version requires a fresh residency episode,
not an “ever restored” flag.

### 3.3 Charge events, not an abstract page-fault penalty twice

Use the existing disjoint ledger
`p_i I + p_w W + p_r R + p_o O` on every actual inference. Restored tool text
is input on its next model appearance; it is not model-generated output.
If an extra inference generated the read call, charge that inference's old
context and arguments/output as well. Cache writes replace the corresponding
uncached-input category. Persistent restored content can subsequently be
cache-read repeatedly. Costs for a local disk lookup are outside this API
invoice unless an external service charge is explicitly added in a future
estimand.

Under a strictly append-only retained prompt, inserting a new suffix need not
invalidate a matching earlier prefix. Moving the payload to an earlier
message or rewriting a summary can invalidate everything after the changed
boundary. Accordingly, “reread bytes” and “cold bytes” need separate measures.

### 3.4 A small discriminating example, not an empirical calibration

Construct a four-ordinary-call segment after a reset. Evict two available
immutable artifacts: `A=1,000` tokens, `B=9,000` tokens. The fixed stream
needs A at call 1 and never needs B. Compare whole-set immediate reinjection
with first-use reinjection. Assume no intervening compaction, identical
ordinary output, unchanged summary/prefix, and one initial cache write then
three eligible reads for restored suffixes.

| Restoration rule | Initial restored payload | Payload appearances across 4 calls | Payload contribution to invoice |
| --- | ---: | ---: | --- |
| Immediate whole-set | 10,000 | 40,000 | `10,000 * (p_w + 3*p_r)` |
| First required use | 1,000 | 4,000 | `1,000 * (p_w + 3*p_r)` |

The difference is `9,000 * (p_w + 3*p_r)`, even though the deleted set is
identical. If A is needed only at call 3, first-use contributes
`1,000 * (p_w + p_r)`. An extra compulsory recovery-model round adds its
complete ledger and may outweigh some savings. These hand calculations are
reproducible by substitution and make no provider-price or traffic claim.

## 4. Minimal useful probe and adoption boundary

Before implementing an elaborate semantic eviction policy, collect a
sanitized fixed-operation trace with event index, artifact version/range,
tokenized payload size, lost-observation boundary, actual prerequisite
failure, restoration delay, and whether a normal operation already refreshes
the view. Record model invocations and provider input/write/read/output usage
separately. Do not publish repository content, credentials, or local paths.

Replay three contracts over the same ordinary operations:

1. All evicted payloads are immediately required (current aggregate control).
2. Only the next required artifact/range is restored at first use.
3. The tool's durable editor/artifact state survives; an ordinary operation
   already supplies the necessary fresh view where its contract allows it.

Report the immediate payload, fraction of evicted bytes never reused before
the horizon, first-use delay distribution, restored ranges rather than whole
files, extra compulsory invocation count, earliest mutated prefix boundary,
and paired expected invoice differences across the same threshold grid.
The discriminating value is identifying which contract predicts actual
restoration, not accumulating more masking benchmarks.

**Adopt now:** demand/availability state, precise operation contracts, and
explicit recovery invocations in a small replay. **Defer:** learned utility
estimators, semantic paging agents, variable-size cache policy optimization,
and quality-utility objectives. Classical locality can supply a tractable
demand law; the current four-price transition kernel can price it without
changing the decision question.

## Provenance and reproduction scope

Sources were located by English queries for the named papers, opened at the
versioned links above, and checked against current arXiv abstract metadata
on 2026-10-06. Initial reads of older versions were followed by v3/v2 checks
for Complexity Trap, TokenPilot, and MemGPT. Sections cited above distinguish
author measurements, configured parameters, inferred mechanisms, and our
constructed arithmetic. No paper experiment, production trace fitting, API
run, or empirical cache measurement was performed for this note. The
original-paper scan limitation for Mattson is explicit; IBM's primary
follow-up verifies the particular stack-distance property used here.
