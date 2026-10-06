# Official price vectors for controlled invoice sensitivity

Verified 2026-10-06 against current first-party English pricing and caching
documentation. Scope: project quoted USD token prices onto the **same**
controlled ledger, not compare actual providers' invoices or model performance.
Companion machine-readable artifact: `price-scenarios.json`.

Starting internal contracts: `engineering-calibrated-experiments.md`,
`stochastic-model.md`, `../implementation-contract.md`, and `Pricing` in
`src/context_compaction_lab/config.py`. The configuration consumes USD **per
token**, whereas provider tables quote USD per million tokens. The four
categories are disjoint: uncached input without a write, cache creation,
cache reuse, and output. A write price is not added to base input for the same
token unless a distinct provider fee actually requires that accounting.

## 1. Usable official vectors

Order below is `(input, write, read, output)`, all USD per million tokens.
The initial six entries are Standard synchronous first-party global rates, excluding Batch,
Fast, residency uplifts, negotiated discounts, tools, taxes and subscriptions.

| JSON ID | Model / write TTL | Price vector | Input-normalized vector |
| --- | --- | --- | --- |
| `sonnet46_5m` | Claude Sonnet 4.6 / 5m | (3, 3.75, 0.30, 15) | (1, 1.25, 0.10, 5) |
| `sonnet55_5m` | Claude Sonnet 5.5 / 5m | (2, 2.50, 0.20, 10) | (1, 1.25, 0.10, 5) |
| `opus55_5m` | Claude Opus 5.5 / 5m | (4, 5, 0.20, 20) | (1, 1.25, 0.05, 5) |
| `fable51_5m` | Claude Fable 5.1 / 5m | (10, 12.50, 0.25, 50) | (1, 1.25, 0.025, 5) |
| `sonnet55_1h` | Claude Sonnet 5.5 / 1h | (2, 4, 0.20, 10) | (1, 2, 0.10, 5) |
| `gpt53codex_standard` | GPT-5.3-Codex / effective write | (1.75, 1.75, 0.175, 14) | (1, 1, 0.10, 8) |

