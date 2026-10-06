# Community and theory study: mandatory restoration after compaction

Started 2026-10-06. User-supplied premise: clearing tool calls/results makes
some files mandatory to re-input. Investigate the actual reconstruction
contracts instead of hiding these costs inside aggregate recovered input.

## Decision and deliverables

Select a useful model of expected four-price API invoice against a compaction
threshold, holding ordinary task actions fixed. Distinguish immediate required
restoration from later first-use mandatory reads, discretionary rediscovery,
stable prompt reinjection, and compulsory extra model/tool rounds. Do not turn
this into task-per-token optimization. Never count the same file payload both
inside a recovered aggregate and again as explicit restoration.

Existing knowledge: engineering-context-evidence.md,
engineering-calibrated-experiments.md, stochastic-model.md, and
implementation-contract.md. Current median-anchored aggregate is a control,
not evidence that every file is reread or that every cache boundary becomes cold.

## Blackboard ownership

| Track | Durable artifact | Responsibility |
| --- | --- | --- |
| Production mechanisms | community-compaction-mechanisms.md | Source-pinned harness behavior, read-before-edit contracts, stable prefixes |
| Community incidents/data | community-reload-observations.md | Primary reports and traces; measurable variables; representativeness |
| Academic frontier | compaction-memory-literature.md | Recent compression/memory studies and classical working-set connections |
| Stochastic theory | mandatory-reload-theory.md | File first-use/working-set model, exact expectation/derivative cases |
| Decision alternatives | compaction-model-selection.md | Compare mathematical tools and produce a tractable discriminating test |
| Integration | mandatory-reload-synthesis.md | Mechanism synthesis, recommended next model, actionable experiment |

Each owner reads only relevant internal notes, searches English primary
sources, persists findings in English, separates configured/measured/inferred
quantities, and reports decision-relevant findings promptly. No private trace
publication or project artifacts outside the repository. No production edits
by research tracks unless explicitly delegated by the integrator.

## Acceptance

1. At least several concrete production/community mechanisms, not one vendor
   article recycled into a universal model.
2. Mandatory status follows a cited contract or explicit task assumption, not
   the assertion that deleting a tool result forces every old file to be read.
3. Several suitable mathematical tools compared by assumptions and decision
   value, including a model with delayed file restoration.
4. An inexpensive reproducible probe differentiates immediate constant reload
   from first-use restoration before committing to a large implementation.
5. Durable notes plus an integrated recommendation and changes to the research
   roadmap; existing published results retain their original accounting scope.
