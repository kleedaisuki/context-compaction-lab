# GPT, Qwen and DeepSeek: expanded quoted-vector experiments

Executed 2026-10-06. Extension of the
[price sensitivity study](price-sensitivity-study.md), not a replacement of its
theory or immutable 35-case results. The official catalog grows from 6 to **38**
vectors: 17 GPT/OpenAI, 12 Qwen, 4 DeepSeek and the original 5 Claude vectors.
GPT entries cover 12 distinct models; Qwen includes three models, selected
regional/tier quotes and mutually exclusive explicit/implicit modes.

**Every result below is a constant quoted-price projection on the same token
workload. It is NOT an actual-provider optimum, a tokenizer comparison, a
capacity-feasibility claim, or an estimate of cache reliability.** Short/long
and peak/off-peak labels identify selected quotes; request-level band switching
is not implemented. q is held equal when comparing price modes.

## 1. Theory predicts useful groups, not just a longer price list

The existing conditional control theory has

\[
c=(1-q)p_w+qp_r,\qquad
A=p_i[K+(1-q)S]+qp_w(S-B)+qp_rB+p_oC.
\]

The core gap solves D(L*)=A/c. Its price response depends on setup versus
carry shares, not on an isolated absolute price. Full marked rates retain the
cold crossing tail. With the same growth/reset/cache law:

1. Proportional vectors have identical optimal controllers at EVERY q, while
   costs scale. GPT-6 Astra, GPT-6 Sol, GPT-5.6 Sol and GPT-6 Luna short tariffs
   have the same normalized (1,1.25,.10,5) vector as the original Sonnet lane.
2. GPT-6.1 Sol lowers the relative read price to .05 while retaining the
   1.25 write multiplier. It shares the Opus 5.5 price-ratio class, not the
   ordinary .10-read GPT class.
3. GPT-5.4 and earlier selected rows without a separate write charge use
   effective write=input. GPT-5.2 and GPT-5.3-Codex are the same price vector
   here, though their actual behavior need not be the same.
4. GPT long bands multiply input/read/write by two but output by 1.5. They
   are NOT uniform scaling of the short vector: the relative summary-output
   cost falls, so their isolated projection can prefer an earlier compact.
5. DeepSeek peak vectors are exactly twice off-peak. The time-band price
   difference alone cannot move an optimal constant-band threshold.
6. Qwen 3.7 Plus Singapore long quotes are exactly three times short quotes
   for each cache mode. These isolated vectors must choose the same H.

These are hypotheses/identities derived before confirmation. See the
[full sign and regret derivation](price-sensitivity-theory.md).

## 2. Quote provenance and important exceptions

The [catalog](price-scenarios.json) contains USD-per-million and USD-per-token
values, context/time bands, region, cache mode, source URLs, and native Beijing
Qwen Max CNY quotes separately. Unit conversion is checked. No exchange rate is
invented and CNY is never silently used as USD.

