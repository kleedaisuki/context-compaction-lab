# Mandatory file restoration: community-to-theory synthesis

Status update: v0.2 now implements and executes this model. See
[working-set experiment results](working-set-experiments.md) and
[independent validation](working-set-validation.md). The original sections below
record the research milestone and retain their historical scope.

Recorded 2026-10-06. Five parallel tracks investigated source implementations,
community incidents/data, selected academic literature, stochastic derivations,
and alternative mathematical tools. The original fixed-normal-action objective
and four-price invoice remain unchanged. This milestone delivers a mechanism
selection and executable research probes, not a silently revised production
simulator or a new universally recommended threshold.

## 1. The modeling correction

The user's premise is useful: compaction can erase the tool observations or
read eligibility needed for a later operation, creating a compulsory restoration
cost. The correction is to model **the lost prerequisite and its next use**,
not merely increase an iid reset-size constant.

Let a required artifact identify a file/content version, relevant range, and
operation contract. Two separate failures can require a read: missing exact
facts in visible context, or an unsatisfied tool read-before-operation guard.
The repository still containing a file satisfies neither condition by itself.
Conversely, internal tool disk reads, path references and warnings do not
necessarily put file content back into a billed model input.

The useful recovery decomposition is

`immediate required reinjection + retained valid facts + delayed first-use
restoration + optional rediscovery`.

Restore only missing contract-required payloads and charge their actual timing.
Keep on-disk/external availability, visible usable facts, tool eligibility, and
exact-prefix cache reuse separate. A file version can become stale while its
old tokens remain in the prompt and continue to be billed until explicit removal.

## 2. Community evidence changes the event law

The implementation track inspected four systems and five compaction routes:

- Claude Code documents selected automatic file restoration with size limits,
  on-demand scoped guidance, version/model/permission-specific editing guards,
  and normally reusable system cache layers. Official documentation has changed
  since the older five-file article; whole large files are not universally
  reinserted. Historical incidents must be compared with their actual version.
- Pi preserves recent tool groups and file-path provenance. Its built-in edit
  tool can read disk internally without returning that entire file to the model.
- OpenHands removes a middle segment and keeps atomic prefix/tail events,
  rather than invariably deleting every tool observation.
- Inspected Codex local/remote-v2 paths discard old tool items and rebuild
  canonical initial context; the inspected compactors do not schedule rereading
  all old source files. API compaction and harness routes must remain distinct.

Therefore mandatory restoration is a **hybrid contract-dependent** mechanism.
Community failure reports support read/compact loops and repeated reconstruction,
but do not establish universal frequency or prove all lost files are required.
Restoration batching and atomic read-edit units must be visible: an automatic
compact inserted between a qualifying read and its edit can recreate the missing
prerequisite indefinitely. Our existing once-before-normal-call simulator
cannot reproduce that feedback loop; a future replay should detect it explicitly
instead of treating it as ordinary iid document noise.

Source detail and pins: [mechanisms](community-compaction-mechanisms.md) and
[incidents/data](community-reload-observations.md). Literature and limitations:
[selected papers](compaction-memory-literature.md). Denning's peer-reviewed
working-set model, SWE-agent observation refresh, and TokenPilot external
artifact recovery provide representation mechanisms, not production parameter
estimates or permission to replace the fixed-action objective.

## 3. Real community data probe

The root downloaded and parsed the complete sanitized UW SyFI TraceLab v0.0.2
JSONL release with the project uv environment, not just a website screenshot.
Attribution: UW SyFI TraceLab authors; dataset license CC BY 4.0.
[Release](https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2).

Source digest:
`11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65`.
Compressed size: 100,939,722 bytes. There are **665,453 rows**, **52 pseudonymous
users**, **8,058 distinct session IDs**. Provider/project-qualified grouping
produces 8,059 groups; this grouping distinction is recorded rather than hidden.
All 665,453 rows satisfy `total = cached_prefix + fresh_append`. All Claude
rows additionally satisfy `total = uncached + cache_creation + cache_read`.
No negative input count or duplicate qualified session-round key was observed
in this pinned release. Preserve published rows and order by round index then
ingestion ordinal; do not blindly join other releases on natural IDs.

