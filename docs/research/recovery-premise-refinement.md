# Recovery premise refinement from practical workload feedback

Recorded on 2026-10-06. The user reports that retained state size and reloaded
document volume are highly concentrated around project-specific constants.
Treat this as a supplied workload premise for the next model, not as evidence
that every agent workload has the same recovery law.

## Mismatch in the initial synthetic reference

The published default used summary H-dependent tokens 2,000+H*U with
U~Beta(0.9,29.1), and independent Lognormal documents with mean 12,000 and CV
0.8. The document standard deviation is 9,600; q50, q90, and q99 are about
9,370, 23,079, and 48,124 tokens (see the executable calculation for exact
values). This is not a law concentrated tightly around a constant.

At H=40,000, summary mean is 3,200 and standard deviation approximately 1,226.
Recovered-state mean is 15,200 and standard deviation approximately 9,678.
The original near-optimal region and recovery-over-threshold counts must not
be carried over as estimates for a tightly concentrated recovery workload.

## Refined model direction

Use generated-summary size C=c0+epsilon_C and reloaded documents
D=d0+epsilon_D with small residual variation conditional on project/task phase.
Begin with constants C=c0 and D=d0, preserving random ordinary growth,
request-start gaps, threshold crossing, and cache expiry. Constant recovery
does not make the entire stopping-time and billing process deterministic.
Do not retain an H-proportional term without measured evidence for it.

If retained context includes verbatim preserved messages, distinguish that
quantity L from newly generated summary C. Only C is compactor output billed
at p_o; L can incur input/write/read charges without being generated again.
Version 0.1 lacked this split. Version 0.1.1 exposes preserved_tokens separately
and bills only generated-summary tokens as compactor output.

The conservative default still treats the branch-specific replacement as cold.
Version 0.1.1 also accepts an explicitly declared unchanged eligible boundary
inside preserved context; only its previously warm tokens survive. This does
not claim that copying identical documents automatically guarantees cache reuse.

## Price schedule actually used

The simulator constants are USD per million tokens: uncached input 3,
cache writes 3.75, cache reads 0.30, and output 15. They were borrowed as
illustrative Sonnet-like rates, not selected from the user's actual model or
subscription. Normal requests write eligible new prefix tokens; the compactor
reads eligible cached old input but does not select its obsolete suffix for
new cache writes. Both share one configured Pricing object. There are no
price tiers, separate compactor-model prices, or cache-storage rental.

## Reporting implication

The first correction made the illustrative baseline summary fixed 2,000,
documents fixed 12,000, and proportional fraction zero. These remain a named
synthetic control, not the CLI default after engineering evidence calibration.
See engineering-context-evidence.md: the CLI now uses a full recovered-state
anchor of 65,588, generated summary 4,382, and constructed aggregate residual
61,206, without pretending the documents-only split was measured.
Optional small absolute
noise leaves growth, gaps, crossing, and expiry stochastic. Prices remain
unchanged to isolate the recovery correction. Matched-at-40k controls use a
fixed 3,200-token summary rather than silently attributing changed mean size
to a change in dispersion. The already-published experiment remains historical.
