#!/usr/bin/env python3
"""Run 2-port RMAC/switch topology scenarios."""

from __future__ import annotations

import argparse
import ipaddress
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pacilab.engine import simulate_packet
from pacilab.scenario_lib import validate_scenario_obj


@dataclass
class PortCfg:
    id: int
    name: str
    subnet: ipaddress.IPv4Network
    mac: str


def in_subnet(ip_text: str | None, subnet: ipaddress.IPv4Network) -> bool:
    if not ip_text:
        return False
    try:
        return ipaddress.ip_address(ip_text) in subnet
    except ValueError:
        return False


def lookup_egress(ports: list[PortCfg], ingress: int, dst_ip: str | None) -> int | None:
    if not dst_ip:
        return None
    for p in ports:
        if p.id == ingress:
            continue
        if in_subnet(dst_ip, p.subnet):
            return p.id
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run topology scenario")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--mode", choices=["mock", "real"], default="mock")
    parser.add_argument("--pacgate-bin", default="pacgate")
    parser.add_argument("--output")
    args = parser.parse_args()

    raw = json.loads(Path(args.scenario).read_text(encoding="utf-8"))
    scenario = validate_scenario_obj(raw)

    topo = scenario.get("topology")
    if not isinstance(topo, dict):
        raise SystemExit("scenario.topology is required")

    ports = [
        PortCfg(
            id=int(p["id"]),
            name=str(p["name"]),
            subnet=ipaddress.ip_network(str(p["subnet"]), strict=False),
            mac=str(p["mac"]),
        )
        for p in topo["ports"]
    ]
    by_id = {p.id: p for p in ports}

    rules = scenario.get("default_rules_file", "rules/examples/allow_arp.yaml")
    stateful = bool(scenario.get("stateful", False))

    stats = {
        "total_events": 0,
        "rmac_error_count": 0,
        "rmac_dropped": 0,
        "switch_forwarded": 0,
        "switch_dropped": 0,
        "switch_drop_reasons": {
            "rmac_error": 0,
            "ingress_subnet_mismatch": 0,
            "pacgate_drop": 0,
            "no_route": 0,
        },
    }

    mismatches = 0
    results = []

    for i, ev in enumerate(scenario["events"]):
        stats["total_events"] += 1
        delay_ms = int(ev.get("delay_ms", 0))
        if i > 0 and delay_ms > 0:
            time.sleep(delay_ms / 1000.0)

        ingress = int(ev.get("ingress_port", 0))
        if ingress not in by_id:
            raise SystemExit(f"events[{i}].ingress_port {ingress} not in topology")

        packet = ev["packet"]
        src_ip = str(packet.get("src_ip", "")).strip() or None
        dst_ip = str(packet.get("dst_ip", "")).strip() or None
        ingress_cfg = by_id[ingress]

        pacgate = None
        switch_action = "drop"
        egress = None
        drop_reason = ""

        if bool(ev.get("inject_rmac_error", False)):
            stats["rmac_error_count"] += 1
            stats["rmac_dropped"] += 1
            stats["switch_dropped"] += 1
            stats["switch_drop_reasons"]["rmac_error"] += 1
            drop_reason = "rmac_error"
        elif src_ip and not in_subnet(src_ip, ingress_cfg.subnet):
            stats["rmac_dropped"] += 1
            stats["switch_dropped"] += 1
            stats["switch_drop_reasons"]["ingress_subnet_mismatch"] += 1
            drop_reason = "ingress_subnet_mismatch"
        else:
            pacgate = simulate_packet(packet, rules, args.mode, args.pacgate_bin, stateful)
            if pacgate.get("action") == "drop":
                stats["switch_dropped"] += 1
                stats["switch_drop_reasons"]["pacgate_drop"] += 1
                drop_reason = "pacgate_drop"
            else:
                egress = lookup_egress(ports, ingress, dst_ip)
                if egress is None:
                    stats["switch_dropped"] += 1
                    stats["switch_drop_reasons"]["no_route"] += 1
                    drop_reason = "no_route"
                else:
                    switch_action = "forward"
                    stats["switch_forwarded"] += 1

        expected_action = ev.get("expected_action")
        expected_switch = ev.get("expected_switch_action")
        expected_egress = ev.get("expected_egress_port")

        action_ok = True
        if expected_action is not None:
            actual = pacgate.get("action") if pacgate else "drop"
            action_ok = expected_action == actual

        switch_ok = True
        if expected_switch is not None:
            switch_ok = expected_switch == switch_action

        egress_ok = True
        if expected_egress is not None:
            egress_ok = int(expected_egress) == int(egress if egress is not None else -1)

        event_ok = action_ok and switch_ok and egress_ok
        if not event_ok:
            mismatches += 1

        results.append({
            "event_index": i,
            "event_name": ev.get("name", f"event_{i+1}"),
            "ingress_port": ingress,
            "switch_action": switch_action,
            "egress_port": egress,
            "drop_reason": drop_reason,
            "pacgate": pacgate,
            "event_ok": event_ok,
        })

    out = {
        "scenario_id": scenario["id"],
        "mode": args.mode,
        "mismatch_count": mismatches,
        "stats": stats,
        "results": results,
    }

    text = json.dumps(out, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")

    raise SystemExit(0 if mismatches == 0 else 1)


if __name__ == "__main__":
    main()
