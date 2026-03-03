#!/usr/bin/env python3
"""Engine integration for mock or external pacgate simulation."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


def packet_to_spec(packet: dict[str, Any]) -> str:
    parts = []
    for k, v in packet.items():
        if v is None:
            continue
        s = str(v).strip()
        if s:
            parts.append(f"{k}={s}")
    if not parts:
        raise ValueError("packet has no fields")
    return ",".join(parts)


def simulate_packet(
    packet: dict[str, Any],
    rules_file: str,
    mode: str,
    pacgate_bin: str,
    stateful: bool = False,
) -> dict[str, Any]:
    if mode == "mock":
        ethertype = str(packet.get("ethertype", "")).lower()
        dst_ip = str(packet.get("dst_ip", "")).strip()
        if ethertype == "0x0806":
            action = "pass"
        elif dst_ip.startswith("10.0.1."):
            action = "pass"
        else:
            action = "drop"
        return {
            "status": "ok",
            "action": action,
            "matched_rule": "mock_rule",
            "is_default": False,
            "fields": [],
        }

    resolved = shutil.which(pacgate_bin) if "/" not in pacgate_bin else pacgate_bin
    if not resolved:
        raise FileNotFoundError(
            f"pacgate binary not found: '{pacgate_bin}'. Use --mode mock or set --pacgate-bin"
        )

    cmd = [resolved, "simulate", rules_file, "--packet", packet_to_spec(packet), "--json"]
    if stateful:
        cmd.append("--stateful")
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)
