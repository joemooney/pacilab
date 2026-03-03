#!/usr/bin/env python3
"""Import/export scenario files to local custom store."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pacilab.scenario_lib import validate_scenario_obj

DEFAULT_STORE = Path("examples/custom_scenarios.json")
DEFAULT_DIR = Path("examples/scenarios")


def load_store(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        raise ValueError("store must have array field 'items'")
    return [validate_scenario_obj(i) for i in items]


def save_store(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"items": items}, indent=2) + "\n", encoding="utf-8")


def cmd_validate(in_dir: Path) -> dict:
    files = sorted(p for p in in_dir.glob("*.json") if p.is_file())
    for f in files:
        validate_scenario_obj(json.loads(f.read_text(encoding="utf-8")))
    return {"validated_files": len(files), "in_dir": str(in_dir)}


def cmd_import(in_dir: Path, store: Path, mode: str) -> dict:
    files = sorted(p for p in in_dir.glob("*.json") if p.is_file())
    imported = [validate_scenario_obj(json.loads(f.read_text(encoding="utf-8"))) for f in files]
    if mode == "replace":
        merged = imported
    else:
        current = load_store(store)
        by_id = {s["id"]: s for s in current}
        for s in imported:
            by_id[s["id"]] = s
        merged = sorted(by_id.values(), key=lambda x: x["id"])
    save_store(store, merged)
    return {"imported_files": len(files), "stored_total": len(merged), "mode": mode}


def cmd_export(store: Path, out_dir: Path) -> dict:
    items = load_store(store)
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in items:
        (out_dir / f"{s['id']}.json").write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
    return {"exported": len(items), "out_dir": str(out_dir)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Scenario sync tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_val = sub.add_parser("validate")
    p_val.add_argument("--in-dir", default=str(DEFAULT_DIR))

    p_imp = sub.add_parser("import")
    p_imp.add_argument("--in-dir", default=str(DEFAULT_DIR))
    p_imp.add_argument("--store", default=str(DEFAULT_STORE))
    p_imp.add_argument("--mode", choices=["merge", "replace"], default="merge")

    p_exp = sub.add_parser("export")
    p_exp.add_argument("--store", default=str(DEFAULT_STORE))
    p_exp.add_argument("--out-dir", default=str(DEFAULT_DIR))

    args = parser.parse_args()

    if args.cmd == "validate":
        out = cmd_validate(Path(args.in_dir))
    elif args.cmd == "import":
        out = cmd_import(Path(args.in_dir), Path(args.store), args.mode)
    else:
        out = cmd_export(Path(args.store), Path(args.out_dir))

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
