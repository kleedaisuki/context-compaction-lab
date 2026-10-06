# Independent working-set validation

## Basis and method

Expected behavior comes from `docs/working-set-contract.md`, not implementation
internals. Maintained independent checks are in
`tests/test_working_set_validation.py`. All fixtures use a single deterministic
trajectory: base 10, summary 2, file payload 5 plus wrapper 1, normal ephemeral
input 1, compactor instruction 2, recovery command 3, recovery instruction 2.
Distinct input/write/read/output prices 1/2/3/4 expose classification mistakes.
These are deliberately artificial counting fixtures, not empirical pricing.

## Hand ledgers

| Case | Uncached input | Cache write | Cache read | Generated output |
|---|---:|---:|---:|---:|
| Cold one call, background 3, output 4 | 1 | 13 | 0 | 4 |
| Warm two calls, background 3/1, output 4/2 | 2 | 8 | 23 | 6 |
| Same warm trajectory, reset at 17, stable base survives | 8 | 6 | 33 | 8 |
| Missing file with generated recovery command | 3 | 19 | 10 | 3 |
| Missing file without generated recovery | 1 | 16 | 0 | 0 |
| Reset at 17 after cache expiry | 21 | 16 | 10 | 8 |
| Mutation between two file-required calls | 2 | 22 | 16 | 0 |

The mutation case preserves obsolete text in billed history while restoring the
new version. Recovery first processes the current context and generates the
command; tool payload is appended afterward. Generated commands are output once
and input on the next request. Preserving file content does not itself preserve
read eligibility or cache placement. Additional tests distinguish eager unused
catalog restoration, automatic observations, precondition/postaction separation,
atomic action completion, strict reset/read failure, and no terminal reset.

## Execution

Executed on 2026-10-06 using Windows PowerShell, repository-root uv `.venv`,
Python 3.14.6, NumPy 2.5.3, pytest 9.1.1. Reproduce:

```powershell
uv run pytest tests/test_working_set_validation.py -q
uv run ruff check tests/test_working_set_validation.py
uv run pytest -q
```

Observed: independent suite **23 passed in 1.12 s**; Ruff clean; complete suite
**277 passed in 10.80 s** at the latest CLI integration snapshot. Added inclusive TTL
checks for recovery delays and a two-trajectory strict failure test: failed
neighbor completes zero actions, successful neighbor completes one with cost 21.

## Issues and disposition

1. Initial four fixture failures were setup/contract ambiguity, not billing
   failures: empty catalogs are intentionally unsupported under the integrator's
   domain requirement. File-free ledgers now carry one unused zero-token artifact
   and false masks; this does not change any request or expected token count.
2. Inspection identified an oversized stable-base declaration risk. With base 10,
   old prefix 16 and rebuilt context 12, accepting a surviving prefix 20 could
   retain 16 and produce negative new-write counts. The simulator owner added a
   `ValueError` when the declared surviving base exceeds actual base. Independent
   regression check now requires rejection rather than accepting invalid billing.
3. Inspection identified a transient diagnostic inflation: the compactor briefly
   appended its summary to obsolete old context before replacing it. The owner
   fixed `max_context` to describe retained working states. Independent regression
   assertion expects 17, not transient 19, for the warm reset example above.
4. Follow-up checks pass for batching two missing files into one generated
   command, rejecting obsolete snapshots during preservation, and preserving
   guard-free facts without unnecessary rereads.
5. The integrator clarified the fixed ordinary stream: required restoration
   before an action and an automatic tool observation after it are distinct
   events, even for one artifact/version. Both payloads occupy context; only
   the precondition restoration increments reload diagnostics. The next request
   must bill the automatic payload. The initial contract wording on duplicate
   observations was superseded by this event-order clarification.
6. An explicit nonzero stable cache boundary below the configured minimum is
   rejected. The regression fixture uses minimum 8 and declaration 5; silently
   treating an ineligible declared boundary as warm would violate the contract.

## Verdict and limits

Deterministic billing and semantic restoration cases pass independently.
These tests do not establish empirical realism, optimal threshold behavior,
range-level reads, or provider-specific cache behavior. No production source is
modified by this validation work.

## True CLI workflow validation

Executed successfully on 2026-10-06:

```powershell
uv run compaction-lab working-set --calls 8 --replicates 16 --thresholds 40000:100000:20000 --difference-step 5000 --policies eager_cold,first_use_warm,preserve_warm,strict_first_use --output .cache/review/ws-cli
```

Artifacts: `sweep.json`, `sweep.png`, `trajectory-costs.npz` under that directory.
Independent JSON checks recomputed full invoices from the four mean token
categories times the declared prices (relative tolerance 1e-12). All **27**
complete reports matched and completed exactly eight ordinary actions. The one
failed strict grid point at h=40,000 had failure share **0.5** and null full-task
expected cost. No failed partial bill was presented as a successful cost.

All four families selected **no_compaction**, null selected threshold, and zero
confirmed compactions. This verifies selection can prefer no reset rather than
forcing a finite-grid reset. After subtracting summary and command outputs,
every feasible discovery row had identical ordinary output mean **4,990.1875**
tokens. Discovery and confirmation action-field hashes differ, as required by
independent confirmation; per-family evaluations share the discovery field.

Verified all four cached corpus byte SHA-256 hashes against the calibration
manifest. Their source URLs separately identify repository, pinned commit and
path. The report separates `environment.source_sha256` (implementation code),
`evidence.artifacts` (measured full-file tokenizer proxies), `evidence.trace`
(public output marginal and block pool), and `demand_controls` (synthetic
prerequisite/access interventions). The manifest explicitly labels this as
proxy-size/output calibration rather than real task replay.

Two maintained inference regressions additionally require null strict failure
costs/secants, no-compaction tie selection, and equal ordinary-output work across
atomic and generated-command recovery families. No substantive CLI defect was
observed in this workflow.
