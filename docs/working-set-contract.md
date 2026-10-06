# Working-set simulator v0.2 integration contract

Implementation completed 2026-10-06. Actual experimental results:
research/working-set-experiments.md; exact controls:
research/working-set-exact-control.md. Legacy interfaces remain supported.

Started 2026-10-06. Owner: root integrator. This is the agreed implementation
interface for the refactor; legacy APIs/commands remain reproducible.

## Objective and event order

Fixed ordinary action count N; charge all additional compactor/recovery model
calls. Prices are the existing four disjoint Pricing fields. No task-quality
denominator. Files are current-version whole-file payload units for this first
implementation; range support is deferred, not implied.

At each ordinary action: expire eligible cache entries from the exogenous gap;
apply declared external version changes; optionally compact before the action;
retain selected valid recent file observations; optionally reload the catalog
eagerly; restore missing required facts/read eligibility; bill any additional
recovery model round; execute and bill the ordinary request; append output and
declared automatic observations. No terminal compact. Changed old file text
continues to occupy context until a real reset; invalidating a version is not
free token eviction. Required file payload is not included in background input.

Compaction: bill the complete current context once (warm prefix read, remaining
uncached input, compactor instruction, generated summary output). Rebuild stable
base + generated summary + selected valid file observations. Only an explicitly
eligible, previously warm unchanged stable prefix survives; retained tail
observations are not assumed to remain prefix-cached. Guard retention is a
separate policy flag; a preserved visible file can still need a qualifying read.

Recovery: missing files are batched before an ordinary operation. Each restored
payload/wrapper is appended once per event and becomes semantically available
at its current version. A recovery model round, when enabled, processes current
context plus a generated command/output; its full four-price ledger is charged.
Tool I/O itself is not billed model output. Recovery delay can expire cache.

Atomic mode (default): at most one compact before a read/edit unit. Strict
pre-request mode (diagnostic): recheck after restoration; if repeated compact
erases the prerequisite, bound attempts, mark infeasible/loop, and never report
truncated failure bills as successful policy costs. Summary/reset exceeding h
is recorded; hard provider capacity remains a separate configured constraint.

## Shared typed interfaces (working_set_config.py)

ArtifactSpec(name: str, tokens: int, requires_read_guard: bool=True).
WorkingSetWorkload(artifacts: tuple[ArtifactSpec,...], calls:int=400,
base_tokens:int, summary_tokens:int, pricing:Pricing,
minimum_cache_tokens:int=1024, cache_ttl_seconds:float|None=300,
normal_uncached_tokens:int=128, compaction_instruction_tokens:int=128,
file_wrapper_tokens:int=64, warm_start:bool=False,
recovery_command_tokens:int=64, recovery_instruction_tokens:int=64,
recovery_delay_seconds:float=0, max_compactions_per_action:int=8).
Also compaction_delay_seconds:float=0; these delays are policy-extra elapsed
time, excluded from the common exogenous gap marks. A cache reuse refreshes
that eligible prefix's lifetime; compactor/recovery delay can subsequently
expire it before the next request.
WorkingSetPolicy(restoration: Literal['eager','first_use']='first_use',
preserve_recent_tokens:int=0, preserve_read_guards:bool=False,
surviving_base_tokens:int=0, recovery_model_round:bool=False,
trigger:Literal['atomic','strict']='atomic').
preserve_recent_tokens is a WHOLE VALID FILE OBSERVATION budget including
wrappers, not all generic recent-turn tokens. Diagnostics reload_tokens and
retained_file_tokens include wrappers; pure payload can be separately reported.

ActionField immutable copied arrays:
- background_input/output_tokens/gaps shape (replicates,calls), integer token
  counts and nonnegative seconds; first gap zero.
- required/mutations/observed shape (replicates,calls,artifacts), boolean.
- mutations are external current-version changes BEFORE action; observed means
  automatic current-version file observation AFTER that ordinary request.
  A prerequisite read BEFORE an operation and its automatic observation AFTER
  it are different events: both supplied masks may legitimately add payload.
  Never suppress fixed ordinary observations based on restoration policy.
  Background input excludes explicit file observations; an ordinary Read need
  not declare its own result as a prerequisite. Earlier obsolete versions
  still contribute to x.

simulate_working_set(workload, policy, threshold, field)->WorkingSetResult:
per-trajectory costs,input_tokens,write_tokens,read_tokens,output_tokens,
compactions,recovery_rounds,reload_events,reload_tokens,retained_file_tokens,
context_area,max_context,overshoots,loop_failures,completed_actions,
base_cache_read_tokens. Optional additional diagnostics may be appended.
When any loop failure occurs the inference layer treats that policy point as
infeasible rather than dropping failed trajectories or averaging their bills.

Source-array identity is matched by ordinary-action index, never compact count.
Policy comparisons share the same ActionField. Whole snapshots/version history
may be represented by lengths plus current valid snapshot version/last-observed
index, not unbounded per-file text copies. Prefer vectorization over trajectories
and short helpers; do not add a generic event framework.

## Ownership

- working_set_config.py + tests/test_working_set_config.py: domain worker.
- working_set_simulation.py + tests/test_working_set_simulation.py: simulator worker.
- independent tests/test_working_set_validation.py and review doc: validator.
- exact reference/control experiments and math review: theory worker.
- trace/corpus calibration, generators, inference, CLI integration, experiment
  runner, figures, integrated results: root.

All source comments/docs English; uv root .venv; outputs in .cache/.temp.
Numeric defaults are declared scenarios, not fabricated workload measurements.

## Implemented diagnostic meanings and scope

reload_events counts batches, not distinct files or calls; recovery_rounds counts
extra billed model requests. reload_tokens includes wrappers; reload_payload_tokens
does not. retained_file_tokens sums copied valid snapshots across resets, not
current resident length. context_area sums ordinary cacheable pre-output input;
extra requests and ephemeral suffix are billed separately. max_context is maximum
retained working state, not a hard provider input-plus-output capacity certificate.
loop_failures stops the affected trajectory; full-workload inference rejects
that sampled policy point. Output-only measured blocks never contain inserted
file payload, so background is declared separately and ordinary fixed observations
are never suppressed when a separate prerequisite read occurred earlier.

Whole-file snapshot requirements and qualifying automatic observations are the
v0.2 unit. Range/partial views, semantic patch reconstruction, ordinary edit-driven
revision inference, hard context capacity and provider routing/eviction remain
outside the inferred scenario. External version changes are explicit marks;
their old visible bytes still occupy context until actual replacement.
