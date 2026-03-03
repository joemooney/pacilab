#!/usr/bin/env python3
"""Scenario validation and normalization for paciLab."""

from __future__ import annotations

import re
from typing import Any

SCENARIO_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
ALLOWED_TOP_KEYS = {
    "schema_version",
    "id",
    "name",
    "description",
    "default_rules_file",
    "stateful",
    "tags",
    "events",
    "topology",
}
ALLOWED_EVENT_KEYS = {
    "name",
    "packet",
    "expected_action",
    "delay_ms",
    "meta",
    "ingress_port",
    "expected_egress_port",
    "expected_switch_action",
    "inject_rmac_error",
}
ALLOWED_TOPOLOGY_KEYS = {"kind", "ports"}
ALLOWED_TOPOLOGY_PORT_KEYS = {"id", "name", "subnet", "mac"}


class ScenarioValidationError(ValueError):
    pass


def validate_scenario_obj(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ScenarioValidationError("scenario must be an object")

    schema_version = str(raw.get("schema_version", "v1")).strip().lower()
    if schema_version not in ("v1", "v2"):
        raise ScenarioValidationError("schema_version must be 'v1' or 'v2'")

    unknown_top = set(raw.keys()) - ALLOWED_TOP_KEYS
    if unknown_top:
        raise ScenarioValidationError(f"unknown top-level keys: {sorted(unknown_top)}")

    sid = str(raw.get("id", "")).strip()
    if not sid:
        raise ScenarioValidationError("id is required")
    if not SCENARIO_ID_RE.match(sid):
        raise ScenarioValidationError("id must match ^[A-Za-z0-9_.-]+$")

    name = str(raw.get("name", "")).strip()
    if not name:
        raise ScenarioValidationError("name is required")

    description = str(raw.get("description", ""))
    default_rules_file = raw.get("default_rules_file")
    if default_rules_file is not None:
        default_rules_file = str(default_rules_file).strip()
        if not default_rules_file:
            raise ScenarioValidationError("default_rules_file cannot be empty when provided")

    stateful = bool(raw.get("stateful", False))

    tags_raw = raw.get("tags", []) or []
    if not isinstance(tags_raw, list):
        raise ScenarioValidationError("tags must be an array")
    tags = []
    seen_tags = set()
    for i, t in enumerate(tags_raw):
        tag = str(t).strip()
        if not tag:
            raise ScenarioValidationError(f"tags[{i}] cannot be empty")
        if tag in seen_tags:
            raise ScenarioValidationError(f"tags[{i}] duplicates '{tag}'")
        seen_tags.add(tag)
        tags.append(tag)

    events_raw = raw.get("events")
    if not isinstance(events_raw, list) or not events_raw:
        raise ScenarioValidationError("events must be a non-empty array")

    events = []
    for i, ev in enumerate(events_raw):
        if not isinstance(ev, dict):
            raise ScenarioValidationError(f"events[{i}] must be an object")
        unknown_ev = set(ev.keys()) - ALLOWED_EVENT_KEYS
        if unknown_ev:
            raise ScenarioValidationError(f"events[{i}] unknown keys: {sorted(unknown_ev)}")

        ev_name = str(ev.get("name", "")).strip()
        if not ev_name:
            raise ScenarioValidationError(f"events[{i}].name is required")

        packet = ev.get("packet")
        if not isinstance(packet, dict) or not packet:
            raise ScenarioValidationError(f"events[{i}].packet must be a non-empty object")

        normalized_packet = {}
        for k, v in packet.items():
            if not isinstance(k, str) or not k.strip():
                raise ScenarioValidationError(f"events[{i}].packet contains invalid key")
            if not isinstance(v, (str, int, float, bool)):
                raise ScenarioValidationError(
                    f"events[{i}].packet['{k}'] must be string/integer/number/boolean"
                )
            normalized_packet[k.strip()] = v

        out_ev = {"name": ev_name, "packet": normalized_packet}

        expected_action = ev.get("expected_action")
        if expected_action is not None:
            ea = str(expected_action).strip().lower()
            if ea not in ("pass", "drop"):
                raise ScenarioValidationError(f"events[{i}].expected_action must be 'pass' or 'drop'")
            out_ev["expected_action"] = ea

        delay_ms = int(ev.get("delay_ms", 0))
        if delay_ms < 0:
            raise ScenarioValidationError(f"events[{i}].delay_ms must be >= 0")
        if delay_ms:
            out_ev["delay_ms"] = delay_ms

        meta = ev.get("meta")
        if meta is not None:
            if not isinstance(meta, dict):
                raise ScenarioValidationError(f"events[{i}].meta must be an object")
            out_ev["meta"] = meta

        ingress_port = ev.get("ingress_port")
        if ingress_port is not None:
            p = int(ingress_port)
            if p < 0:
                raise ScenarioValidationError(f"events[{i}].ingress_port must be >= 0")
            out_ev["ingress_port"] = p

        expected_egress_port = ev.get("expected_egress_port")
        if expected_egress_port is not None:
            p = int(expected_egress_port)
            if p < 0:
                raise ScenarioValidationError(f"events[{i}].expected_egress_port must be >= 0")
            out_ev["expected_egress_port"] = p

        expected_switch_action = ev.get("expected_switch_action")
        if expected_switch_action is not None:
            sa = str(expected_switch_action).strip().lower()
            if sa not in ("forward", "drop"):
                raise ScenarioValidationError(
                    f"events[{i}].expected_switch_action must be 'forward' or 'drop'"
                )
            out_ev["expected_switch_action"] = sa

        if bool(ev.get("inject_rmac_error", False)):
            out_ev["inject_rmac_error"] = True

        events.append(out_ev)

    topology = raw.get("topology")
    if topology is not None:
        if not isinstance(topology, dict):
            raise ScenarioValidationError("topology must be an object")
        unknown_topology = set(topology.keys()) - ALLOWED_TOPOLOGY_KEYS
        if unknown_topology:
            raise ScenarioValidationError(f"topology unknown keys: {sorted(unknown_topology)}")

        kind = str(topology.get("kind", "l3_switch_2port")).strip()
        if not kind:
            raise ScenarioValidationError("topology.kind cannot be empty")

        ports_raw = topology.get("ports")
        if not isinstance(ports_raw, list) or len(ports_raw) < 2:
            raise ScenarioValidationError("topology.ports must be an array of at least 2 ports")

        ports = []
        seen = set()
        for i, port in enumerate(ports_raw):
            if not isinstance(port, dict):
                raise ScenarioValidationError(f"topology.ports[{i}] must be an object")
            unknown_port = set(port.keys()) - ALLOWED_TOPOLOGY_PORT_KEYS
            if unknown_port:
                raise ScenarioValidationError(
                    f"topology.ports[{i}] unknown keys: {sorted(unknown_port)}"
                )
            pid = int(port.get("id", -1))
            if pid < 0:
                raise ScenarioValidationError(f"topology.ports[{i}].id must be >= 0")
            if pid in seen:
                raise ScenarioValidationError(f"topology.ports[{i}].id duplicates {pid}")
            seen.add(pid)

            subnet = str(port.get("subnet", "")).strip()
            mac = str(port.get("mac", "")).strip()
            if not subnet:
                raise ScenarioValidationError(f"topology.ports[{i}].subnet is required")
            if not mac:
                raise ScenarioValidationError(f"topology.ports[{i}].mac is required")

            ports.append(
                {
                    "id": pid,
                    "name": str(port.get("name", f"port{pid}")).strip() or f"port{pid}",
                    "subnet": subnet,
                    "mac": mac,
                }
            )

        topology = {"kind": kind, "ports": ports}

    out = {"id": sid, "name": name, "events": events}
    if schema_version != "v1":
        out["schema_version"] = schema_version
    if description:
        out["description"] = description
    if default_rules_file:
        out["default_rules_file"] = default_rules_file
    if stateful:
        out["stateful"] = True
    if tags:
        out["tags"] = tags
    if topology is not None:
        out["topology"] = topology
    return out