| Per-call descriptive quantity | Claude, 305,445 calls | Codex, 360,008 calls |
| --- | ---: | ---: |
| Full input median | 149,779 | 123,895 |
| Fresh append median | 992 | 1,086 |
| Fresh append mean | 10,819.681 | 4,726.077 |
| Positive adjacent full-input delta median | 914 | 619 |
| Positive adjacent full-input delta mean | 1,857.885 | 2,873.169 |

Values are pooled call-weighted descriptions, not iid fitted moments or
post-compaction recovery statistics. A positive full-input delta can already
include document restoration; do not then add the same restoration again.
Fresh append includes cache replay and is not the same as new semantic growth.
The incident track's 19-row accounting sample demonstrates this concretely:
full context increases by 94 while fresh append increases by 6,494.

An intentionally simple detector flags an adjacent full-input drop of at least
64,000 tokens. It yields 671 Claude candidates and 4,286 Codex candidates, with
post-drop input medians 51,113 and 32,411 respectively. Median post-drop cached
tokens remain 26,230 and 20,864. **These are not confirmed compactions**:
the release supplies no explicit compact marker or file-content identities.
Provider prompt changes or other trimming can also produce a drop. The
published dashboard detector's slow-rebound condition can exclude fast
mandatory-restoration loops, so neither detector identifies the user's D.
Do not recalibrate a compulsory file-load distribution from these proxies.

Reproduction (download only the explicitly pinned public asset):

```shell
uv run python experiments/profile_public_trace.py --input .cache/community-data/syfi-v0.0.2.jsonl.gz
```

The script verifies the publisher checksum and writes aggregate-only JSON to
`.cache/community-data/tracelab-profile.json`. It publishes no per-user traces,
paths, code, credentials or raw transcript content. SWE-chat can supply richer
file-level transcripts, but the inspected upstream requires authorized access;
we did not attempt to bypass that gate.

## 4. Mathematical tool selection

The best next model is a finite-horizon, versioned working-set **reward process**
with separate prefix caching, rather than a different positive marginal family.
Start with 4 files and 8-12 fixed ordinary actions, exact state enumeration,
then extend to stochastic replay once the mechanisms are discriminated.

| Tool | Decision value | Current adoption |
| --- | --- | --- |
| Working sets / first-use hazards | Which facts are absent, next compulsory use, phase/locality | Primary event representation |
| Finite Markov reward / dynamic programming | Expected invoice with dependence and terminal boundaries | Primary small-case computation |
| Renewal reward / Markov renewal | Analytical reduction when regeneration or stationary reset chain is justified | Control/approximation, not assumed iid cycles |
| Setup/holding and lot-sizing | One-time compact/recovery fees versus integrated retained-token area | Interpretation and offline segmentation benchmark |
| Paired contrasts; IPA or score methods | Threshold sensitivity without differentiating discontinuous sample paths incorrectly | Paired contrasts now; smooth derivatives only in checked special cases |
| Partial identification / robust scenario regret | Which choices survive unknown splits, cache survival and hazards | Mechanism-consistent sensitivity before invented distribution fits |

Detailed assumptions and peer-reviewed foundations:
[model selection](compaction-model-selection.md). Adaptive MDP/optimal stopping
is optional research, not a prerequisite or an unannounced change of objective.
Next-compaction and version-change censoring are policy-dependent; naive
independent-censoring survival fits can be wrong.

## 5. Exact inexpensive result

For one initially missing fixed-version file of d tokens, required independently
with probability a before each ordinary action in an exogenous m-action cycle,

`u(m) = 1 - (1-a)^m`

and the ideal warm-cache file contribution is

`Q(m) = d*(p_w+kappa)*u(m) + p_r*d*(m-u(m)/a)`.