- OpenAI: [official pricing](https://developers.openai.com/api/docs/pricing),
  its first-party [Markdown table](https://developers.openai.com/api/docs/pricing.md),
  and [cache rules](https://developers.openai.com/api/docs/guides/prompt-caching).
  Standard all-model rows are collapsed in the HTML view; the fetched Markdown
  exposes them separately from Batch/Flex. GPT-5.6 Sol uses its currently quoted
  promotional rate, not a claim about permanent prices.
- Qwen: model-specific
  [3.8 Max](https://www.alibabacloud.com/help/en/model-studio/qwen3-8-max),
  [3.8 Flash](https://www.alibabacloud.com/help/en/model-studio/qwen3-8-flash),
  [3.7 Plus](https://www.alibabacloud.com/help/en/model-studio/qwen3-7-plus)
  tables and [cache modes](https://www.alibabacloud.com/help/en/model-studio/context-cache).
  Explicit and implicit modes have different write/read vectors. Specific 3.8
  Flash creation quotes conflict with generic 1.25x creation prose: the JSON
  explicitly flags the discrepancy. This study uses the specific table; no
  actual invoice reconciles the two sources. Newer read prices must not be
  inferred from generic 10%/20% examples.
- DeepSeek: current first-party
  [model/pricing table](https://api-docs.deepseek.com/quick_start/pricing/)
  and [cache mechanism](https://api-docs.deepseek.com/guides/kv_cache/).
  `deepseek-flash` is V4.1 Flash; Pro is V4-Pro-0813. Miss input is the
  effective write price, not zero and not an extra duplicate fee.
  Peak is weekdays UTC 01:00-04:00 and 06:00-10:00 excluding Chinese public
  holidays. The whole trajectory holds one quoted band; clock switching is not
  inferred. Automatic best-effort caching does not guarantee q=1.

## 3. Executed design

The immutable TraceLab v0.0.2 public pool and previous reset anchors are reused:
S=65,588; B=20,000; C=4,382; K=I=128; theta=1. Matched marginal growth mean
is 1,532.8794; aligned ordinary billed output mean is 848.0400 tokens. Neither
is silently changed to match a different model's generation or tokenization.

All 38 vectors are evaluated at q=.8,.95,1, plus the retained 29 local/sign/
material/timing/growth controls: **143 analytical scenarios**. Each has a full
marked empirical-renewal minimum and an unbounded-right-tail certificate for
the finite binned law. The canonical core derivatives remain separately labeled.

Confirmation uses 512 trajectories x 4,000 ordinary calls under both iid and
random-phase intact 16-action blocks. Seeds remain 2026102601/2026102602 to pair
the new price comparisons and preserve old controls; these are not new observed
community runs. One immutable four-category trajectory ledger is simulated per
mechanism and repriced for all vectors. q=.8/.95 price comparisons use the
unchanged-price optimum of that SAME cache mechanism as their reference.
No paid model requests are made. Intervals are conditional Monte Carlo, not
source-selection, actual-provider or cross-model uncertainty.

## 4. Representative results

H is the full marked long-run optimum in thousand tokens, not a production
recommendation. Short or long means the SELECTED fixed-rate projection.

| Projection | (input,write,read,output), USD/M | H at q=.8 | H at q=.95 | H at q=1 |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra short | (10,12.5,1,50) | 91.003 | 102.938 | 112.848 |
| GPT-6.1 Sol short | (2,2.5,.1,10) | 92.663 | 110.393 | 132.838 |
| GPT-6.1 Sol long | (4,5,.2,15) | 91.678 | 108.748 | 130.383 |
| GPT-6 Luna short | (.1,.125,.01,.5) | 91.003 | 102.938 | 112.848 |
| GPT-6 Sol short | (2,2.5,.2,10) | 91.003 | 102.938 | 112.848 |
| GPT-5.6 Sol short | (4,5,.4,20) | 91.003 | 102.938 | 112.848 |
| GPT-5.6 Terra short | (2,2.5,.2,12) | 91.723 | 103.998 | 114.183 |
| GPT-5.6 Luna short | (.2,.25,.02,1.2) | 91.723 | 103.998 | 114.183 |
| GPT-5.4 short | (2.5,2.5,.25,15) | 92.618 | 103.198 | 110.993 |
| GPT-5.4 mini | (.75,.75,.075,4.5) | 92.618 | 103.198 | 110.993 |
| GPT-5.2 | (1.75,1.75,.175,14) | 94.208 | 105.448 | 113.728 |
| GPT-4.1 | (2,2,.5,8) | 86.893 | 90.613 | 92.403 |
| Qwen 3.8 Max Beijing explicit | (1.65,2.063,.137,4.951) | 89.993 | 102.703 | 114.483 |
| Qwen 3.8 Max Beijing implicit | (1.65,1.65,.206,4.951) | 89.253 | 97.078 | 102.223 |
| Qwen 3.8 Max Singapore explicit | (2,2.5,.17,6) | 89.918 | 102.458 | 113.898 |
| Qwen 3.8 Max Singapore implicit | (2,2,.25,6) | 89.248 | 97.063 | 102.198 |
| Qwen 3.8 Flash Singapore explicit | (.15,.2,.016,.47) | 89.263 | 100.538 | 109.888 |
| Qwen 3.8 Flash Singapore implicit | (.15,.15,.016,.47) | 89.953 | 98.998 | 105.458 |
| Qwen 3.7 Plus Singapore short explicit | (.4,.5,.04,1.6) | 90.248 | 101.853 | 111.478 |
| Qwen 3.7 Plus Singapore short implicit | (.4,.4,.08,1.6) | 88.008 | 92.948 | 95.553 |
| DeepSeek V4.1 Flash off-peak | (.15,.15,.003,.6) | 94.423 | 116.923 | 162.003 |
| DeepSeek V4 Pro off-peak | (.66,.66,.022,1.98) | 92.753 | 111.018 | 137.273 |

All 38 projections, complete usage gradients and confirmation results are in
[price-family-results.json](price-family-results.json). DeepSeek's very cheap
read price matters greatly near q=1 but does not mean 162k is suitable at
imperfect hits: at q=.8 the same Flash vector selects 94.4k. GPT-4.1's read/input
ratio .25 favors substantially shorter retained history than .05/.10 classes.

### Economic importance, not just argmin shifts

At q=1, keeping the original 112,848 policy rather than retuning has block
confirmation savings available of 1.566% for GPT-6.1 Sol short, 3.591% for
GPT-4.1, 5.585% for DeepSeek Flash, 2.262% for DeepSeek Pro, and 2.428% for
Qwen 3.7 Plus implicit. Many smaller GPT shifts have tiny or unresolved
retuning gains; a changed number alone does not justify operational retuning.

### Qwen cache modes: cheaper reads versus dearer writes

Both modes have the SAME declared q, workload and independent cache uniforms.
They are repriced and separately retuned; these compare TOTAL expenses, not
each mode's isolated retuning gain.

| Qwen 3.8 Max Singapore condition | Analytic explicit expense versus implicit | Block explicit-minus-implicit USD/action | Paired MC95 halfwidth |
| --- | ---: | ---: | ---: |
| q=.8 | +6.865% | +.0042707084 | .0000284263 |
| q=.95 | -6.514% | -.0026877552 | .0000202521 |
| q=1 | -15.973% | -.0054464281 | .0000084903 |

Explicit Max prices lower read usage expense (.17 vs .25) but raise writes
(2.5 vs 2). Their benefit depends on repeated reliable reuse versus expensive
miss/reconstruction writes. This is a conditional price mechanism, not an
observed claim that a real explicit cache has the same q as an implicit one.

Flash's specific Singapore quote has the SAME read/input/output prices in
both modes, but explicit writes cost .2 versus implicit .15. Thus its explicit
vector is componentwise dominated at fixed q: price monotonicity proves it
cannot reduce the optimized bill for ANY shared feasible policy set. At the
three tested q values the explicit projection costs 20.53%, 12.39%, and 6.30%
more respectively. If the real explicit mode improves q, that is a different
joint mechanism which can offset the price disadvantage. The conflicting
generic creation-rate prose remains a source limitation, not a resolved bill.

## 5. Extending beyond constant-vector projections

With request-level input-price bands b, the exact accounting is

\[
J(H)=\sum_b p_b^T m_b(H),\quad
m_b(H)=E\left[\sum_t 1\{\text{request }t\text{ uses band }b\}\,m_t\right].
\]

The concatenated band-price vector still has a price-linear fixed-policy
invoice, concave optimized envelope and usage ordering. But a single constant
c,A renewal root no longer automatically solves it. Band occupation must
include compactor input and crossing overshoot, not merely ordinary calls or
the chosen H. For clock-dependent prices it must also include timing/phase.
The next extension is this request-band ledger, not pretending that a long-rate
projection at H<272k is actual long-band execution. No such implementation or
provider-optimality claim is made in this catalog expansion.

## 6. Reproduction and audit

Prepare the pinned public pool using the existing calibration instructions:

```powershell
uv sync --locked
$env:OPENBLAS_NUM_THREADS='1'
uv run python experiments/run_price_sensitivity.py --replicates 512 --calls 4000 --cache-conditions 0.8 0.95 1 --result-name price-family-results
uv run python experiments/price_family_crosscheck.py
uv run python experiments/price_sensitivity_derivation.py
uv run python experiments/price_sensitivity_crosscheck.py
```

The final expanded study took 18.72 seconds. The artifact audit checks all
38 quote/unit mappings, the 143 cases, same-q reference controls, metadata
embedded in the executed result, and exact preservation of the previous
35 analytical cases. Twenty-seven proportional-price comparisons pass with
identical H and proportionally scaled analytical and iid/block mean invoices.
It also checks the dominated Flash vectors. The existing independent physical
DP/SymPy checks remain the underlying ledger/theory verification, not replaced
by comparing one implementation to itself. Raw pools, plots and logs remain
under `.cache`; no private traces, credentials or new CI are introduced.
