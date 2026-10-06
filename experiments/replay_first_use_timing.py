"""Replay a controlled versioned-file restoration ledger, not a provider fit."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Ledger:
    """Mutually exclusive input categories plus all billed output tokens."""

    uncached: int
    writes: int
    reads: int
    output: int

    @property
    def dollars(self) -> float:
        """Price the synthetic invoice using declared USD per million rates."""
        return (3 * self.uncached + 3.75 * self.writes
                + .30 * self.reads + 15 * self.output) / 1_000_000


def replay(mode: str, stream: str, warm: bool) -> dict[str, object]:
    """Hold each stream fixed while varying only its restoration mechanism."""
    sizes = {"A": 2000, "B": 3000, "C": 5000, "D": 7000}
    demands = ({1: "A", 2: "B", 3: "C", 7: "A"} if stream == "early"
               else {1: "A", 6: "B", 7: "A", 8: "C"})
    resident: set[tuple[str, int]] = set()
    retained = 9000  # Stable prefix 8000 plus generated summary 1000.
    prefix = 8000 if warm else 0
    uncached, writes, reads, output = 5000, 0, 75000, 1000
    rereads: list[tuple[int, str, int]] = []
    landing = retained
    input_area = 0

    def restore(call: int, name: str, version: int) -> None:
        """Append payload and wrapper exactly once per required current version."""
        nonlocal retained
        resident.add((name, version))
        retained += sizes[name] + 64
        rereads.append((call, name, version))

    if mode == "immediate":
        for name in sizes:
            restore(0, name, 1)
        landing = retained

    for call in range(1, 9):
        if call in demands:
            name = demands[call]
            version = 2 if name == "A" and call >= 7 else 1
            if (name, version) not in resident:
                restore(call, name, version)
        cacheable = retained + 200
        reads += prefix
        writes += cacheable - prefix
        uncached += 128
        output += 100
        input_area += cacheable
        prefix = cacheable
        retained = cacheable + 100

    ledger = Ledger(uncached, writes, reads, output)
    return {"mode": mode, "stream": stream, "warm": warm,
            "landing_tokens": landing, "restores": rereads,
            "reload_payload_tokens": sum(sizes[name] for _, name, _ in rereads),
            "ordinary_cacheable_token_calls": input_area,
            "invoice_categories": ledger.__dict__, "usd": ledger.dollars}


if __name__ == "__main__":
    result = json.dumps([replay(mode, stream, warm)
                      for warm in [True, False]
                      for stream in ["early", "late"]
                      for mode in ["immediate", "first_use"]], indent=2)
    destination = Path(".cache/experiments/first-use-reload/timing-replay.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result + "\n", encoding="utf-8")
    print(result)