This includes first write, all subsequent carries and terminal compactor input.
Any genuine extra recovery inference cost must be added, not confused with local
tool I/O. Finite tasks omit unnecessary terminal compaction; this expression is
a complete-cycle analytic control.

The Monte Carlo probe uses d=12,000, a=0.08, m=20, p_w=3.75e-6 and
p_r=kappa=0.30e-6 USD/token. Its exact expected file contribution is **USD
0.074920704** for compulsory first-use loading, versus **USD 0.117** for eager
loading. A 200,000-path seeded Monte Carlo gives 0.074927124 (SE 0.000089863).
This is a constructed mechanism test, not an empirical workload estimate or
a claim that lazy loading always dominates batched/threshold-triggered recovery.

The decision track's fixed 8-action timing permutation restores 12,000 tokens
in both first-use cases, yet token-carry area changes 154,472 to 116,896 and
four-price invoice 0.1675818 to 0.1563090. The eager all-files control stays
0.2128638. Thus **equal reload volume does not identify equal invoice**.

An exact 2-action counterexample shows why stopping dependence matters:
s=0,h=2,g=1,d=1,a=0.5 gives true probability of a required load before crossing
0.75, while an independent-cycle-length plug-in gives 0.625. Restoration itself
changes the crossing time. Theory proves a useful carry identity under
predictable continuation, so dependence can be represented without abandoning
all tractable formulas. Details: [theory](mandatory-reload-theory.md).

The root SymPy probe also verifies a continuous-duration relaxation:

`r(m) = p_r*g*(m-1)/2 + K/m + Q(m)/m`,

`r'(m) = p_r*g/2 - K/m^2 + beta*(m*u'(m)-u(m))/m^2`,

where `beta=d*(p_w+kappa-p_r/a)` and K contains only non-file fixed setup fees.
The beta sign can change. Consequently compulsory reload does not always move
the sweet point in one direction as a larger constant would. This is an m
derivative under exogenous duration, **not the actual endogenous token-h
derivative**. A joint reward process is needed for that latter objective.

```shell
uv run python experiments/first_use_reload_probe.py
uv run python experiments/exact_first_use_control.py
uv run python experiments/replay_first_use_timing.py
```

Output: `.cache/experiments/first-use-reload/probe.json`. The theory track also
performed 256-path exhaustive verification and symbolic derivative checks;
maintained outcomes are in its document. Current production test suite plus
research-control tests: 85 passed on CPython 3.14.6, project package 0.1.1.

## 6. Next implementation contract and discriminating acceptance test

Minimal state: retained length, eligible prefix/age, current file version/range
coverage, read eligibility, ordinary action index (or measured phase), and
remaining fixed ordinary actions. Record immediate insertion, retained valid
facts, mandatory first-use insertion, already included ordinary observations,
optional reconstruction, extra inference rounds and actual billed categories.
Do not count an ordinary operation's automatic file view twice.

Reproduce the same fixed read-edit workflow under four conditions: no compact;
compact plus eager restoration; compact plus first-use restoration; compact
plus retained recent valid observations. Permute first-use delay while keeping
file sizes and ordinary actions fixed. Separately hold these fixed and change
the genuine stable cache boundary. Model a missing read guard explicitly and
exercise a compact inserted between read and edit to reveal a restoration loop.

Useful hypotheses:

1. If a small mandatory working set always saturates immediately, concentrated
   constant D remains a good reduction. Test saturation timing, not a new tail
   distribution by fiat.
2. Equal recovery volume but different first-use timing changes carry area and
   invoice; this rejects an immediate aggregate-only event law.
3. Semantic observation loss and cache-prefix survival have independently
   observable effects. All-cold recovery is a control, not a default fact.
4. Restoration-induced crossing or guard resets require joint state and can
   create repeated compact/read loops absent from the original simulation.

The old 100k-120k result remains conditional on the old aggregate, fully cold,
fixed-normal-call scenario. It is not promoted to a recommendation for the new
working-set mechanism. No production profile has been re-fitted from unlabeled
drop events. This research milestone instead supplies the structure and cheap
tests needed for a justified next model.
