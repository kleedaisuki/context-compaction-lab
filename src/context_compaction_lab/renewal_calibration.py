"""Calibrate aggregate context growth without treating cache append as growth.

Full input differences already contain intervening model output and tool input.
Consequently output is never added to the growth proxy. Contiguous accepted runs
preserve observed serial dependence; they are not inferred compaction cycles.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

TRACE_SHA256 = "11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65"
SOURCE_URL = "https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2"


def moments(values: np.ndarray) -> dict[str, float | int]:
    """Describe the empirical distribution, including zeros and raw tail moments."""
    x = np.asarray(values, dtype=np.float64)
    if not len(x):
        return {"n": 0}
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if len(x) > 1 else 0.0
    return {
        "n": len(x),
        "mean": mean,
        "sd": sd,
        "cv": sd / mean if mean else 0.0,
        "zero_share": float(np.mean(x == 0)),
        "second_raw_moment": float(np.mean(x**2)),
        "third_raw_moment": float(np.mean(x**3)),
        **{f"p{q}": float(np.percentile(x, q)) for q in (10, 50, 90, 95, 99, 99.9)},
        "max": float(x.max()),
    }


def dependence(runs: list[np.ndarray], block_length: int) -> dict[str, object]:
    """Measure pairs and disjoint block sums only within uninterrupted runs.

    Block-versus-IID variance uses the marginal of the exact same block cohort;
    pooled correlation can include session heterogeneity rather than causality.
    """
    result: dict[str, object] = {}
    for lag in (1, 5):
        eligible = [x for x in runs if len(x) > lag]
        left = np.concatenate([x[:-lag] for x in eligible])
        right = np.concatenate([x[lag:] for x in eligible])
        result[f"lag{lag}"] = {
            "pairs": len(left),
            "pooled_correlation": float(np.corrcoef(left, right)[0, 1]),
        }
        long_runs = [x for x in eligible if len(x) >= block_length]
        centered_left = np.concatenate([x[:-lag] - x.mean() for x in long_runs])
        centered_right = np.concatenate([x[lag:] - x.mean() for x in long_runs])
        result[f"lag{lag}"]["long_run_centered_pairs"] = len(centered_left)
        result[f"lag{lag}"]["long_run_centered_correlation"] = float(
            np.corrcoef(centered_left, centered_right)[0, 1],
        )
    blocks = np.concatenate(
        [
            x[: len(x) // block_length * block_length].reshape(-1, block_length)
            for x in runs
            if len(x) >= block_length
        ]
    )
    variance = float(blocks.ravel().var(ddof=1))
    result["disjoint_block_comparison"] = {
        "block_length": block_length,
        "blocks": len(blocks),
        "marginal": moments(blocks.ravel()),
        "sum_variance": float(blocks.sum(axis=1).var(ddof=1)),
        "iid_sum_variance": block_length * variance,
        "variance_ratio": float(blocks.sum(axis=1).var(ddof=1) / (block_length * variance)),
    }
    return result


def calibrate_trace(
    source: Path,
    output: Path,
    *,
    block_length: int = 16,
    drop_tokens: int = 64_000,
    recovery_calls: int = 3,
) -> dict[str, object]:
    """Write aggregate metadata and IID/run pools for a fixed public trace cohort.

    A transition is accepted iff ordered round indices are consecutive, input
    change is nonnegative, and it is not among the next ``recovery_calls`` after
    a large negative change. Negative changes break runs rather than being
    replaced with zero. Neither a drop nor its end state proves compaction.
    """
    if block_length < 2 or drop_tokens < 1 or recovery_calls < 0:
        raise ValueError("Invalid cohort controls.")
    with source.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    if digest != TRACE_SHA256:
        raise ValueError("Source differs from pinned TraceLab v0.0.2.")
    groups = defaultdict(list)
    counts = Counter()
    outputs, read_shares, creation_shares = [], [], []
    with gzip.open(source, "rt", encoding="utf-8") as handle:
        for ordinal, line in enumerate(handle):
            row = json.loads(line)
            counts["all_rows"] += 1
            if row["provider"] != "claude":
                continue
            counts["claude_rows"] += 1
            key = (row["provider"], row.get("project"), row["session_id"], row.get("session_file"))
            total = row["input_tokens_total"]
            read = row["claude_cache_read_input_tokens"]
            create = row["claude_cache_creation_input_tokens"]
            groups[key].append((row["round_index"], ordinal, total, row["output_tokens"]))
            outputs.append(row["output_tokens"])
            if total:
                read_shares.append(read / total)
                creation_shares.append(create / total)
            counts["read_tokens"] += read
            counts["creation_tokens"] += create
            counts["input_tokens"] += total
    runs, output_runs, session_means, postdrops = [], [], [], []
    growth_output_pairs = []
    for rows in groups.values():
        rows.sort(key=lambda row: (row[0], row[1]))
        output_runs.append(np.asarray([row[3] for row in rows], dtype=np.int64))
        run, session_growth = [], []
        last_drop = -recovery_calls - 2
        for i in range(1, len(rows)):
            previous, current = rows[i - 1], rows[i]
            delta = current[2] - previous[2]
            counts["transitions"] += 1
            if delta <= -drop_tokens:
                last_drop = i
                postdrops.append(current[2])
                counts["large_drop_candidates"] += 1
            if current[0] != previous[0] + 1:
                counts["excluded_nonconsecutive_round"] += 1
                accepted = False
            elif delta < 0:
                counts["excluded_negative_change"] += 1
                accepted = False
            elif i - last_drop <= recovery_calls:
                counts["excluded_recovery_window"] += 1
                accepted = False
            else:
                accepted = True
            if accepted:
                run.append(delta)
                session_growth.append(delta)
                growth_output_pairs.append((delta, previous[3]))
            elif run:
                runs.append(np.asarray(run, dtype=np.int64))
                run = []
        if run:
            runs.append(np.asarray(run, dtype=np.int64))
        if len(session_growth) >= block_length:
            session_means.append(float(np.mean(session_growth)))
    growth = np.concatenate(runs)
    pairs = np.asarray(growth_output_pairs, dtype=np.int64)
    if not np.array_equal(growth, pairs[:, 0]):
        raise RuntimeError("Growth/output marks lost chronological run alignment.")
    output.mkdir(parents=True, exist_ok=True)
    pools = {}
    for name, selected_runs in (("growth", runs), ("output", output_runs)):
        values = np.concatenate(selected_runs)
        offsets = np.cumsum([0] + [len(x) for x in selected_runs])
        starts = np.concatenate(
            [
                np.arange(offsets[i], offsets[i + 1] - block_length + 1, dtype=np.int64)
                for i, x in enumerate(selected_runs)
                if len(x) >= block_length
            ]
        )
        filename = f"{name}-pool.npz"
        # Match the block-weighted one-step marginal for an apples-to-apples IID
        # comparison; run edges appear in fewer uniformly sampled moving blocks.
        weight_changes = np.zeros(len(values) + 1, dtype=np.int64)
        np.add.at(weight_changes, starts, 1)
        np.add.at(weight_changes, starts + block_length, -1)
        marginal_weights = np.cumsum(weight_changes[:-1])
        arrays = {
            "values": values,
            "block_starts": starts,
            "run_offsets": offsets,
            "block_length": block_length,
            "block_marginal_weights": marginal_weights,
        }
        if name == "growth":
            arrays["previous_output_tokens"] = pairs[:, 1]
        np.savez_compressed(output / filename, **arrays)
        pools[name] = {
            "filename": filename,
            "values": len(values),
            "moving_block_starts": len(starts),
            "runs": len(selected_runs),
            "block_weighted_marginal_mean": float(
                np.average(values, weights=marginal_weights),
            ),
        }
        if name == "growth":
            pools[name]["previous_output_mean"] = float(pairs[:, 1].mean())
            pools[name]["block_weighted_previous_output_mean"] = float(
                np.average(pairs[:, 1], weights=marginal_weights),
            )
            pools[name]["previous_output_exceeds_growth_share"] = float(
                np.mean(pairs[:, 1] > values),
            )
            pools[name]["block_weighted_previous_output_exceeds_growth_share"] = float(
                np.average(pairs[:, 1] > values, weights=marginal_weights),
            )
    report = {
        "source": {
            "url": SOURCE_URL,
            "sha256": digest,
            "license": "CC BY 4.0",
            "attribution": "UW SyFI TraceLab authors",
        },
        "cohort": {
            "provider": "claude",
            "order": "round_index_then_ingestion",
            "group": "provider_project_session_id_session_file",
            "nonnegative_consecutive_input_change": True,
            "large_drop_tokens": drop_tokens,
            "recovery_calls_excluded": recovery_calls,
            "session_groups": len(groups),
            "counts": dict(counts),
        },
        "growth": moments(growth),
        "growth_dependence": dependence(runs, block_length),
        "growth_tail_moment_shares": {
            f"top1pct_moment{power}_share": float(
                np.sum(growth[growth >= np.percentile(growth, 99)].astype(float) ** power)
                / np.sum(growth.astype(float) ** power),
            )
            for power in (1, 2, 3)
        },
        "output": moments(np.asarray(outputs)),
        "output_dependence": dependence(output_runs, block_length),
        "session_growth_mean_distribution_min16": moments(np.asarray(session_means)),
        "growth_previous_output_correlation": float(np.corrcoef(pairs.T)[0, 1]),
        "large_drop_post_input": moments(np.asarray(postdrops)),
        "cache_proxies": {
            "call_read_share": moments(np.asarray(read_shares)),
            "call_creation_share": moments(np.asarray(creation_shares)),
            "token_weighted_read_share": counts["read_tokens"] / counts["input_tokens"],
            "token_weighted_creation_share": counts["creation_tokens"] / counts["input_tokens"],
            "identification": "Billed shares, NOT prefix survival probability or cache TTL.",
        },
        "pools": pools,
        "limitations": [
            "Observed full input growth is policy-conditioned and censored to monotone runs.",
            "Growth already includes prior output/tools; never add output a second time.",
            "Previous billed output is an aligned invoice mark, not retained output-tail size.",
            "No identification of file bytes, mandatory reloads, reset components, or causality.",
            "Large drops are candidates only; postdrop input is aggregate, not summary size.",
            "IID uses all accepted values; block cohort weighting differs at run boundaries.",
        ],
    }
    (output / "calibration.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return report
