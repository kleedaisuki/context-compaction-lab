"""Profile pinned sanitized TraceLab usage without publishing individual traces.

Example:
    uv run python experiments/profile_public_trace.py
        --input .cache/community-data/syfi-v0.0.2.jsonl.gz

Download the v0.0.2 release separately. This script does not relabel token
drops as confirmed compactions or infer file identity from sanitized tool names.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

EXPECTED_SHA256 = "11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65"
"""Publisher digest for the immutable v0.0.2 sanitized JSONL asset."""

SOURCE_URL = (
    "https://github.com/uw-syfi/TraceLab/releases/download/v0.0.2/"
    "syfi_coding_trace.jsonl.gz"
)
"""Public source, CC BY 4.0; attribution: UW SyFI TraceLab authors."""


def moments(values: list[int]) -> dict[str, float | int]:
    """Return descriptive moments; zero counts are valid, not silently censored."""
    if not values:
        return {"n": 0}
    x = np.asarray(values, dtype=np.float64)
    return {
        "n": len(x), "mean": float(x.mean()),
        "sd": float(x.std(ddof=1)) if len(x) > 1 else 0.0,
        **{f"p{q}": float(np.percentile(x, q)) for q in (10, 50, 90, 99)},
    }


def profile(path: Path) -> dict[str, object]:
    """Check row accounting and summarize ordered within-session token transitions."""
    with path.open("rb") as source_file:
        digest = hashlib.file_digest(source_file, "sha256").hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Expected the pinned TraceLab v0.0.2 source digest.")
    groups = defaultdict(list)
    counts, problems, keys = Counter(), Counter(), Counter()
    measures = defaultdict(lambda: defaultdict(list))
    users = set()
    session_ids = set()
    with gzip.open(path, "rt", encoding="utf-8") as source:
        for ordinal, line in enumerate(source):
            row = json.loads(line)
            provider = row["provider"]
            counts[provider] += 1
            users.add(row.get("user"))
            session_ids.add(row["session_id"])
            total, prefix, appended = (
                row[key] for key in ("input_tokens_total", "prefix_tokens", "newly_append_tokens")
            )
            problems["input_partition_mismatch"] += total != prefix + appended
            problems["negative_input_counts"] += min(total, prefix, appended) < 0
            if provider == "claude":
                actual = sum(row[key] for key in (
                    "claude_uncached_input_tokens", "claude_cache_creation_input_tokens",
                    "claude_cache_read_input_tokens",
                ))
                problems["claude_partition_mismatch"] += actual != total
            session = (provider, row.get("project"), row["session_id"], row.get("session_file"))
            keys[session + (row["round_index"],)] += 1
            groups[session].append((row["round_index"], ordinal, total, prefix))
            for name, value in (
                ("input", total), ("cached", prefix), ("append", appended),
                ("output", row["output_tokens"]),
            ):
                measures[provider][name].append(value)
    for session, rows in groups.items():
        rows.sort(key=lambda item: (item[0], item[1]))
        provider = session[0]
        measures[provider]["calls_per_session"].append(len(rows))
        for previous, current in zip(rows, rows[1:]):
            delta = current[2] - previous[2]
            if delta > 0:
                measures[provider]["positive_adjacent_input_delta"].append(delta)
            if delta <= -64_000:
                measures[provider]["drop64k_pre_input"].append(previous[2])
                measures[provider]["drop64k_post_input"].append(current[2])
                measures[provider]["drop64k_post_cached"].append(current[3])
    return {
        "source": {"url": SOURCE_URL, "sha256": digest, "license": "CC BY 4.0"},
        "rows": sum(counts.values()), "provider_counts": dict(counts),
        "session_groups": len(groups), "pseudonymous_users": len(users),
        "distinct_session_ids": len(session_ids),
        "session_key": "provider_project_session_id_optional_session_file",
        "quality": {
            **dict(problems),
            "duplicate_session_round_rows_beyond_first": sum(n - 1 for n in keys.values()),
            "duplicate_policy": "preserve_published_rows; order_by_round_index_then_ingestion",
        },
        "metrics": {
            provider: {name: moments(values) for name, values in bucket.items()}
            for provider, bucket in measures.items()
        },
        "interpretation": {
            "drop_detector": "adjacent_full_input_drop_at_least_64000_tokens_only",
            "drop_status": "candidates_not_confirmed_compactions_no_future_rebound_filter",
            "delta_status": "positive_observed_input_delta_not_iid_nonfile_growth",
            "missing_identification": (
                "file_paths_versions_contents_and_explicit_compaction_markers"
            ),
            "use": "descriptive_community_scale_and_model_inputs_not_policy_counterfactuals",
        },
    }


def main() -> None:
    """Write aggregate-only output under the workspace cache by default."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=Path(".cache/community-data/tracelab-profile.json"),
    )
    args = parser.parse_args()
    report = profile(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
