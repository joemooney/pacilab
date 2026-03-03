#!/usr/bin/env python3
"""Run high-volume scenario regression."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pacilab.engine import simulate_packet
from pacilab.scenario_lib import validate_scenario_obj


def main() -> None:
    parser = argparse.ArgumentParser(description="Run packet regression")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--mode", choices=["mock", "real"], default="mock")
    parser.add_argument("--pacgate-bin", default="pacgate")
    parser.add_argument("--output")
    args = parser.parse_args()

    raw = json.loads(Path(args.scenario).read_text(encoding="utf-8"))
    scenario = validate_scenario_obj(raw)
    rules = scenario.get("default_rules_file", "rules/examples/allow_arp.yaml")
    stateful = bool(scenario.get("stateful", False))

    events = scenario["events"]
    mismatches = 0
    results = []

    start = time.perf_counter()
    for i in range(args.count):
        ev = events[i % len(events)]
        res = simulate_packet(ev["packet"], rules_file=rules, mode=args.mode, pacgate_bin=args.pacgate_bin, stateful=stateful)
        expected = ev.get("expected_action")
        action = res.get("action")
        ok = expected is None or expected == action
        if not ok:
            mismatches += 1
        results.append({
            "index": i,
            "event_name": ev.get("name", f"event_{i+1}"),
            "expected_action": expected,
            "actual_action": action,
            "ok": ok,
        })

    elapsed = time.perf_counter() - start
    out = {
        "scenario_id": scenario["id"],
        "count": args.count,
        "mode": args.mode,
        "mismatches": mismatches,
        "elapsed_sec": round(elapsed, 3),
        "packets_per_sec": round(args.count / elapsed, 2) if elapsed > 0 else None,
        "results": results[:50],
    }

    text = json.dumps(out, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")

    raise SystemExit(0 if mismatches == 0 else 1)


if __name__ == "__main__":
    main()
