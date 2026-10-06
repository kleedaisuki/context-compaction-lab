"""Measured artifact sizes and block-resampled public output-token distributions.

Only file-size proxies and output marginals are measured. Task prerequisites,
non-file inputs, timing, mutations and stable-cache boundaries remain explicit
controlled interventions. Fresh append is never reused as non-file growth.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import tiktoken

from .working_set_config import ArtifactSpec

TRACE_SHA256 = "11ce51ec0a25e3d1d95b025bca2f7d1647e47571eb7cc968acd5fc64d4b4fb65"
"""Digest of the pinned sanitized TraceLab v0.0.2 compressed release."""

CORPUS = (
    (
        "jinja_filters",
        "pallets/jinja",
        "15206881c006c79667fe5154fe80c01c65410679",
        "src/jinja2/filters.py",
    ),
    ("rich_text", "Textualize/rich", "72e3bb33d44fd96881f7742b77137983907a942f", "rich/text.py"),
    (
        "asyncio_base_events",
        "python/cpython",
        "ebf955df7a89ed0c7968f79faec1de49f61ed7cb",
        "Lib/asyncio/base_events.py",
    ),
    (
        "django_query",
        "django/django",
        "9e7cc2b628fe8fd3895986af9b7fc9525034c1b0",
        "django/db/models/query.py",
    ),
)
"""Pinned real source-file corpus; only manifests, not source bodies, are published."""


def summarize_values(values: np.ndarray) -> dict[str, float | int]:
    """Describe a measured marginal without implying independent observations."""
    return {
        "count": len(values),
        "mean": float(values.mean()),
        "sd": float(values.std(ddof=1)),
        "zero_share": float(np.mean(values == 0)),
        **{f"p{q}": float(np.percentile(values, q)) for q in (10, 50, 90, 99)},
    }


def measure_corpus(destination: Path) -> list[dict[str, object]]:
    """Count full files with a declared tokenizer proxy, caching under destination.

    cl100k_base is a reproducible unit proxy, NOT an exact Claude tokenizer or
    an assertion that full-file recovery is always required by a real task.
    Model API calls and credentials are unnecessary.
    """
    destination.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TIKTOKEN_CACHE_DIR", str((destination / "tokenizer").resolve()))
    encoder = tiktoken.get_encoding("cl100k_base")
    manifest = []
    for name, repo, commit, relative in CORPUS:
        url = f"https://raw.githubusercontent.com/{repo}/{commit}/{relative}"
        path = destination / f"{name}.py"
        if not path.exists():
            with urlopen(url, timeout=60) as response:
                path.write_bytes(response.read())
        content = path.read_bytes()
        manifest.append(
            {
                "name": name,
                "repository": repo,
                "commit": commit,
                "path": relative,
                "source_url": url,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "tokens": len(encoder.encode(content.decode("utf-8"))),
                "encoding": "cl100k_base",
            }
        )
    return manifest


def extract_outputs(trace: Path, provider: str, block_length: int) -> tuple[np.ndarray, np.ndarray]:
    """Extract chronological output-only blocks, respecting session boundaries.

    Released rows are preserved. Session identity includes provider/project;
    ingestion order breaks equal round-index ties. Eligible block starts are
    pooled uniformly, a declared call-weighted moving-block bootstrap.
    """
    if provider not in {"claude", "codex"} or block_length < 1:
        raise ValueError("Require provider claude/codex and positive block length.")
    with trace.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if digest != TRACE_SHA256:
        raise ValueError("Expected the pinned sanitized TraceLab v0.0.2 asset.")
    groups = defaultdict(list)
    with gzip.open(trace, "rt", encoding="utf-8") as source:
        for ordinal, line in enumerate(source):
            row = json.loads(line)
            if row["provider"] == provider:
                key = (row.get("project"), row["session_id"], row.get("session_file"))
                groups[key].append((row["round_index"], ordinal, row["output_tokens"]))
    sequences, starts, offset = [], [], 0
    for rows in groups.values():
        rows.sort(key=lambda item: (item[0], item[1]))
        values = np.array([item[2] for item in rows], dtype=np.int64)
        if np.any(values < 0):
            raise ValueError("Negative observed output counts must not be silently dropped.")
        sequences.append(values)
        starts.extend(range(offset, offset + max(0, len(values) - block_length + 1)))
        offset += len(values)
    if not starts:
        raise ValueError("No sessions support the requested output block length.")
    return np.concatenate(sequences), np.asarray(starts, dtype=np.int64)


def prepare_data(
    trace: Path, destination: Path, provider: str = "claude", block_length: int = 16
) -> dict[str, object]:
    """Materialize local-only resampling pools and a portable provenance manifest."""
    destination.mkdir(parents=True, exist_ok=True)
    artifacts = measure_corpus(destination / "corpus")
    outputs, starts = extract_outputs(trace, provider, block_length)
    np.savez_compressed(destination / "output-pool.npz", outputs=outputs, starts=starts)
    manifest = {
        "artifacts": artifacts,
        "trace": {
            "url": "https://github.com/uw-syfi/TraceLab/releases/tag/v0.0.2",
            "sha256": TRACE_SHA256,
            "license": "CC BY 4.0",
            "attribution": "UW SyFI TraceLab authors",
            "provider": provider,
            "block_length": block_length,
            "eligible_block_starts": len(starts),
            "all_output_rows": summarize_values(outputs),
        },
        "scope": "measured_whole_file_size_proxy_and_output_marginal_not_real_task_replay",
        "unmeasured": [
            "required_file_accesses",
            "nonfile_input",
            "mutations",
            "ordinary_gaps",
            "stable_prefix",
            "summary_distribution",
        ],
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_data(destination: Path) -> tuple[tuple[ArtifactSpec, ...], dict, np.ndarray, np.ndarray]:
    """Read a prepared pool without silently downloading or creating measurements."""
    manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    artifacts = tuple(ArtifactSpec(row["name"], row["tokens"]) for row in manifest["artifacts"])
    with np.load(destination / "output-pool.npz", allow_pickle=False) as source:
        outputs, starts = source["outputs"].copy(), source["starts"].copy()
    return artifacts, manifest, outputs, starts
