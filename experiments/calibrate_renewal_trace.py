"""Build aggregate growth calibration and serial block pools inside the workspace.

Example: uv run python experiments/calibrate_renewal_trace.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from context_compaction_lab.renewal_calibration import calibrate_trace


def main() -> None:
    """Calibrate pinned public data without publishing raw rows or identifiers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=Path(".cache/community-data/syfi-v0.0.2.jsonl.gz")
    )
    parser.add_argument("--output", type=Path, default=Path(".cache/renewal-calibration"))
    parser.add_argument("--block-length", type=int, default=16)
    parser.add_argument("--recovery-calls", type=int, default=3)
    args = parser.parse_args()
    report = calibrate_trace(
        args.source, args.output, block_length=args.block_length, recovery_calls=args.recovery_calls
    )
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
