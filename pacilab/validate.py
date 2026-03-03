#!/usr/bin/env python3
"""Validate paciLab scenario files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pacilab.scenario_lib import ScenarioValidationError, validate_scenario_obj


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate scenario JSON files")
    parser.add_argument("files", nargs="+", help="Scenario files")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = []
    errors = []

    for name in args.files:
        p = Path(name)
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            norm = validate_scenario_obj(raw)
            results.append({"file": str(p), "id": norm["id"], "events": len(norm["events"]), "ok": True})
        except (OSError, json.JSONDecodeError, ScenarioValidationError, ValueError) as exc:
            errors.append({"file": str(p), "ok": False, "error": str(exc)})

    summary = {
        "status": "ok" if not errors else "error",
        "validated": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for r in results:
            print(f"OK  {r['file']}  id={r['id']} events={r['events']}")
        for e in errors:
            print(f"ERR {e['file']}  {e['error']}")

    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