The Anthropic rates and cache-read exceptions are explicit in its
[official pricing table](https://platform.claude.com/docs/en/about-claude/pricing).
The selected Claude models have standard token rates throughout their 1M
context window. Batch's input/output discount does not enter these vectors.
The older 4.6 and newer models do not have identical tokenizers; this study
holds token counts fixed intentionally rather than infer real text cost from
the scale-only comparison.

OpenAI's [official specialized-model pricing](https://developers.openai.com/api/docs/pricing)
quotes GPT-5.3-Codex Standard input 1.75, cached input 0.175, and output 14.
Its [official caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
says earlier models have no additional cache-write charge. Therefore write
tokens in our ledger are priced once at ordinary input, giving effective
`write=input`. **Do not generalize this to current OpenAI models:** GPT-5.6+
now has 1.25-times-input cache-write pricing. The guide also distinguishes
their 30m lifetime from earlier models' retention policies.

No requested model was replaced silently. The local `openai-docs` skill was
consulted; official documentation was searched and fetched. No credential,
paid API request or private account information was used.

The expanded catalog now contains 38 vectors, including region-specific Qwen
quotes and DeepSeek time bands. See the extension below. The original six
entries and IDs are retained; regional additions are not global-price claims.

## 2. What price-only interventions can establish

Let `m(h)=(E[I_h],E[W_h],E[R_h],E[O_h])` be expected category token totals
for a fixed horizon and controlled mechanism at threshold `h`. Then

\[
J_p(h)=p\cdot m(h),\qquad
J_{\alpha p}(h)=\alpha J_p(h)\quad(\alpha>0).
\]

Thus Sonnet 5.5 versus Sonnet 4.6, with **only** the vector substituted,
must produce the same minimizers, relative-cost plateaus and normalized slopes;
all dollar costs and dollar slopes scale by 2/3. This is an exact simulator
consistency check, not a prediction about real model runs.

The substantive sensitivity axes are relative prices:

- Opus/Fable reduce the weight of accumulated read history. Cheaper reads can
  reduce the reward for compacting warm history, while reset write and summary
  output costs remain material. The actual direction depends on the ledger;
  do not assert a universal monotonic optimum shift.
- One-hour Sonnet pricing increases the relative penalty for reconstruction
  writes. A price-only run should hold its existing cache law fixed to isolate
  this axis. A provider-coherent one-hour run must separately change TTL and
  recompute token categories; it answers a different question.
- GPT-5.3-Codex's lower relative write price and higher output/input ratio act
  on different categories. Their net effect requires the actual paired ledger.

Since `m(h)` does not depend on prices in a price-only intervention, sample
category totals once with common random numbers, then reprice many vectors.
Do not regenerate random streams for each price vector. For two thresholds,
the equal-cost price boundary is a hyperplane
`p dot (m(h1)-m(h2))=0`; heterogeneous vectors probe which side of those
boundaries the controlled workload occupies.

## 3. Cache semantics are metadata, not automatic overrides

Anthropic's [caching guide](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
requires exact cached-prefix matches and prior written lookup boundaries.
It supports 5m and 1h lifetime, refreshed on reuse; lookup checks at most 20
positions per breakpoint, with up to four explicit breakpoints. Minimum
cacheable prompt is 1,024 tokens for Sonnet 4.6 and 512 for selected 5.5/5.1
models. These details mean an unchanged semantic prefix need not produce a hit.

For earlier OpenAI models, in-memory entries typically survive 5–10 minutes
of inactivity, up to an hour; extended-retention support is model-specific.
Matching-machine routing and request configuration affect reuse and cache
minimums. Those are not a deterministic 300s TTL guarantee.

The JSON stores `provider_cache_metadata` separately from rates. For the main
price sensitivity keep the project's TTL, cache minimum, warm probability,
compaction preservation, restoration and timing controls unchanged. Even the
`sonnet55_1h` tariff must not silently set TTL to 3600 in that experiment.
When mechanisms change, label the experiment **joint price-and-cache-policy
sensitivity**, not a price-vector-only test.

Provider implementations can expose different cache boundaries and tokenizers,
reasoning output, task trajectories, compaction routes and tool payloads.
Neither the same price ratio nor the same model family establishes equal
`m(h)`, reset size, first-use reads or cache survival. This artifact supplies
prices for conditional projections only.

## 4. Hypothetical mechanism controls

The JSON has a separate `hypothetical_scenarios` array, not provider tariffs:

| ID | Vector | Purpose |
| --- | --- | --- |
| `equal_write_read` | (3, 0.30, 0.30, 15) | Remove premium for changing warm prefix into new cache input |
| `cheap_write` | (3, 0.75, 0.30, 15) | Reduce write/input ratio to 0.25 |
| `free_write` | (3, 0, 0.30, 15) | Boundary case to expose dependence on reset-write cost |

These isolate mechanism dependencies and can serve as stress tests. They are
not recommendations or claims that a provider offers those rates.

## 5. Gemini storage rent is outside this ledger

The [official Gemini API pricing table](https://ai.google.dev/gemini-api/docs/pricing)
lists Gemini 3.5 Flash paid Standard input 1.50, output 9, cached input 0.15
USD per million, plus explicit context-storage rent of 1 USD per million
tokens **per hour**. That rent cannot be represented by a fixed per-write
price independently of residence time and cache occupancy.

An appropriate extension needs a term such as

\[
C_{\mathrm{storage}}=p_s\int K(t)\,dt
\]

with consistent token-hour units. Do not force Gemini into the four-vector,
omit rent, and describe the result as a comparable provider invoice. The
JSON records this only in `excluded_provider_mechanisms`, not selectable
official four-vector scenarios.

## 6. JSON usage and verification

Use each scenario's `pricing_per_token` directly in the existing `Pricing`
contract, or divide `prices_per_million_usd` by 1,000,000. The JSON contains
the verification date, sources, input-normalized vectors, service qualifiers,
and excluded mechanisms. `schema_version=1` defines the file shape.

Validation performed: JSON parse; positive finite official rates; exact
per-million/per-token conversion; input normalization; Sonnet scale identity;
effective earlier-OpenAI write/input identity. No live provider execution was
performed. Reverify linked official pages before later reuse: prices are
time-sensitive and this artifact is a dated research input, not an evergreen
price resolver.

## 6. GPT / Qwen / DeepSeek catalog extension (2026-10-06)

The added vectors preserve the old identifiers and USD/token contract. They
are selected first-party quotes projected into the same controlled ledger,
not a new cross-provider tokenizer/performance experiment. Rates are USD per
million tokens in (input,write,read,output) order. Context/time bands are held
constant in a row. Applying a real band depends on EACH request, not H alone:
a crossing compactor can exceed a tariff boundary even when H is below it.
Therefore none of these constant-vector minima claims to optimize full tiered
provider billing. No actual cache lifetime or model capacity is imposed.

### GPT Standard vectors

The HTML pricing page hides some all-model rows in collapsed sections. Its
first-party Markdown version exposes the named **Standard pricing data** table;
we fetched that table, not adjacent Batch/Flex tables. New cache-write rates
are direct and disjoint; earlier models without an extra write fee use effective
write=input. GPT-5.6 Sol's currently quoted promotion is documented through at
least 2026-11-21, not a timeless list-price assumption.

Primary sources: [official pricing](https://developers.openai.com/api/docs/pricing),
[first-party Markdown](https://developers.openai.com/api/docs/pricing.md),
[cache rules](https://developers.openai.com/api/docs/guides/prompt-caching).
Short/long rows use the 272k input boundary. Single selected rows are not claims
that capacity or all other price bands disappear.

| ID | Model / tariff | Vector |
| --- | --- | --- |
| `gpt6astra_short` | gpt-6-astra / short | (10, 12.5, 1, 50) |
| `gpt6astra_long` | gpt-6-astra / long | (20, 25, 2, 75) |
| `gpt61sol_short` | gpt-6.1-sol / short | (2, 2.5, 0.1, 10) |
| `gpt61sol_long` | gpt-6.1-sol / long | (4, 5, 0.2, 15) |
| `gpt6luna_short` | gpt-6-luna / short | (0.1, 0.125, 0.01, 0.5) |
| `gpt6luna_long` | gpt-6-luna / long | (0.2, 0.25, 0.02, 0.75) |
| `gpt6sol_short` | gpt-6-sol / short | (2, 2.5, 0.2, 10) |
| `gpt56sol_short` | gpt-5.6-sol / short | (4, 5, 0.4, 20) |
| `gpt56sol_long` | gpt-5.6-sol / long | (8, 10, 0.8, 30) |
| `gpt56terra_short` | gpt-5.6-terra / short | (2, 2.5, 0.2, 12) |
| `gpt56luna_short` | gpt-5.6-luna / short | (0.2, 0.25, 0.02, 1.2) |
| `gpt54_short` | gpt-5.4 / short | (2.5, 2.5, 0.25, 15) |
| `gpt54_long` | gpt-5.4 / long | (5, 5, 0.5, 22.5) |
| `gpt54mini_short` | gpt-5.4-mini / short | (0.75, 0.75, 0.075, 4.5) |
| `gpt52_short` | gpt-5.2 / short | (1.75, 1.75, 0.175, 14) |
| `gpt41_short` | gpt-4.1 / short | (2, 2, 0.5, 8) |

### Qwen: specific model quotes, region and cache mode

Use mutually exclusive explicit and implicit modes. Creation in implicit mode
has no extra fee; effective write=input. Explicit mode quotes a separate
creation rate. q remains an independent controlled probability in BOTH modes:
no actual hit guarantee is inferred from the mode label.

The generic cache page cannot safely supply all newer discounts. For 3.8 Max,
read quotes differ from generic 10%/20% examples. For 3.8 Flash, even the explicit
creation/input ratios on the specific model pages differ from generic 1.25x
creation prose. We preserve the **specific published table** and flag that
source discrepancy in JSON. No actual billing run resolves it here; do not
present the selected quote as an independently reconciled provider invoice.

Sources: [3.8 Max](https://www.alibabacloud.com/help/en/model-studio/qwen3-8-max),
[3.8 Flash](https://www.alibabacloud.com/help/en/model-studio/qwen3-8-flash),
[3.7 Plus](https://www.alibabacloud.com/help/en/model-studio/qwen3-7-plus), and
[cache modes](https://www.alibabacloud.com/help/en/model-studio/context-cache).
For 3.7 Plus the two quoted tiers split at 256k input tokens.

| ID | Region / mode | Vector |
| --- | --- | --- |
| `qwen38max_beijing_explicit` | China (Beijing) / explicit | (1.65, 2.063, 0.137, 4.951) |
| `qwen38max_beijing_implicit` | China (Beijing) / implicit | (1.65, 1.65, 0.206, 4.951) |
| `qwen38max_singapore_explicit` | Singapore / International / explicit | (2, 2.5, 0.17, 6) |
| `qwen38max_singapore_implicit` | Singapore / International / implicit | (2, 2, 0.25, 6) |
| `qwen38flash_beijing_explicit` | China (Beijing) / explicit | (0.113, 0.177, 0.014, 0.382) |
| `qwen38flash_beijing_implicit` | China (Beijing) / implicit | (0.113, 0.113, 0.014, 0.382) |
| `qwen38flash_singapore_explicit` | Singapore / International / explicit | (0.15, 0.2, 0.016, 0.47) |
| `qwen38flash_singapore_implicit` | Singapore / International / implicit | (0.15, 0.15, 0.016, 0.47) |
| `qwen37plus_singapore_short_explicit` | Singapore / International / explicit | (0.4, 0.5, 0.04, 1.6) |
| `qwen37plus_singapore_short_implicit` | Singapore / International / implicit | (0.4, 0.4, 0.08, 1.6) |
| `qwen37plus_singapore_long_explicit` | Singapore / International / explicit | (1.2, 1.5, 0.12, 4.8) |
| `qwen37plus_singapore_long_implicit` | Singapore / International / implicit | (1.2, 1.2, 0.24, 4.8) |

Beijing's English USD table is not Singapore pricing and is not an inferred FX
conversion. The native [Chinese Max quote](https://help.aliyun.com/zh/model-studio/qwen3-8-max)
is separately recorded: explicit CNY (12,15,1,36); implicit CNY (12,12,1.5,36),
per million tokens. Native CNY is NOT silently treated as USD. Independently
rounded USD/CNY quote ratios need not yield exactly the same threshold.

### DeepSeek: first-party, peak versus off-peak

Source: [official prices](https://api-docs.deepseek.com/quick_start/pricing/) and
[cache mechanism](https://api-docs.deepseek.com/guides/kv_cache/).
The active API alias `deepseek-flash` identifies V4.1 Flash; the Pro quote is
V4-Pro-0813. Do not silently reuse old V3/R1 or Alibaba-hosted DeepSeek prices.
Effective write equals miss input, not zero and not an added second input fee.
Best-effort cache construction takes seconds; reported idle retention is hours
or days, not guaranteed lifetime or q=1.

| ID | Active model version / time | Vector |
| --- | --- | --- |
| `deepseek41flash_offpeak` | DeepSeek-V4.1-Flash / offpeak | (0.15, 0.15, 0.003, 0.6) |
| `deepseek41flash_peak` | DeepSeek-V4.1-Flash / peak | (0.3, 0.3, 0.006, 1.2) |
| `deepseek4pro_offpeak` | DeepSeek-V4-Pro-0813 / offpeak | (0.66, 0.66, 0.022, 1.98) |
| `deepseek4pro_peak` | DeepSeek-V4-Pro-0813 / peak | (1.32, 1.32, 0.044, 3.96) |

Peak is weekdays UTC 01:00-04:00 and 06:00-10:00, excluding Chinese public
holidays; mainland clock times are 09:00-12:00 and 14:00-18:00. All other
hours are off-peak. Every quoted peak component is exactly twice off-peak:
constant-band invoices double but optimal controls cannot change. Dynamic
clock-dependent trajectories are a different experiment.

### Reproduction and scope

`price-family-results.json` embeds the exact scenario metadata as well as the
source SHA and q conditions. Source-text capture hashes in the catalog identify
local primary-source fetches; full copyrighted pages remain in `.cache`.
The executable expanded study is documented in `price-family-study.md`.
Original 35-case artifacts remain unchanged as historical evidence. The next
step for genuine tiered/time-dependent invoices is category occupation by
request price band, not assigning one band from the scalar compact trigger.
